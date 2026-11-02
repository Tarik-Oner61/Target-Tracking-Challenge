# Ayrı test kümesi değerlendirmesi — 2 Kasım 2026

## Model ve veri

- Model: `../models/drone_yolo11n.pt`
- Veri seti: PARS Dataset V2, sürüm 2
- Bölüm: test
- Görüntü: 498
- Etiketli nesne: 981
- Yeni eğitim yapılmadı; mevcut model değerlendirildi.

## Ayarlar

- Ultralytics: 8.4.197
- Python: 3.14.8
- PyTorch: 2.15.0
- Aygıt: Apple M5, MPS
- imgsz: 320
- batch: 2
- workers: 0
- plots: True

Değerlendirme komutunda `conf` belirtilmedi; kütüphanenin
doğrulama varsayılanları kullanıldı. Bu ölçümler, canlı uygulamanın
0.50 güven eşiğiyle yapılan ayrı bir performans ölçümü değildir.

## Sonuçlar

| Sınıf | Nesne sayısı | Precision | Recall | mAP50 | mAP50–95 |
|---|---:|---:|---:|---:|---:|
| Tüm sınıflar | 981 | 0.980 | 0.957 | 0.970 | 0.702 |
| drone | 345 | 0.977 | 0.965 | 0.973 | 0.700 |
| f16 | 291 | 0.983 | 0.921 | 0.949 | 0.672 |
| roket | 345 | 0.979 | 0.986 | 0.988 | 0.735 |

## Süre ve çıktılar

Değerlendirme ilerleme çubuğunda 14.1 saniye raporlandı.

Görüntü başına:
- Ön işleme: 0.8 ms
- Çıkarım: 1.5 ms
- Son işleme: 4.2 ms

Bu süreler canlı arayüz FPS'i veya uçtan uca gecikme değildir.

Çıktı klasörü:
`~/Datasets/pars_v2_runs/test_degerlendirme`

Veri setinin test bölümünde `labels.cache` oluşturuldu.
Ham veri ve bu önbellek repo dışında tutuldu.

## Sınırlar

Veri bölünmeleri arasında aynı veya benzer kare kontrolü yapılmadı.
Bu nedenle ayrı test bölümü kullanılması, görüntülerin birbirinden
tamamen bağımsız olduğunu tek başına kanıtlamaz.

Bu sonuçlar motor kontrolünü, fiziksel hizalamayı veya farklı
ortamlardaki başarıyı değerlendirmez.