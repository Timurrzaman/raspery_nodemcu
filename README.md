# 🚗 Akıllı Otopark Sistemi (Smart Parking IoT System)

Bu proje, otopark doluluk durumunu gerçek zamanlı olarak takip etmeyi sağlayan, uçtan uca (End-to-End) tasarlanmış bir **Nesnelerin İnterneti (IoT)** çözümüdür. 

Sistem; donanım sensörleri, yerel bir ağ geçidi (Gateway), merkezi bir API sunucusu ve modern bir mobil uygulamadan oluşan 4 katmanlı bir mimariye sahiptir.

## 🏗️ Sistem Mimarisi ve Teknolojiler

Proje, görevlerin donanımlar ve yazılımlar arasında paylaştırıldığı hibrit bir yapı kullanır:

1. **Donanım Beyni (Raspberry Pi - Python):** Otoparktaki HC-SR04 ultrasonik sensörleri okur. İnternete bağlanmakla zaman kaybetmez; doluluk durumunu (örn: `10110`) hesaplayıp USB (Seri Port) üzerinden köprü cihaza aktarır.
2. **Wi-Fi Köprüsü (NodeMCU ESP8266 - C++):** Raspberry Pi'den gelen saf veriyi seri porttan dinler. Gelen veriyi yakaladığı an üzerindeki Wi-Fi çipi aracılığıyla Django REST API'ye POST eder.
3. **Merkezi Sunucu (Django - Python):** NodeMCU'dan gelen verileri karşılar, güvenlik kontrollerini yapar (API Key) ve SQLite veritabanına kaydeder.
4. **Mobil Arayüz (Flutter - Dart):** Kullanıcıların otopark durumunu anlık olarak görebilmesi için tasarlanmış, karanlık tema (Dark Mode) destekli, modern iOS/Android uygulaması.

## ⚙️ Nasıl Çalışır?

* Raspberry Pi, 5 farklı park noktasını tarar. Araç sensöre 50 cm'den yakınsa o noktayı **"DOLU" (1)**, uzaksa **"BOŞ" (0)** olarak işaretler.
* Sıkıştırılmış veri paketi oluşturulur (Örn: `11001` -> 1., 2. ve 5. park yerleri dolu).
* Paket, NodeMCU aracılığıyla saniyeler içinde sunucuya iletilir.
* Sürücü, mobil uygulamayı açtığında isim ve plakasıyla giriş yapar (bilgiler `SharedPreferences` ile cihazda tutulur) ve direkt olarak güncel otopark haritasıyla karşılaşır.

## 🚀 Kurulum ve Çalıştırma

### 1. Sunucu (Backend) Kurulumu
Projenin API klasöründe terminali açın:
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
