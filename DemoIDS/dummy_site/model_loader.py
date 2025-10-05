# dummy_site/model_loader.py
# Modelleri ve scaler'ı yüklemek için küçük yardımcı sınıf.
# Bu sınıf demo sırasında tek bir noktadan modelleri yükleyip predict wrapper'ları sağlar.

import joblib
import os

# MODEL_DIR: bu dosyanın bir üst dizinindeki "models" klasörünü işaret eder
MODEL_DIR = os.path.join(os.path.dirname(__file__), '..', 'models')

class ModelBundle:
    """
    ModelBundle:
    - __init__: modelleri (binary, multiclass) ve scaler'ı joblib ile yükler.
    - predict_binary(X): scaler uygular, binary predict ve predict_proba döner.
    - predict_multiclass(X): scaler uygular, multiclass tahmin ile olasılıkları döner,
      ayrıca label encoder varsa etiketleri orijinal string sınıf isimlerine çevirir.
    """
    def __init__(self):
        # sklearn ile kaydedilmiş pkl dosyalarını burada yükler.
        self.binary = joblib.load(os.path.join(MODEL_DIR, 'mini_binary_clf.pkl'))
        self.multiclass = joblib.load(os.path.join(MODEL_DIR, 'mini_multiclass_clf.pkl'))
        self.scaler = joblib.load(os.path.join(MODEL_DIR, 'scaler.pkl'))
        # Label encoder (multiclass model için): varsa yükle, yoksa None bırak
        try:
            self.le = joblib.load(os.path.join(MODEL_DIR, 'label_encoder.pkl'))
        except:
            self.le = None

    def predict_binary(self, X):
        """
        Binary tahmin wrapper:
        - X: 2D array-like (n_samples, n_features)
        - scaler.transform ile normalize et, sonra binary modelin predict ve predict_proba'sını çağır.
        - (predict_proba ile attack olasılığını elde edebiliyoruz)
        """
        Xs = self.scaler.transform(X)
        return self.binary.predict(Xs), self.binary.predict_proba(Xs)

    def predict_multiclass(self, X):
        """
        Multiclass tahmin wrapper:
        - X: 2D array-like
        - scaler.transform ile normalize edilir
        - model.predict ile sınıf indeksleri alınır, model.predict_proba ile olasılıklar elde edilir
        - eğer LabelEncoder varsa indeksleri orijinal etiketlere çeviririz
        - dönen: (labels, probs)
        """
        Xs = self.scaler.transform(X)
        y_pred = self.multiclass.predict(Xs)
        probs = self.multiclass.predict_proba(Xs)
        if self.le is not None:
            labels = self.le.inverse_transform(y_pred)
        else:
            labels = y_pred
        return labels, probs

