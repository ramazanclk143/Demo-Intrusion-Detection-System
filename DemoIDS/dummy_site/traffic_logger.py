# dummy_site/traffic_logger.py
# Gelen istekleri CSV formatında append eden basit logger.
# Her satır: timestamp, duration, src_bytes, dst_bytes, pkt_rate, failed_logins, client_ip, note

import csv
import os
from datetime import datetime

# LOG_FILE: bu dosyanın bulunduğu klasör içinde logs/traffic_log.csv
LOG_FILE = os.path.join(os.path.dirname(__file__), 'logs', 'traffic_log.csv')
# logs klasörü yoksa oluştur
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

# CSV başlık satırı (ilk oluşturulduğunda yazılacak)
HEADER = ['timestamp','duration','src_bytes','dst_bytes','pkt_rate','failed_logins','client_ip','note']

def append_row(row_dict):
    """
    append_row:
    - row_dict içinde beklenen anahtarlar kullanılarak CSV'ye bir satır ekler.
    - Eğer dosya yeni oluşturuluyorsa, önce HEADER yazılır.
    - timestamp otomatik UTC zaman damgası ile doldurulur.
    """
    first = not os.path.exists(LOG_FILE)
    with open(LOG_FILE, 'a', newline='') as f:
        writer = csv.writer(f)
        if first:
            # Eğer dosya yoksa başlık yaz
            writer.writerow(HEADER)
        # Yazılacak satırı sırayla oluştur
        writer.writerow([
            datetime.utcnow().isoformat(),
            row_dict.get('duration'),
            row_dict.get('src_bytes'),
            row_dict.get('dst_bytes'),
            row_dict.get('pkt_rate'),
            row_dict.get('failed_logins'),
            row_dict.get('client_ip','-'),
            row_dict.get('note','')
        ])
