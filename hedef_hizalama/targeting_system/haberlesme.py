from time import monotonic, sleep

from protokol import komut_olustur


class SimulasyonBaglantisi:
    """Komut gönderimini donanım olmadan gösterir."""

    def __init__(self):
        self.son_komut = None
        self.son_gonderim = None
        self.yenileme_suresi = 0.1
        self.kapali = False

    def _yaz(self, komut):
        print(f"[SIMULASYON] {komut.strip()}")

    def gonder(self, yatay, dikey):
        if self.kapali:
            raise RuntimeError("Baglanti kapali.")

        komut = komut_olustur(yatay, dikey)
        simdi = monotonic()

        degisti = komut != self.son_komut
        sure_doldu = (
            self.son_gonderim is None
            or simdi - self.son_gonderim >= self.yenileme_suresi
        )

        if degisti or sure_doldu:
            self._yaz(komut)
            self.son_komut = komut
            self.son_gonderim = monotonic()

    def durdur(self):
        """Yenileme süresini beklemeden STOP üret."""
        if self.kapali:
            return

        self._yaz(komut_olustur(0, 0))
        self.son_komut = "STOP\n"
        self.son_gonderim = monotonic()

    def kapat(self):
        if self.kapali:
            return

        try:
            self.durdur()
        finally:
            self.kapali = True


class SeriBaglanti(SimulasyonBaglantisi):
    """Aynı komutları açıkça belirtilen seri porta gönderir."""

    def __init__(self, port):
        import serial

        super().__init__()
        self.seri = None

        if not isinstance(port, str) or not port.strip():
            raise ValueError("Seri port acikca belirtilmeli.")

        try:
            self.seri = serial.Serial(
                port=port,
                baudrate=115200,
                timeout=0,
                write_timeout=0.2,
            )

            # Port açılışında kartın yeniden başlaması için süre tanı.
            # Bu bekleme, kartın hazır olduğuna dair onay değildir.
            sleep(2.0)
            self.durdur()

        except BaseException:
            if self.seri is not None:
                self.seri.close()
            self.kapali = True
            raise

    def _yaz(self, komut):
        veri = komut.encode("ascii")
        yazilan = self.seri.write(veri)

        if yazilan != len(veri):
            raise IOError("Seri mesaj eksik yazildi.")

    def kapat(self):
        if self.kapali:
            return

        try:
            # Bağlantı kopmuşsa STOP gönderimi hata verebilir.
            self.durdur()
        finally:
            self.kapali = True
            if self.seri is not None:
                self.seri.close()