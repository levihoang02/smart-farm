import os
import pickle
import pandas as pd
import numpy as np
from sklearn.decomposition import DictionaryLearning
from sklearn.linear_model import OrthogonalMatchingPursuit
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import StandardScaler
from scipy.signal import detrend
from scipy.ndimage import gaussian_filter
from datetime import datetime
import mysql.connector

class TimeSeriesCompressor:
    def __init__(self, date, segment_length=8000, n_atoms=5, n_nonzero_coefs=5, dict_path='dictionary.pkl'):
        self.segment_length = segment_length
        self.date = date
        self.n_atoms = n_atoms
        self.n_nonzero_coefs = n_nonzero_coefs
        self.dict_path = dict_path
        self.dictionary = None
        self.sparse_codes = None
        self.compressed_data = None
        self.scaler = None
        self.mse = None
        self.compression_ratio = None
        self.date_time = None
        self.num_series = None
        self.num_points = None
        self.sparse_codes_shape = None
        self.compressed_shape = None

    def load_data(self):
        try: 
            conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='312002VH',
            database='iot_data',
            port=3310
        )
            cursor = conn.cursor()
            
            # Get all necessary data including shape information
            cursor.execute('''
                SELECT compressed, scaler, sparse_codes, num_series, num_points, 
                    sparse_codes_shape, compressed_shape, mse, compression_ratio,
                    n_atoms, n_nonzero_coefs, segment_length, date_time 
                FROM compressed_data WHERE date_time LIKE %s
            ''', (f'%{self.date}%',))
            result = cursor.fetchone()
            
            if not result:
                raise ValueError(f"No data found for {self.date}")
            
            while cursor.fetchone() is not None:
                pass
            # Debug prints
            print(f"Compressed data blob size: {len(result[0])}")
            print(f"Target shape: {eval(result[6])}")
            
            # Convert shape strings to tuples
            self.sparse_codes_shape = eval(result[5])
            self.compressed_shape = eval(result[6])
            
            # Convert BLOBs to numpy arrays with proper shapes
            raw_compressed = np.frombuffer(result[0], dtype=np.float64)
            print(f"Raw compressed array size: {raw_compressed.size}")
            print(f"Expected size for shape {self.compressed_shape}: {np.prod(self.compressed_shape)}")
            
            self.compressed_data = raw_compressed.reshape(self.compressed_shape)
            self.scaler = pickle.loads(result[1])
            self.sparse_codes = np.frombuffer(result[2], dtype=np.float64).reshape(self.sparse_codes_shape)
            
            # Store other metadata
            self.num_series = result[3]
            self.num_points = result[4]
            self.mse = result[7]
            self.compression_ratio = result[8]
            self.n_atoms = result[9]
            self.n_nonzero_coefs = result[10]
            self.segment_length = result[11]
            self.date_time = result[12]
            
        finally:
            if cursor: 
                cursor.close()
            if conn:
                conn.close()

    def load_dictionary(self):
        if os.path.exists(self.dict_path):
            with open(self.dict_path, 'rb') as f:
                self.dictionary = pickle.load(f)
            print("Dictionary loaded from dictionary.pkl")
        else:
            print("Dictionary not found. Please train the dictionary first.")
    

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
    
    def inverse_transform_data(self, data):
        return self.scaler.inverse_transform(data.T).T
        

    def run_compression(self):
        # print("Loading data...")
        self.load_data()
        
        # print("Learning dictionary...")
        self.load_dictionary()
        # print(f"Dictionary shape: {self.dictionary.shape}")  # Expected: (n_atoms, segment_length)
    
        decompressed_segments = self.decompress()

        decompressed_data = self.reassemble_segments(decompressed_segments, self.num_series, self.num_points)
        
        print("Decompressed data:")
        print(decompressed_data)
        print("Inverse transformed data:")
        result = self.inverse_transform_data(decompressed_data)
        print(result)
        
        return result, self.date_time
        

if __name__ == "__main__":
    decompressor = TimeSeriesCompressor(date='2024-12-12')
    decompressor.run_compression()