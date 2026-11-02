# Drone tespit ve hizalama uygulaması

## Kapsam

YOLO11n ile drone tespiti, görüntü merkezine göre yön hesabı,
hedef kaybında arama isteği ve Tkinter arayüzü geliştirilmiştir.

Varsayılan çalışma modu simülasyondur: hareket komutları gösterilir,
gerçek seri port açılmaz. Fiziksel motor hareketi simüle edilmez.

Arduino kaynak kodu hazırlanmıştır ancak henüz derlenmemiş,
karta yüklenmemiş ve fiziksel donanımda test edilmemiştir.

## Kurulum

Geliştirme ortamı: macOS, Apple Silicon, Python 3.14.8.
Diğer işletim sistemlerinde ve temiz ortamda kurulum test edilmemiştir.

Yeni kurulum için proje ana klasöründe:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r hedef_hizalama/requirements.txt
```

Mevcut sanal ortam varsa yeniden oluşturmak gerekmez.
Tkinter desteği olan bir Python kurulumu ve kamera erişim izni gerekir.

## Çalıştırma

Proje ana klasöründen:

```bash
source .venv/bin/activate
python hedef_hizalama/dashboard/uygulama.py
```

Model repoda bulunur; uygulamayı çalıştırmak için ham veri setini
indirmek veya yeniden eğitim yapmak gerekmez.

Kamera indeksi 0 kullanılır. Aynı anda başka bir kamera test
uygulaması çalıştırılmamalıdır.

## Kullanım

- Başlat: Tespit bilgilerini gösterir ve hareket komutu üretimini açar.
- Durdur veya Escape: STOP üretir; kamera önizlemesi devam eder.
- Tekrar Başlat basılmadan hareket komutları yeniden başlamaz.
- Ardışık aynı komutlar tekrar sayısıyla gruplanır; son 500 geçmiş satırı bellekte tutulur.
- Temizle yalnızca komut geçmişini temizler.
- Pencereyi kapatma sırasında STOP gönderilmeye çalışılır.

Başlat öncesinde ve Durdur sonrasında hedef bilgileri ve kutular
gizlenir. Model arka planda görüntü işlemeye devam eder.

## Gerçek seri bağlantı seçeneği

Yalnızca doğru donanım yapılandırması doğrulandıktan sonra:

```bash
python hedef_hizalama/dashboard/uygulama.py --port PORT_ADI
```

`PORT_ADI` gerçek cihaz portuyla değiştirilmelidir.
Gerçek UART bağlantısı ve fiziksel hizalama test edilmemiştir.

## Belgeler

- [Arayüz ve hata davranışı](hedef_hizalama/dashboard/KULLANIM.md)
- [Arduino bağlantısı ve protokol](hedef_hizalama/mcu/BAGLANTI_VE_PROTOKOL.md)
- [Eğitim bilgileri](hedef_hizalama/yolo/EGITIM.md)
- [Veri seti](hedef_hizalama/yolo/dataset/KULLANILAN_VERISETI.md)
- [Model bilgileri](hedef_hizalama/yolo/models/README.md)
- [Doğrulama sonuçları](hedef_hizalama/yolo/results/README.md)
- [Ayrı test sonuçları](hedef_hizalama/yolo/results/TEST_SONUCLARI.md)

## Doğrulamalar ve sınırlar

- Kamera ve canlı tespit, dahili kamera ve telefondaki drone
  fotoğrafıyla denenmiştir.
- Hizalama fonksiyonunda 8 kontrol geçmiştir.
- Komut protokolünde 15 kontrol geçmiştir.
- Seri katman sahte portla 7 kontrolden geçmiştir.
- Ayrı test kümesinde 498 görüntü değerlendirilmiştir.
- Drone test mAP50: 0.973; mAP50–95: 0.700.

Bu ölçümler tüm sistemin veya fiziksel hizalamanın başarı oranı değildir.

Her karede en yüksek güvenli drone seçilir; kalıcı hedef kimliği
takibi yoktur. Birden fazla drone varsa hedef değişebilir.

Veri bölünmeleri arasında benzer/tekrarlanan kare kontrolü yapılmamıştır.
Gerçek motor, sürücü, mekanik sınır ve acil durdurma doğrulaması yoktur.