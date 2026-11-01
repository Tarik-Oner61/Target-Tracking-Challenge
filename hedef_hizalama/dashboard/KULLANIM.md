# Drone takip arayüzü

## Çalıştırma

Proje ana klasöründen, gerekli paketlerin bulunduğu sanal
ortam aktifken:

```bash
python hedef_hizalama/dashboard/uygulama.py
```

Varsayılan mod simülasyondur. Seri port açılmaz.
MOVE ve STOP mesajları terminalde gösterilir.
Bu mod, fiziksel motor dinamiğini simüle etmez.

Gerçek seri bağlantı yalnızca açıkça port verilirse açılır:

```bash
python hedef_hizalama/dashboard/uygulama.py --port PORT_ADI
```

`PORT_ADI` gerçek cihaz portuyla değiştirilmelidir.
Gerçek UART ve motor sistemiyle test yapılmamıştır.

## Arayüz

- Başlangıçta kamera açık, hareket komutu üretimi durdurulmuştur.
- Başlat: Yeni kamera sonuçlarından hareket komutu üretir.
- Durdur veya Escape: STOP üretir; görüntü devam eder.
- Durdur sonrasında yeniden Başlat basılmadan MOVE üretilmez.
- Pencereyi kapatma: STOP üretmeye çalışır, kamera işçisinin
  bitmesini bekler ve bağlantıyı kapatır.

## Sistem bağlantısı

`uygulama.py`, kamera ve YOLO işlemlerini ayrı bir iş parçacığında
çalıştırır. Kuyrukta yalnızca en yeni sonuç tutulur.

Arayüz ana iş parçacığında çalışır ve komut gönderimini yönetir.

Kullanılan targeting_system modülleri:

- `hizalama.py`: Merkez hatasından yön kararı.
- `protokol.py`: Yönlerden MOVE/STOP mesajı.
- `haberlesme.py`: Simülasyon veya seri bağlantı ve gönderim zamanlaması.

Model:
`hedef_hizalama/yolo/models/drone_yolo11n.pt`

## Davranış ve ayarlar

- Kamera indeksi: 0.
- macOS kamera altyapısı: AVFoundation.
- İşlem aygıtı: MPS kullanılabiliyorsa MPS, aksi halde CPU.
- Tahmin boyutu: 320.
- Güven eşiği: 0.50.
- Kullanılan sınıf: 0, drone.
- Hedef seçimi: Her karede en yüksek güvenli drone.
- Hizalama toleransı: Her eksende görüntü boyutunun %3'ü.
- Hedef kaybında bekleme: 1 saniye.
- Aramada yatay yön değişimi: 2 saniye.

Aynı drone'un kimliğini kareler arasında koruyan bir takip
algoritması yoktur. Birden fazla drone varsa hedef değişebilir.

## Hata davranışı

Kare alınma zamanından itibaren 0.5 saniyeden eski sonuçlarla
hareket üretilmez. Görüntü geciktiğinde sistem durdurulur;
yeniden Başlat gerekir.

Kamera, model veya arayüz hatasında STOP üretmeye çalışılır.
Uygulama hatası sonrasında yeniden başlatmak için program
kapatılıp açılmalıdır.

Pencere kapatılırken kamera işçisinin bitmesi beklenir.
Kamera okuması veya model işlemi takılırsa kapanış gecikebilir.

Seri yazma zaman aşımı 0.2 saniyedir.
Seri port açılışında 2 saniye beklenir; bu, Arduino'dan alınmış
bir hazır onayı değildir.

## Yapılan kontroller

Mac'in dahili kamerası ve telefonda gösterilen drone fotoğrafıyla:

- Canlı görüntü ve drone tespiti.
- Başlat ile komut üretimi.
- Durdur ile STOP ve yeniden Başlat'a kadar MOVE üretilmemesi.
- Yeniden Başlat ile çalışmaya devam.
- Pencere kapanışında STOP ve terminale dönüş.

İlk sürümde PPM/Base64 görüntü aktarımı hata verdi.
Bellekte PNG kodlama kullanılarak görüntü gösterimi düzeltildi.
Görüntüler diske kaydedilmez.

Bu kontroller fiziksel motor veya gerçek UART testleri değildir.
FPS ve durdurma gecikmesi sayısal olarak ölçülmemiştir.
Bütün hata yolları uygulamalı olarak sınanmamıştır.