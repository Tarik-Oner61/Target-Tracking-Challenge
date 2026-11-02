def hizalama_karari(hata_x, hata_y, genislik, yukseklik):
    """Görüntüde hedefe doğru yatay ve dikey yönleri hesaplar."""

    tolerans_x = genislik * 0.03
    tolerans_y = yukseklik * 0.03

    # 0: hareket gerekmiyor, +1: sağ, -1: sol
    yatay = 0
    if hata_x > tolerans_x:
        yatay = 1
    elif hata_x < -tolerans_x:
        yatay = -1

    # Görüntü koordinatlarında +1: aşağı, -1: yukarı
    dikey = 0
    if hata_y > tolerans_y:
        dikey = 1
    elif hata_y < -tolerans_y:
        dikey = -1

    if yatay == 0 and dikey == 0:
        durum = "HIZALI"
    else:
        durum = "HIZALANIYOR"

    return durum, yatay, dikey