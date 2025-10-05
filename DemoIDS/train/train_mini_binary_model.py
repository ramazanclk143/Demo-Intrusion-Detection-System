# train/train_mini_binary_model.py
# Binary (BENIGN vs ATTACK) model eğitme script'i.
# - mini_dataset.csv okur
# - binary label oluşturur (BENIGN=0, diğerleri=1)
# - scaler uygular, MLPClassifier ile eğitir
# - test set üzerinde classification_report ve confusion_matrix yazdırır
# - model ve scaler'ı models/ altına kaydeder (joblib)

import os, joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import classification_report, confusion_matrix

# Proje kökünü ve modellerin kaydedileceği klasörü hesapla
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "models")
os.makedirs(MODEL_DIR, exist_ok=True)

# Veri yolunu oluştur ve kontrol et
DATA_PATH = os.path.join(BASE_DIR, "mini_dataset.csv")
if not os.path.exists(DATA_PATH):
    raise FileNotFoundError(f"mini_dataset.csv bulunamadı: {DATA_PATH}")

# CSV'yi oku
df = pd.read_csv(DATA_PATH)

# Binary hedef sütunu oluştur: BENIGN -> 0, diğer tüm etiketler -> 1 (ATTACK)
df['binary'] = df['label'].apply(lambda x: 0 if x == 'BENIGN' else 1)

# Özellik kolonları sıralaması (model eğitirken aynı sırayı kullanmak önemli)
features = ['duration','src_bytes','dst_bytes','pkt_rate','failed_logins']
X, y = df[features].values, df['binary'].values

# Train/test bölme (stratify ile sınıf oranları korunur)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# StandardScaler ile öznitelikleri normalize et
scaler = StandardScaler().fit(X_train)
X_train_s, X_test_s = scaler.transform(X_train), scaler.transform(X_test)

# MLPClassifier (sklearn) ile model oluştur ve eğit
clf = MLPClassifier(hidden_layer_sizes=(64,32), max_iter=500, random_state=42)
clf.fit(X_train_s, y_train)

# Test set tahmini
y_pred = clf.predict(X_test_s)

# Performans metriklerini yazdır (accuracy, precision, recall, f1, confusion matrix)
print("\n📊 [Binary Model] Sonuçlar")
print("Eğitim doğruluk:", clf.score(X_train_s, y_train))
print("Test doğruluk   :", clf.score(X_test_s, y_test))
print("\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=["BENIGN","ATTACK"]))
print("Confusion Matrix:")
print(confusion_matrix(y_test, y_pred))

# Eğitilmiş modeli ve scaler'ı joblib ile kaydet
joblib.dump(clf, os.path.join(MODEL_DIR, 'mini_binary_clf.pkl'))
joblib.dump(scaler, os.path.join(MODEL_DIR, 'scaler.pkl'))
print(f"✅ Binary model ve scaler kaydedildi: {MODEL_DIR}")
