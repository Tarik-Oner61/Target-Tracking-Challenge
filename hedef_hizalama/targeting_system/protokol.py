def komut_olustur(yatay, dikey):
    """İki eksenin yön isteğini seri haberleşme mesajına çevirir."""

    # Yalnızca -1, 0 ve 1 tam sayılarını kabul et.
    for yon in (yatay, dikey):
        if type(yon) is not int or yon not in (-1, 0, 1):
            raise ValueError("Yonler -1, 0 veya 1 tam sayisi olmali.")

    # İki eksende de hareket gerekmiyorsa durdur.
    if yatay == 0 and dikey == 0:
        return "STOP\n"

    return f"MOVE {yatay} {dikey}\n"