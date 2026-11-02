## Bu çalışmada kullanılan veri seti

- Veri seti: PARS Dataset V2
- Roboflow çalışma alanı: `new-workspace-maa2l`
- Proje: `pars-dataset-v2`
- Kullanılan sürüm: 2
- Sürüm bağlantısı: https://universe.roboflow.com/new-workspace-maa2l/pars-dataset-v2/dataset/2
- İndirilen biçim: YOLOv8 nesne tespiti formatı
- Kaynak metadata dosyasında belirtilen lisans: CC BY 4.0

Kaynak/atıf: Roboflow Universe üzerinde `new-workspace-maa2l`
tarafından yayımlanan PARS Dataset V2, sürüm 2.
Lisans bağlantısı: https://creativecommons.org/licenses/by/4.0/

Sağlanan ikinci veri seti bu çalışmada kullanılmamıştır.
Ham veri seti, depo boyutunu artırmamak için repo dışında tutulmuştur.

## Sınıflar

İndirilen sürümün `data.yaml` dosyasında üç sınıf bulunmaktadır:

| Sınıf kimliği | Sınıf adı |
| --- | --- |
| 0 | drone |
| 1 | f16 |
| 2 | roket |

Sağlanan gözatma bağlantılarındaki Drone filtresi, indirilen
veri setinin yalnızca drone sınıfını içerdiği anlamına gelmez.
Model üç sınıfla eğitilmiştir.

## Veri bölünmeleri

Veri setinin sağladığı bölünmeler korunmuş, yeniden bölme yapılmamıştır.

| Bölüm | Kaynaktaki görüntü sayısı | Kullanım |
| --- | ---: | --- |
| train | 4711 | Üç sorunlu örnek atlanarak 4708 görüntüyle eğitim |
| valid | 994 | Eğitim sırasında doğrulama |
| test | 498 | Ayrı test değerlendirmesinde kullanıldı; sonuçlar ../results/TEST_SONUCLARI.md dosyasındadır |

Görüntü ve etiket dosyalarının eşleşmesi kontrol edilmiş;
etiketsiz görüntü veya görüntüsüz etiket bulunmamıştır.
Bu kontrol, bütün etiket içeriklerinin doğru olduğunu garanti etmez.

Bölünmeler arasında aynı veya benzer kare bulunup bulunmadığı
henüz kontrol edilmemiştir.

## Veri hazırlama ve artırma

Roboflow sürüm 2, ön işleme ve veri artırma uygulanmamış sürüm
olarak seçilmiştir. Böylece önceden uygulanmış stretch işlemi
yerine eğitim sırasında görüntü boyutlandırma kullanılmıştır.

- Veri seti YOLOv8 detection biçiminde indirilmiştir; OBB değildir.
- Orijinal `data.yaml` korunmuştur.
- Yerel veri konumunu tanımlayan ayrı bir `data_local.yaml`
  oluşturulmuştur.
- Kullanıcıya özel mutlak yollar içeren bu yerel dosya repoya eklenmemiştir.
- Eğitim `imgsz=320` ile gerçekleştirilmiştir.
- `close_mosaic=10` ve toplam 10 epoch nedeniyle mosaic,
  eğitimin başlangıcında kapatılmıştır.
- Mosaic dışındaki artırma ayarlarının ayrıntıları bu belgede
  listelenmemiştir; mosaic'in kapalı olması bütün artırmaların
  kapalı olduğu anlamına gelmez.

Bir eğitim görüntüsünde gerçek etiket kutuları çizilerek görsel
kontrol yapılmıştır. Veri setinin tamamı görsel olarak denetlenmemiştir.

## Etiket sorunları

Eğitim sırasında üç görüntü, etiketlerinde segmentasyon ve
nesne tespiti satırları karıştığı için Ultralytics tarafından
atlanmıştır. Kaynak dosyalar elle değiştirilmemiş veya silinmemiştir.

Ayrıca segment ve kutu sayılarının uyuşmadığı uyarısı alınmış;
eğitim yalnızca nesne tespit kutularıyla devam etmiştir.

Atlanan dosya adları ve uyarı ayrıntıları:
[Eğitim sonuçları](../results/README.md).