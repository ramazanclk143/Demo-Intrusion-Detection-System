# train/generate_mini_dataset.py
# Sentetik (demo) mini dataset üreten script.
# Amaç: her sınıf için belirgin özellik örüntüleri oluşturarak demo modellerin daha stabil öğrenmesini sağlamak.

import numpy as np
import pandas as pd

"""
Daha net ayrım yapan sentetik mini veri seti.
"""

# Tekrar üretilebilirlik için seed sabitlenir
np.random.seed(42)

def safe_normal(loc, scale, size=1, floor=0.0):
    """
    Normal dağılımdan değer çek, negatif olmasını engelle (clip ile).
    - loc: ortalama
    - scale: std
    - floor: minimum değer (genelde 0.0)
    """
    vals = np.random.normal(loc, scale, size)
    return np.clip(vals, floor, None)

def make_row(label):

    # features: duration, src_bytes, dst_bytes, pkt_rate, failed_logins
    if label == 'BENIGN':
        # BENIGN: düşük paket hızı, makul kaynak/dest byte, failed_logins=0
        duration = np.abs(np.random.exponential(scale=0.5))
        pkt_rate = safe_normal(loc=2.0, scale=1.0, size=1)[0]
        src_bytes = np.random.randint(20, 300)
        dst_bytes = np.random.randint(10, 200)
        failed_logins = 0
        return [float(duration), float(src_bytes), float(dst_bytes), float(pkt_rate), float(failed_logins), label]

    if label == 'BRUTE_FORCE':
        # BRUTE_FORCE: uzun duration, düşük pkt_rate, çok sayıda failed_logins
        duration = np.abs(np.random.exponential(scale=1.8))
        pkt_rate = safe_normal(loc=1.0, scale=0.5, size=1)[0]
        src_bytes = np.random.randint(10, 80)
        dst_bytes = np.random.randint(5, 60)
        failed_logins = np.random.randint(4, 12)
        return [float(duration), float(src_bytes), float(dst_bytes), float(pkt_rate), float(failed_logins), label]

    if label == 'DDoS':
        # DDoS: çok yüksek pkt_rate ve yüksek src_bytes
        duration = np.abs(np.random.exponential(scale=0.8))
        pkt_rate = safe_normal(loc=1200.0, scale=300.0, size=1)[0]
        src_bytes = np.random.randint(2000, 20000)
        dst_bytes = np.random.randint(0, 200)
        failed_logins = 0
        return [float(duration), float(src_bytes), float(dst_bytes), float(pkt_rate), float(failed_logins), label]

    if label == 'PORTSCAN':
        # PORTSCAN: çok kısa duration, yüksek fakat BRUTE/DDOS'tan farklı bir pkt_rate aralığı
        duration = np.abs(np.random.exponential(scale=0.05))
        pkt_rate = safe_normal(loc=200.0, scale=50.0, size=1)[0]
        src_bytes = np.random.randint(1, 40)
        dst_bytes = np.random.randint(1, 40)
        failed_logins = 0
        return [float(duration), float(src_bytes), float(dst_bytes), float(pkt_rate), float(failed_logins), label]

    # BOT veya diğer sınıflar: orta seviyede özellikler
    duration = np.abs(np.random.exponential(scale=0.8))
    pkt_rate = safe_normal(loc=12.0, scale=5.0, size=1)[0]
    src_bytes = np.random.randint(50, 800)
    dst_bytes = np.random.randint(20, 600)
    failed_logins = np.random.randint(0, 2)
    return [float(duration), float(src_bytes), float(dst_bytes), float(pkt_rate), float(failed_logins), label]


# Her sınıftan kaç örnek üretileceğini belirle
SAMPLES_PER_CLASS = 300
labels = ['BENIGN', 'BRUTE_FORCE', 'DDoS', 'PORTSCAN', 'BOT']
rows = []

# Her sınıf için örnekleri üret ve rows listesine ekle
for lab in labels:
    for _ in range(SAMPLES_PER_CLASS):
        rows.append(make_row(lab))

# DataFrame oluştur ve CSV'ye yaz
df = pd.DataFrame(rows, columns=['duration','src_bytes','dst_bytes','pkt_rate','failed_logins','label'])

OUT_PATH = 'mini_dataset.csv'
df.to_csv(OUT_PATH, index=False)

# Bilgilendirici çıktı: toplam satır sayısı, sınıf dağılımı ve ilk birkaç satır
print(f"✅ mini_dataset.csv oluşturuldu: {OUT_PATH} — toplam satır: {len(df)}")
print("Sınıf dağılımı (label : count):")
print(df['label'].value_counts())
print("\nÖzellik özetleri (ilk 5 satır):")
print(df.head().to_string(index=False))
