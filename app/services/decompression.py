import os
import pickle
import pandas as pd
import numpy as np
from sklearn.decomposition import DictionaryLearning
from sklearn.linear_model import OrthogonalMatchingPursuit
from sklearn.metrics import mean_squared_error
import sqlite3
from sklearn.preprocessing import StandardScaler
from scipy.signal import detrend
from scipy.ndimage import gaussian_filter

class TimeSeriesCompressor:
    def __init__(self, csv_file_path, segment_length=5000, n_atoms=50, n_nonzero_coefs=5, db_path='iot_data.db', dict_path='dictionary.pkl'):
        self.csv_file_path = csv_file_path
        self.segment_length = segment_length
        self.n_atoms = n_atoms
        self.n_nonzero_coefs = n_nonzero_coefs
        self.db_path = db_path
        self.dict_path = dict_path
        self.time_series_data = None
        self.dictionary = None
        self.sparse_codes = None
        self.compressed_data = None

    def load_data(self):
        data = pd.read_csv(self.csv_file_path)      
        temperature_data = data['T2M'].dropna().values
        humidity_data = data['QV2M'].dropna().values

        if len(temperature_data) != len(humidity_data):
            raise ValueError("Temperature and humidity data lengths do not match.")

        self.time_series_data = np.vstack((temperature_data, humidity_data))

    def preprocess_data(self):        
        scaler = StandardScaler()
        self.time_series_data = scaler.fit_transform(self.time_series_data.T).T
        self.time_series_data = np.apply_along_axis(detrend, axis=1, arr=self.time_series_data)
        self.time_series_data = np.apply_along_axis(lambda x: gaussian_filter(x, sigma=2), axis=1, arr=self.time_series_data)

    def segment_data(self, overlap=5):
        segments = []
        for i in range(self.time_series_data.shape[0]):
            for j in range(0, self.time_series_data.shape[1] - self.segment_length + 1, self.segment_length - overlap):
                segments.append(self.time_series_data[i, j:j + self.segment_length])
        return np.array(segments)

    def load_or_learn_dictionary(self, segments):
        if os.path.exists(self.dict_path):
            with open(self.dict_path, 'rb') as f:
                self.dictionary = pickle.load(f)
            print("Dictionary loaded from dictionary.pkl")
        else:
            if len(segments.shape) == 1:
                segments = segments.reshape(-1, 1)
            dict_learn = DictionaryLearning(
                n_components=self.n_atoms,
                fit_algorithm='lars',
                transform_algorithm='threshold',
                tol=1e-10,
                max_iter=2000
            )
            self.dictionary = dict_learn.fit(segments).components_
            with open(self.dict_path, 'wb') as f:
                pickle.dump(self.dictionary, f)

    def perform_sparse_coding(self, segments):
        omp = OrthogonalMatchingPursuit(n_nonzero_coefs=self.n_nonzero_coefs)
        sparse_codes = []
        for segment in segments:
            sparse_code = omp.fit(self.dictionary.T, segment).coef_
            sparse_codes.append(sparse_code)
        self.sparse_codes = np.array(sparse_codes)

    def compress(self, threshold=0.5):
        corr_matrix = self.compute_correlation_matrix()
        compressed_data = []

        for i in range(self.time_series_data.shape[0]):
            max_corr = np.max(corr_matrix[i][i+1:]) if i + 1 < corr_matrix.shape[0] else 0

            if max_corr < threshold:
                reconstructed_segment = np.sum(self.sparse_codes[i][:, np.newaxis] * self.dictionary, axis=0)
                compressed_data.append(reconstructed_segment)
            else:
                correlated_series_idx = np.argmax(corr_matrix[i][i+1:]) + (i+1)
                scale_factor = (
                    np.dot(self.time_series_data[i], self.time_series_data[correlated_series_idx])
                    / np.dot(self.time_series_data[correlated_series_idx], self.time_series_data[correlated_series_idx])
                )
                compressed_data.append(scale_factor * self.time_series_data[correlated_series_idx])
    
        self.compressed_data = np.array(compressed_data)
        return self.compressed_data
    

    def compute_correlation_matrix(self):
        return np.corrcoef(self.time_series_data)

    def decompress(self):
        decompressed_segments = []
        for sparse_code in self.sparse_codes:
            reconstructed_segment = np.dot(self.dictionary.T, sparse_code)
            decompressed_segments.append(reconstructed_segment)
        return np.array(decompressed_segments)

    def reassemble_segments(self, segments, num_series, num_points):
        reassembled_data = np.zeros((num_series, num_points))
        seg_idx = 0
        for i in range(num_series):
            for j in range(0, num_points, self.segment_length):
                if seg_idx < len(segments):
                    segment = segments[seg_idx]
                    expected_length = min(self.segment_length, reassembled_data.shape[1] - j)
                    reassembled_data[i, j:j + expected_length] = segment[:expected_length]
                    seg_idx += 1
        return reassembled_data

    def evaluate_compression(self, original_data, decompressed_segments):
        num_series, num_points = original_data.shape
        decompressed_data = self.reassemble_segments(decompressed_segments, num_series, num_points)
        mse = mean_squared_error(original_data.flatten(), decompressed_data.flatten())
        compression_ratio = original_data.size / self.sparse_codes.size
        return mse, compression_ratio

    def store_results(self, mse, compression_ratio):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        c.execute('''CREATE TABLE IF NOT EXISTS compressed_data
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      original BLOB,
                      compressed BLOB,
                      mse REAL,
                      compression_ratio REAL)''')

        original_data_blob = self.time_series_data.tobytes()
        compressed_data_blob = self.sparse_codes.tobytes()

        c.execute('''INSERT INTO compressed_data (original, compressed, mse, compression_ratio)
                     VALUES (?, ?, ?, ?)''',
                  (original_data_blob, compressed_data_blob, mse, compression_ratio))

        conn.commit()
        conn.close()

    def run_compression(self):
        # print("Loading data...")
        self.load_data()
        
        # print("Preprocessing data...")
        self.preprocess_data()
        
        # print("Segmenting data...")
        segments = self.segment_data()
        #print(f"Segment length during segmentation: {self.segment_length}")
        # print(f"Segment shape after segmentation: {segments.shape}")
        
        # print("Learning dictionary...")
        self.load_or_learn_dictionary(segments)
        # print(f"Dictionary shape: {self.dictionary.shape}")  # Expected: (n_atoms, segment_length)
        
        # print("Performing sparse coding...")
        self.perform_sparse_coding(segments)
        # print(f"Sparse codes shape: {self.sparse_codes.shape}")  # Expected: (num_segments, n_atoms)

        # print("Compressing data...")
        self.compress()
        # print("Compressed data shape:", self.compressed_data.shape)

        
        # print("Decompressing data...")
        decompressed_segments = self.decompress()
        # print("Decompression complete.")

        # print("Reassembling segments...")
        num_series, num_points = self.time_series_data.shape
        decompressed_data = self.reassemble_segments(decompressed_segments, num_series, num_points)
        
        # print("Evaluating compression...")
        mse, compression_ratio = self.evaluate_compression(self.time_series_data, decompressed_segments)
        
        print(f"Compression Ratio: {compression_ratio}")
        print(f"Mean Squared Error: {mse}")
        
        # print("Storing results...")
        self.store_results(mse, compression_ratio)
        
        return mse, compression_ratio