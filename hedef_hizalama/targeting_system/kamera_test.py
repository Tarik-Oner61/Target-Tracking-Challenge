import cv2

# MacBook kamerasını aç
kamera = cv2.VideoCapture(0, cv2.CAP_AVFOUNDATION)

# Kamera açılamazsa programı sonlandır
if not kamera.isOpened():
    print("Kamera acilamadi!")
    raise SystemExit

# Kameradan sürekli görüntü al
while True:
    basarili, goruntu = kamera.read()

    if not basarili:
        print("Goruntu alinamadi!")
        break

    # Görüntüyü bir pencerede göster
    cv2.imshow("Marmara Rover - Kamera Testi", goruntu)

    # Q tuşuna basılırsa döngüden çık
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# Kamera bağlantısını ve pencereleri kapat
kamera.release()
cv2.destroyAllWindows()