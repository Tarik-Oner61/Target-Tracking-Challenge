# YOLO modelinin eğitimi

## Belgeler

- [Kullanılan veri seti](dataset/KULLANILAN_VERISETI.md)
- [Model bilgileri ve yükleme örneği](models/README.md)
- [Eğitim sonuçları](results/README.md)

## Eğitim ortamı

- Python: 3.14.8
- Ultralytics: 8.4.197
- PyTorch: 2.15.0
- torchvision: 0.29.2
- PyYAML: 6.0.3
- İşlem aygıtı: Apple Silicon üzerinde MPS

Bunlar eğitimin gerçekleştirildiği ortamın sürümleridir.
Diğer ortamlarla uyumluluk ayrıca test edilmemiştir.

## Veri konumu

Veri seti repo dışında, `~/Datasets/pars_v2` altında tutulmuştur.
Orijinal `data.yaml` korunarak ayrı bir `data_local.yaml` oluşturulmuştur.

Yerel YAML dosyasının düzeni şöyledir:

```yaml
path: /VERI_SETININ/TAM/YOLU/pars_v2
train: train/images
val: valid/images
test: test/images
nc: 3
names: ['drone', 'f16', 'roket']
```

`path` alanı, verinin bulunduğu gerçek mutlak yol ile değiştirilmelidir.
Yukarıdaki yol yalnızca yer tutucudur.

## Kullanılan eğitim komutu

Aşağıdaki komut, proje sanal ortamı aktifken çalıştırılmıştır.
Başlangıç ağırlıkları `~/Datasets/pars_v2/yolo11n.pt` konumundadır.

```bash
yolo detect train \
  model="$HOME/Datasets/pars_v2/yolo11n.pt" \
  data="$HOME/Datasets/pars_v2/data_local.yaml" \
  project="$HOME/Datasets/pars_v2_runs" \
  name=tam_veri_10ep \
  epochs=10 fraction=1.0 imgsz=320 batch=2 \
  device=mps workers=0 cache=False plots=True
```

Eğitim, önceden eğitilmiş YOLO11n ağırlıklarından başlatılmıştır.
İlk küçük eğitim denemesinin ağırlıkları kullanılmamıştır.

## Kesintiden devam

İlk iki epoch sonrasında kullanıcı tarafından durdurulan eğitim,
aşağıdaki komutla üçüncü epoch'tan sürdürülmüştür:

```bash
yolo detect train \
  model="$HOME/Datasets/pars_v2_runs/tam_veri_10ep/weights/last.pt" \
  resume=True
```

Toplam 10 epoch tamamlanmıştır. Bu devam komutu, yaşanan kesintiyi
belgelemek içindir; tamamlanmış eğitim için yeniden çalıştırılmamalıdır.

## Teslim edilen model

Tamamlanan çalışmanın `weights/best.pt` dosyası,
`models/drone_yolo11n.pt` adıyla repoya kopyalanmıştır.

Model üç sınıfı tanır: drone, f16 ve roket.

Modelin Python ile yüklenmesi `models/README.md` içinde gösterilmiştir.
Model, `targeting_system/yolo_kamera.py` ve `dashboard/uygulama.py`
uygulamalarına bağlanmıştır. Canlı kamera görüntüsünde yalnızca
drone sınıfı (classes=[0]) kullanılır.