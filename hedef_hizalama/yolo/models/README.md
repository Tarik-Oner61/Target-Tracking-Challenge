# Eğitilmiş YOLO modeli

## Model dosyası

`drone_yolo11n.pt`, önceden eğitilmiş Ultralytics YOLO11n modelinin
PARS Dataset V2 sürüm 2 üzerinde eğitilmesiyle elde edilmiştir.

`tam_veri_10ep` çalışmasının `weights/best.pt` dosyası,
adı değiştirilerek bu klasöre kopyalanmıştır.

Dosya adında drone geçmesine rağmen model üç sınıfı da tespit eder:

| Sınıf kimliği | Sınıf adı |
| --- | --- |
| 0 | drone |
| 1 | f16 |
| 2 | roket |

## Eğitim kökeni

- Başlangıç ağırlıkları: `yolo11n.pt`
- Veri seti: PARS Dataset V2, sürüm 2
- Toplam eğitim: 10 epoch
- Görüntü boyutu: `imgsz=320`
- Batch boyutu: 2
- İşlem aygıtı: Apple MPS
- Ultralytics sürümü: 8.4.197
- PyTorch sürümü: 2.15.0
- Kullanılan görüntüler: 4708 eğitim, 994 doğrulama

İlk iki epoch sonrasında kesilen eğitim, `last.pt` üzerinden
üçüncü epoch'tan sürdürülmüş ve toplam 10 epoch tamamlanmıştır.

Ayrıntılı ölçümler ve eğitim uyarıları:
[Eğitim sonuçları](../results/README.md).

Veri seti açıklamaları:
[Veri seti](../dataset/KULLANILAN_VERISETI.md).

## Python ile yükleme örneği

Aşağıdaki örnek, proje kökünden çalıştırılmak üzere hazırlanmıştır:

```python
from ultralytics import YOLO

# Eğitilmiş model ağırlıklarını yükle.
model = YOLO("hedef_hizalama/yolo/models/drone_yolo11n.pt")

# Modelde kayıtlı sınıf kimliklerini ve adlarını göster.
print(model.names)
```

Bu kod yalnızca model yükleme örneğidir; görüntü üzerinde tahmin yapmaz.
Model, `targeting_system/yolo_kamera.py` ve `dashboard/uygulama.py`
tarafından dosya konumuna göre hesaplanan yoldan yüklenir.
Canlı uygulamalar yalnızca drone sınıfının tespitlerini kullanır.

## Kullanım sınırları

Modelin doğrulama sonuçları, canlı kamera veya fiziksel hizalama
başarısını tek başına göstermez. 498 görüntülük test kümesi
değerlendirilmiştir; sonuçlar `../results/TEST_SONUCLARI.md` içindedir.

Canlı kamera uygulaması, telefon ekranında gösterilen drone
fotoğrafıyla denenmiştir. Gerçek UART ve fiziksel motor testleri
yapılmamıştır.