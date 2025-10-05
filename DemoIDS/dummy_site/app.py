# dummy_site/app.py
# Flask tabanlı küçük demo sunucusu.
# - /        : form arayüzünü döner (index.html)
# - /submit  : POST ile gelen özellikleri alır, modeli çağırır, sonucu JSON olarak döner
# Ayrıca gelen istekleri logs/traffic_log.csv içine kaydeder.

from flask import Flask, request, jsonify, render_template
from model_loader import ModelBundle
from traffic_logger import append_row
import os

# Flask uygulamasını oluştur. template ve static klasörleri lokal yapıya göre ayarlandı.
app = Flask(__name__, template_folder='templates', static_folder='static')

# ModelBundle: model_loader.py içindeki yardımcı sınıf — modelleri ve scaler'ı yüklüyor.
mb = ModelBundle()

def to_float(val):
    """
    Güvenli float parse fonksiyonu.
    - None veya boş string -> 0.0 döner (varsayılan).
    - Eğer gelen değer int/float ise float'a çevirir.
    - Eğer string içeriyorsa önce trim, sonra virgül (',') varsa noktaya ('.') çevirir,
      böylece "0,3" veya "0.3" her ikisini de doğru şekilde float'a dönüştürür.
    - Geçersiz bir string gelirse ValueError fırlatır (çalışma sırasında handle edilir).
    """
    if val is None:
        return 0.0
    if isinstance(val, (int, float)):
        return float(val)
    s = str(val).strip()
    if s == '':
        return 0.0
    s = s.replace(',', '.')
    return float(s)

# Binary sınıflandırma için modelin "attack" demesi gereken minimum olasılık eşiği.
# Daha yüksek bir threshold => daha az false positive, fakat daha fazla false negative olabilir.
THRESHOLD = 0.6

@app.route('/')
def index():
    """
    Ana sayfa route'u: templates/index.html dosyasını render eder.
    Kullanıcı arayüzü buradan açılır.
    """
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    """
    /submit endpoint'i:
    - POST ile JSON veya form-data bekler.
    - Gelen değerleri to_float ile güvenli şekilde float'a çevirir.
    - Önce gelen request'i logs dosyasına yazar (append_row).
    - ModelBundle ile binary tahmin yapılır; eğer attack ise multiclass tahmini de yapılır.
    - Sonuç JSON olarak client'a döner.
    - Hata durumlarında uygun HTTP kodları ile hata mesajı döner.
    """
    data = request.get_json() or request.form

    # Gelen parametreleri güvenli şekilde parse et
    try:
        duration = to_float(data.get('duration', 0))
        src_bytes = to_float(data.get('src_bytes', 0))
        dst_bytes = to_float(data.get('dst_bytes', 0))
        pkt_rate = to_float(data.get('pkt_rate', 0))
        failed_logins = to_float(data.get('failed_logins', 0))
    except ValueError:
        # Parse hatası: client hatalı veri göndermiş
        return jsonify({'error':'invalid input'}), 400

    # Tahmin için kullanılacak özellik dizisini hazırla (2D array: 1 örnek)
    features = [[duration, src_bytes, dst_bytes, pkt_rate, failed_logins]]

    # İlk logging: gelen ham request bilgilerini kaydet
    append_row({
        'duration': duration,
        'src_bytes': src_bytes,
        'dst_bytes': dst_bytes,
        'pkt_rate': pkt_rate,
        'failed_logins': failed_logins,
        'client_ip': request.remote_addr,
        'note': data.get('note','')
    })

    # Binary tahmin: model_loader içindeki predict_binary çağrılır
    try:
        bin_pred, bin_proba = mb.predict_binary(features)
    except Exception as e:
        # Modelde hata olursa 500 dön
        return jsonify({'error': f'model binary predict error: {str(e)}'}), 500

    # predict_proba çıktısı beklenen formatta ise prob_attack alınır.
    # sklearn modellerinde predict_proba => [prob_class0, prob_class1]
    prob_attack = float(bin_proba[0][1]) if hasattr(bin_proba[0], '__len__') and len(bin_proba[0])>1 else float(bin_proba[0])

    # Threshold ile karar ver: prob_attack >= THRESHOLD ise ATTACK, değilse BENIGN
    bin_label = 'ATTACK' if prob_attack >= THRESHOLD else 'BENIGN'
    # bin_score: gösterilecek skor; attack ise attack olasılığı, benign ise benign olasılığı
    bin_score = prob_attack if bin_label == 'ATTACK' else float(bin_proba[0][0]) if hasattr(bin_proba[0],'__len__') else 1.0-prob_attack

    result = {'binary_label': bin_label, 'binary_score': bin_score}

    # Eğer binary karar ATTACK ise, multiclass modeli çağırıp saldırı türünü al
    if bin_label == 'ATTACK':
        try:
            mlabels, mprobs = mb.predict_multiclass(features)
            # mlabels: tahmin edilen sınıf etiketleri (dizisi)
            # mprobs: her sınıf için olasılık dizisi
            attack_type = str(mlabels[0])
            attack_confidence = float(max(mprobs[0])) if hasattr(mprobs[0], '__len__') else float(mprobs[0])
            result['attack_type'] = attack_type
            result['attack_confidence'] = attack_confidence
        except Exception as e:
            # Multiclass modelde hata olsa bile binary sonucu dön (fail-safe)
            result['attack_type'] = None
            result['attack_confidence'] = 0.0
            result['note'] = f"multiclass error: {str(e)}"

    # İkinci logging: model kararını da kaydet (audit için)
    append_row({
        'duration': duration,
        'src_bytes': src_bytes,
        'dst_bytes': dst_bytes,
        'pkt_rate': pkt_rate,
        'failed_logins': failed_logins,
        'client_ip': request.remote_addr,
        'note': f"model:{result.get('binary_label')} score:{result.get('binary_score')}"
    })

    # JSON sonucu döndür
    return jsonify(result)

if __name__ == '__main__':
    # Lokal geliştirme modu: debug=True
    app.run(debug=True, port=5000)
