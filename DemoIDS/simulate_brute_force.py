# simulate_brute_force.py
# Basit script: demo sunucuya ardışık POST istekleri göndererek brute-force ve ddos benzeri örnekleri simüle eder.
# requests paketini kullanır; sunucu localde çalışıyor olmalı (http://127.0.0.1:5000/submit).

import requests
import time

URL = "http://127.0.0.1:5000/submit"

def send_attack():
    """
    Brute-force benzeri örnek gönderir:
    - duration: 2.0
    - düşük paket hızı
    - failed_logins yüksek (6)
    Bu payload demo dataset'te BRUTE_FORCE tarzı örneklerle uyumludur.
    """
    payload = {
        "duration": 2.0,
        "src_bytes": 10,
        "dst_bytes": 5,
        "pkt_rate": 0.5,
        "failed_logins": 6,
        "note":"simulated brute"
    }
    r = requests.post(URL, json=payload)
    print("status", r.status_code, r.json())

def send_ddos():
    """
    DDoS benzeri örnek gönderir:
    - yüksek paket hızı (1200)
    - yüksek src_bytes
    Bu payload demo dataset'teki DDoS örnekleri ile uyumlu.
    """
    payload = {
        "duration": 1.0,
        "src_bytes": 5000,
        "dst_bytes": 10,
        "pkt_rate": 1200,
        "failed_logins": 0,
        "note":"simulated ddos"
    }
    r = requests.post(URL, json=payload)
    print("status", r.status_code, r.json())

if __name__ == "__main__":
    # 5 tane ardışık brute örneği gönder, arada kısa bekleme (throttle)
    for _ in range(5):
        send_attack()
        time.sleep(0.3)
    # bir tane ddos örneği gönder
    send_ddos()
