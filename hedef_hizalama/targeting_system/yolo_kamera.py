from time import monotonic
from pathlib import Path

import cv2
from ultralytics import YOLO
from hizalama import hizalama_karari

# Bu dosyanın konumundan hareketle modelin yolunu bul.
model_yolu = (
    Path(__file__).resolve().parent.parent
    / "yolo" / "models" / "drone_yolo11n.pt"
)

# Model yoksa kamera açılmadan anlaşılır bir hata ver.
if not model_yolu.is_file():
    raise FileNotFoundError(f"Model bulunamadi: {model_yolu}")

# Modeli yalnızca bir kez yükle.
model = YOLO(str(model_yolu))

kamera = cv2.VideoCapture(0, cv2.CAP_AVFOUNDATION)

try:
    if not kamera.isOpened():
        raise RuntimeError("Kamera acilamadi!")

    print("Cikmak icin goruntu penceresindeyken Q tusuna basin.")

    # Arama için başlangıç ayarları; fiziksel olarak ayarlanmış değildir.
    kayip_bekleme = 1.0
    arama_yon_suresi = 2.0

    # Başlangıçta hedef henüz görülmedi.
    kayip_baslangici = monotonic()

    while True:
        basarili, goruntu = kamera.read()

        if not basarili:
            print("Goruntu alinamadi!")
            break

        # Bu karedeki nesneleri tespit et.
        sonuclar = model.predict(
            source=goruntu,
            imgsz=320,
            conf=0.50,
            classes=[0],  # Yalnızca drone sınıfının tespitlerini döndür.
            device="mps",
            save=False,
            verbose=False,
        )

        # Tek kare gönderdiğimiz için ilk sonucu al ve kutuları çiz.
        isaretli_goruntu = sonuclar[0].plot()
        # Görüntünün boyutlarından merkez noktasını hesapla.
        yukseklik, genislik = goruntu.shape[:2]
        merkez_x = genislik // 2
        merkez_y = yukseklik // 2

        # Görüntü merkezini beyaz bir artı ile göster.
        cv2.drawMarker(
            isaretli_goruntu,
            (merkez_x, merkez_y),
            (255, 255, 255),
            cv2.MARKER_CROSS,
            30,
            2,
        )

        kutular = sonuclar[0].boxes

        # Her kareye hareket isteği olmadan başla.
        yatay = 0
        dikey = 0
        karar = "HEDEF_YOK"
        durum = "Drone bulunamadi"

        if len(kutular) > 0:
            # Hedef görüldü; kayıp süresini sıfırla.
            kayip_baslangici = None

            # Drone'lar arasından en yüksek güven skorunu seç.
            secilen = int(kutular.conf.argmax().item())

            # Kutunun sol üst ve sağ alt köşe koordinatlarını al.
            x1, y1, x2, y2 = kutular.xyxy[secilen].tolist()

            hedef_x = int((x1 + x2) / 2)
            hedef_y = int((y1 + y2) / 2)

            hata_x = hedef_x - merkez_x
            hata_y = hedef_y - merkez_y

            # Seçilen drone'un merkezine sarı nokta koy.
            cv2.circle(
                isaretli_goruntu,
                (hedef_x, hedef_y),
                6,
                (0, 255, 255),
                -1,
            )

            # Görüntü merkezi ile hedef merkezini birleştir.
            cv2.line(
                isaretli_goruntu,
                (merkez_x, merkez_y),
                (hedef_x, hedef_y),
                (0, 255, 255),
                2,
            )

            # Test ettiğimiz fonksiyonla hareket yönlerini belirle.
            karar, yatay, dikey = hizalama_karari(
                hata_x, hata_y, genislik, yukseklik
            )

            if karar == "HIZALI":
                durum = "GORUNTUDE HIZALI"
            else:
                durum = (
                    f"HIZALAMA GEREKLI | "
                    f"Yatay: {yatay:+d} Dikey: {dikey:+d}"
                )

        else:
            simdi = monotonic()

            # Hedefin kaybolduğu ilk karede süreyi başlat.
            if kayip_baslangici is None:
                kayip_baslangici = simdi

            kayip_suresi = simdi - kayip_baslangici

            if kayip_suresi < kayip_bekleme:
                karar = "HEDEF_YOK"
                durum = "HEDEF YOK | BEKLENIYOR"
            else:
                karar = "ARAMA"

                # Bekleme bittikten sonra her 2 saniyede yön değiştir.
                arama_suresi = kayip_suresi - kayip_bekleme
                arama_asamasi = int(arama_suresi / arama_yon_suresi)

                yatay = 1 if arama_asamasi % 2 == 0 else -1
                dikey = 0

                durum = f"ARAMA ISTEGI | Yatay: {yatay:+d}"

        # Güncel hizalama, bekleme veya arama durumunu göster.
        cv2.putText(
            isaretli_goruntu,
            durum,
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 255),
            2,
        )
        cv2.imshow("Marmara Rover - YOLO", isaretli_goruntu)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

except KeyboardInterrupt:
    print("\nKullanici tarafindan durduruldu.")

finally:
    # Hata olsa da normal çıkılsa da kamerayı serbest bırak.
    kamera.release()
    cv2.destroyAllWindows()