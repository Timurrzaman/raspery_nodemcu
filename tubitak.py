
import time
import random
import logging

# ──────────────────────────────────────────
# AYARLAR — Buradan yapılandırın
# ──────────────────────────────────────────
MODE          = "SIMULATION"   # "SIMULATION" veya "HARDWARE"
SENSOR_COUNT  = 5
THRESHOLD_CM  = 50             # Bu mesafeden kısa → dolu
READ_INTERVAL = 5              # Saniye cinsinden okuma aralığı
NODEMCU_PORT  = "/dev/ttyUSB0" # NodeMCU'nun bağlandığı USB portu (Windows'ta COM3 vb. olabilir)
NODEMCU_BAUD  = 9600

# HC-SR04 sensörlerinin GPIO pin çiftleri (HARDWARE modunda kullanılır)
SENSOR_PINS = {
    1: (17, 27),
    2: (22, 23),
    3: (24, 25),
    4: (5,  6),
    5: (13, 19),
}

# ──────────────────────────────────────────
# LOGLAMA
# ──────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger(__name__)

# ──────────────────────────────────────────
# DONANIM BAŞLATMA
# ──────────────────────────────────────────
gpio_available  = False
serial_conn     = None

if MODE == "HARDWARE":
    # GPIO Ayarları
    try:
        import RPi.GPIO as GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        for sensor_id, (trig, echo) in SENSOR_PINS.items():
            GPIO.setup(trig, GPIO.OUT)
            GPIO.setup(echo, GPIO.IN)
            GPIO.output(trig, False)
        time.sleep(0.5)
        gpio_available = True
        log.info("GPIO başarıyla yapılandırıldı.")
    except Exception as e:
        log.warning(f"GPIO başlatılamadı ({e}). Simülasyon moduna geçiliyor.")
        MODE = "SIMULATION"

    # NodeMCU Seri Port Bağlantısı
    if gpio_available:
        try:
            import serial
            serial_conn = serial.Serial(NODEMCU_PORT, baudrate=NODEMCU_BAUD, timeout=2)
            log.info(f"NodeMCU ile USB bağlantısı açıldı: {NODEMCU_PORT}")
        except Exception as e:
            log.warning(f"NodeMCU USB portu açılamadı ({e}). Sadece ekrana yazdırılacak.")

# ──────────────────────────────────────────
# SENSÖR OKUMA FONKSİYONLARI
# ──────────────────────────────────────────
def read_hardware_sensor(sensor_id: int) -> float:
    trig, echo = SENSOR_PINS[sensor_id]
    GPIO.output(trig, True)
    time.sleep(0.00001)
    GPIO.output(trig, False)

    timeout = time.time() + 0.04
    pulse_start = time.time()
    while GPIO.input(echo) == 0:
        pulse_start = time.time()
        if pulse_start > timeout: return 999.0

    timeout = time.time() + 0.04
    pulse_end = time.time()
    while GPIO.input(echo) == 1:
        pulse_end = time.time()
        if pulse_end > timeout: return 999.0

    return round(((pulse_end - pulse_start) * 34300) / 2, 1)

def read_simulated_sensor(sensor_id: int) -> float:
    is_parked = random.choices([True, False], weights=[40, 60])[0]
    return random.uniform(20, 45) if is_parked else random.uniform(80, 300)

def read_all_sensors() -> str:
    """Tüm sensörleri okur ve doğrudan '10110' formatında string döner."""
    payload = ""
    for i in range(1, SENSOR_COUNT + 1):
        distance = read_hardware_sensor(i) if MODE == "HARDWARE" else read_simulated_sensor(i)
        is_occupied = distance < THRESHOLD_CM
        payload += "1" if is_occupied else "0"
        
        status = "DOLU" if is_occupied else "BOŞ "
        log.info(f"  Sensör {i}: {distance:6.1f} cm → {status}")
        
    return payload

# ──────────────────────────────────────────
# İLETİŞİM FONKSİYONU (NodeMCU'ya Gönderim)
# ──────────────────────────────────────────
def send_to_nodemcu(payload: str):
    """Veriyi saf haliyle USB üzerinden NodeMCU'ya iletir."""
    data_to_send = f"{payload}\n" # NodeMCU'nun verinin bittiğini anlaması için \n (Enter) ekliyoruz
    
    if serial_conn is not None:
        try:
            serial_conn.write(data_to_send.encode("utf-8"))
            log.info(f"[USB -> NodeMCU] Paket Teslim Edildi: {payload}")
        except Exception as e:
            log.error(f"[USB HATA] Veri gönderilemedi: {e}")
    else:
        log.info(f"[SİMÜLASYON -> NodeMCU] Gönderilecek Paket: {payload}")

# ──────────────────────────────────────────
# ANA DÖNGÜ
# ──────────────────────────────────────────
def main():
    log.info("=" * 50)
    log.info(f"Raspberry Pi (Depo Şefi) Başlatıldı — MOD: {MODE}")
    log.info("=" * 50)

    try:
        while True:
            log.info(f"--- Yeni Tarama ---")
            payload = read_all_sensors()
            send_to_nodemcu(payload)
            time.sleep(READ_INTERVAL)

    except KeyboardInterrupt:
        log.info("Kullanıcı tarafından durduruldu.")
    finally:
        if gpio_available:
            GPIO.cleanup()
        if serial_conn and serial_conn.is_open:
            serial_conn.close()

if __name__ == "__main__":
    main()