/*
  Akıllı Otopark - NodeMCU (Kurye) Kodu
  Görevi: USB'den (Raspberry Pi'den) gelen veriyi dinler ve Wi-Fi üzerinden Django API'ye gönderir.
*/

#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <WiFiClient.h>

// ─── 1. KENDİ AĞ VE SUNUCU AYARLARINI BURAYA GİR ───
const char* ssid = "WIFI_ADINIZI_YAZIN";        // Otoparktaki veya evdeki Wi-Fi adı
const char* password = "WIFI_SIFRENIZI_YAZIN";  // Wi-Fi şifresi

// Django sunucusunun (bilgisayarının) yerel IP adresi. (Örn: 192.168.1.15)
// Not: "127.0.0.1" veya "localhost" YAZMA! NodeMCU dışarıdan bağlandığı için IPv4 adresini yazmalısın.
const char* api_url = "http://192.168.1.XX:8000/api/update/"; 
const char* api_key = "super-secret-key-123";

void setup() {
  // Raspberry Pi (Depo Şefi) ile aynı haberleşme hızında olmalı
  Serial.begin(9600);
  
  // Wi-Fi'ye Bağlanma İşlemi
  WiFi.begin(ssid, password);
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
  }
  
  // NodeMCU Wi-Fi'ye başarıyla bağlandığında üzerindeki mavi LED'i yak
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, LOW); 
}

void loop() {
  // ─── 2. RASPBERRY PI'DEN GELEN VERİYİ DİNLE ───
  // Eğer USB (Seri Port) üzerinden bir veri geliyorsa...
  if (Serial.available() > 0) {
    
    // Veriyi satır sonuna ('\n') kadar oku
    String payload = Serial.readStringUntil('\n');
    payload.trim(); // Boşlukları ve görünmez karakterleri temizle (Sadece "10110" kalsın)

    // ─── 3. VERİYİ DJANGO API'YE (İNTERNETE) GÖNDER ───
    // Eğer gelen veri boş değilse ve Wi-Fi hala bağlıysa işlemi başlat
    if (payload.length() > 0 && WiFi.status() == WL_CONNECTED) {
      WiFiClient client;
      HTTPClient http;

      // API Adresine Bağlan
      http.begin(client, api_url);
      
      // Güvenlik ve Veri Tipi Başlıklarını Ekle
      http.addHeader("Content-Type", "application/json");
      http.addHeader("X-API-Key", api_key);

      // JSON paketini manuel olarak oluştur (Örn: {"payload": "10110"})
      String jsonBody = "{\"payload\": \"" + payload + "\"}";
      
      // Paketi POST metodu ile gönder
      int httpResponseCode = http.POST(jsonBody);
      
      // Bağlantıyı kapat
      http.end();
      
      // Bir sonraki veri için seri port önbelleğini temizle
      Serial.flush();
    }
  }
}