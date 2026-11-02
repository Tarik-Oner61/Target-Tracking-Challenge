# YOLO11n eğitim sonuçları

## Eğitim özeti

- Eğitim tarihi: 1 Kasım 2026
- Çalışma adı: `tam_veri_10ep`
- Başlangıç modeli: Önceden eğitilmiş Ultralytics `yolo11n.pt`
- Veri seti: PARS Dataset V2, sürüm 2
- Sınıflar: `0: drone`, `1: f16`, `2: roket`
- Kaydedilen model: [drone_yolo11n.pt](../models/drone_yolo11n.pt)

Modelin dosya adında drone geçse de model üç sınıfı da tespit eder.
Eğitime ilk küçük denemenin ağırlıklarından değil, başlangıç
YOLO11n ağırlıklarından başlanmıştır.

## Ortam ve eğitim ayarları

| Özellik | Değer |
| --- | --- |
| Bilgisayar | Apple M5, 16 GiB RAM |
| Python | 3.14.8 |
| Ultralytics | 8.4.197 |
| PyTorch | 2.15.0 |
| İşlem aygıtı | MPS |
| Epoch | 10 |
| Eğitim verisi oranı | 1.0 |
| Görüntü boyutu (imgsz) | 320 |
| Batch | 2 |
| Workers | 0 |
| Görüntü önbelleği (cache) | False |
| Grafik üretimi (plots) | True |
| Optimizer | Otomatik seçilen AdamW |
| Başlangıç öğrenme oranı | 0.001429 |
| Seed | 0 |

`close_mosaic=10` ve toplam epoch sayısı 10 olduğundan mosaic,
eğitimin başlangıcında kapatılmıştır.

İlk iki epoch sonrasında eğitim kullanıcı tarafından kesilmiştir.
Kaydedilen `last.pt` üzerinden `resume=True` ile üçüncü epoch'tan
devam edilmiş ve toplam 10 epoch tamamlanmıştır.

## Veri ve eğitim uyarıları

Kaynak veri setinde 4711 eğitim, 994 doğrulama ve 498 test görüntüsü vardır.

Eğitim sırasında üç görüntü, etiketlerindeki segmentasyon ve nesne
tespiti satırlarının karışması nedeniyle atlanmıştır. Kullanılan
eğitim görüntüsü sayısı 4708 olmuştur. Kaynak etiket dosyaları
elle değiştirilmemiş veya silinmemiştir.

Atlanan görüntüler:

- `IMG_20260809_153548548_BURST7_jpg.rf.fa19554e7f437b1fb7f162cba8b1969b.jpg`
- `IMG_20260809_154254550_BURST5_jpg.rf.21479c26d2da01fb3168cd3281a5781d.jpg`
- `IMG_20260809_154259790_BURST46_jpg.rf.dc7f98841f755dbbf3766fae583abdc6.jpg`

Ayrıca `len(segments)=63` ve `len(boxes)=9472` uyumsuzluğu
bildirilmiş; Ultralytics segment bilgilerini kaldırarak yalnızca
tespit kutularıyla devam etmiştir.

`cache=False` görüntü önbelleğini kapatır. Buna rağmen etiket
bilgileri için `labels.cache` dosyaları oluşturulmuştur.

MPS üzerinde bazı işlemler için deterministik uygulama bulunmadığı
uyarıları alınmıştır. Eğitim devam etmiş ve tamamlanmıştır.
Bu nedenle aynı ayarlarla birebir aynı sayısal sonuçlar garanti edilmez.

## Doğrulama sonuçları

Aşağıdaki değerler eğitim sonunda `best.pt` için alınan doğrulama
sonuçlarıdır. Doğrulama kümesi 994 görüntü ve 1987 etiketli nesne içerir.

| Sınıf | Nesne sayısı | Precision | Recall | mAP50 | mAP50–95 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Tüm sınıflar | 1987 | 0.977 | 0.958 | 0.963 | 0.696 |
| drone | 686 | 0.981 | 0.962 | 0.959 | 0.686 |
| f16 | 603 | 0.972 | 0.931 | 0.943 | 0.671 |
| roket | 698 | 0.978 | 0.983 | 0.987 | 0.731 |

- Precision: Yapılan tespitlerin doğruluğunu özetler.
- Recall: Gerçek nesnelerin ne kadarının tespit edildiğini özetler.
- mAP50: IoU eşiği 0.50 için sınıfların ortalama AP değeridir.
- mAP50–95: IoU eşikleri 0.50–0.95 arasında hesaplanan mAP
  değerlerinin ortalamasıdır.

Bu ölçümler nesne tespitini değerlendirir; takip, motor kontrolü
veya tüm sistemin başarı oranını göstermez.

## Sonuç dosyaları

| Dosya | Açıklama |
| --- | --- |
| `results.csv` | Epoch bazında eğitim ve doğrulama ölçümleri |
| `results.png` | Eğitim kayıpları ve doğrulama ölçümlerinin grafikleri |
| `BoxPR_curve.png` | Precision–Recall eğrileri |
| `confusion_matrix.png` | Karışıklık matrisi |
| `confusion_matrix_normalized.png` | Normalize edilmiş karışıklık matrisi |
| `val_batch0_labels.jpg` | Doğrulama örneklerinin gerçek etiketleri |
| `val_batch0_pred.jpg` | Doğrulama örnekleri üzerindeki model tahminleri |

## Bu aşamadaki sınırlar

- 498 görüntülük test kümesi henüz değerlendirilmemiştir.
- Veri bölünmeleri arasında aynı veya benzer kare kontrolü yapılmamıştır.
- YOLO modeli henüz canlı kamera uygulamasına bağlanmamıştır.
- Uçtan uca takip ve hizalama testi yapılmamıştır.
- UART ve fiziksel motor sistemiyle doğrulama yapılmamıştır.
- Doğrulama sırasında ölçülen çıkarım süresi, canlı uygulama
  FPS değeri olarak yorumlanmamalıdır.

## Güncelleme — 2 Kasım 2026

Yukarıdaki sınırlar eğitim tamamlandığındaki durumu anlatır.
Sonrasında ayrı test kümesi değerlendirmesi tamamlanmıştır:
[Test sonuçları](TEST_SONUCLARI.md).

Model, canlı kamera ve dashboard uygulamasına bağlanmış;
telefon ekranındaki drone fotoğrafıyla yazılım kontrolleri yapılmıştır.
Fiziksel motor ve gerçek UART testleri yapılmamıştır.