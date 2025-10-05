# train/train_mini_multiclass_model.py
# Multiclass model (saldırı türleri) eğitme script'i.
# - mini_dataset.csv okur
# - LabelEncoder ile string etiketleri 0..N-1 aralığına çevirir
# - scaler uygular, MLPClassifier ile eğitir
# - classification_report ve confusion_matrix çıktısı verir
# - model, label encoder ve scaler'ı models/ altına kaydeder

import os, joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import classification_report, confusion_matrix

# Proje kökü ve model klasörü
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "models")
os.makedirs(MODEL_DIR, exist_ok=True)

# Veri yükleme
DATA_PATH = os.path.join(BASE_DIR, "mini_dataset.csv")
if not os.path.exists(DATA_PATH):
    raise FileNotFoundError(f"mini_dataset.csv bulunamadı: {DATA_PATH}")

df = pd.read_csv(DATA_PATH)

# Özellikler ve etiket kodlama
features = ['duration','src_bytes','dst_bytes','pkt_rate','failed_logins']
X = df[features].values
le = LabelEncoder()
y = le.fit_transform(df['label'].values)  # y -> numeric sınıf indeksleri

# Train/test split (sınıf oranlarını koru)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# Scaler eğit ve uygulama
scaler = StandardScaler().fit(X_train)
X_train_s, X_test_s = scaler.transform(X_train), scaler.transform(X_test)

# MLPClassifier ile multiclass eğitim
clf = MLPClassifier(hidden_layer_sizes=(128,64), max_iter=500, random_state=42)
clf.fit(X_train_s, y_train)

# Test tahmini
y_pred = clf.predict(X_test_s)

# Metrikler: her sınıf için precision/recall/f1 ve confusion matrix
print("\n📊 [Multiclass Model] Sonuçlar")
print("Eğitim doğruluk:", clf.score(X_train_s, y_train))
print("Test doğruluk   :", clf.score(X_test_s, y_test))
print("\nClassification Report:")
print(classification_report(y_test, y_pred, target_names=le.classes_))
print("Confusion Matrix:")
print(confusion_matrix(y_test, y_pred))

# Modeli, label encoder'ı ve scaler'ı kaydet
joblib.dump(clf, os.path.join(MODEL_DIR, 'mini_multiclass_clf.pkl'))
joblib.dump(le, os.path.join(MODEL_DIR, 'label_encoder.pkl'))
joblib.dump(scaler, os.path.join(MODEL_DIR, 'scaler.pkl'))
print(f"✅ Multiclass model, label encoder ve scaler kaydedildi: {MODEL_DIR}")
