#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>  // Đảm bảo sử dụng đúng thư viện ESP8266HTTPClient
#include <DHT.h>
#define DHTPIN 5
#define DHTTYPE    DHT22
//Change to your wifi name and password here.
const char* ssid = "Tai";
const char* password = "tranmanhtai";

DHT dht(DHTPIN, DHTTYPE);

float t = 0.0;
float h = 0.0;
unsigned long previousMillis = 0;
const long interval = 10000;
//Change to your computer IP address and server port here.
const char* serverUrl = "http://192.168.196.67:5001";

void setup() {
  Serial.begin(115200);
  dht.begin();
  WiFi.begin(ssid, password);
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  
  Serial.println("Connected to WiFi");
}

void loop() {
  unsigned long currentMillis = millis();
  if (currentMillis - previousMillis >= interval) {
    // save the last time you updated the DHT values
    previousMillis = currentMillis;
    // Read temperature as Celsius (the default)
    float newT = dht.readTemperature();
    // Read temperature as Fahrenheit (isFahrenheit = true)
    //float newT = dht.readTemperature(true);
    // if temperature read failed, don't change t value
    if (isnan(newT)) {
      Serial.println("Failed to read from DHT sensor!");
    }
    else {
      t = newT;
      Serial.println(t);
    }
    // Read Humidity
    float newH = dht.readHumidity();
    // if humidity read failed, don't change h value 
    if (isnan(newH)) {
      Serial.println("Failed to read from DHT sensor!");
    }
    else {
      h = newH;
      Serial.println(h);
    }
  }
  String tStr = String(t, 3);  // 3 là số chữ số thập phân cần giữ lại
  String hStr = String(h, 3);
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;  // Đảm bảo sử dụng đúng tên biến và lớp HTTPClient
    WiFiClient client;  // Khai báo WiFiClient để kết nối HTTP

    // Tạo URL với thông tin từ cảm biến (temperature, humidity)
    String url = serverUrl;
    url += "/";  // Tạo URL theo cú pháp của bạn
    url += tStr;  // temperature
    url += "/";
    url += hStr;  // humidity
    
    http.begin(client, url);  // Bắt đầu kết nối với URL qua WiFiClient

    int httpResponseCode = http.GET();  // Gửi yêu cầu GET
    
    // Lấy HTTP response và in kết quả
    if (httpResponseCode == 200) {
      String response = http.getString();
      Serial.println("Server response:");
      Serial.println(response);
    } else {
      Serial.print("HTTP error code: ");
      Serial.println(httpResponseCode);
    }
    
    http.end();  // Kết thúc kết nối HTTP
  } else {
    Serial.println("WiFi disconnected");
  }
  
  delay(2000);  // Gửi yêu cầu sau mỗi 2 giây
}