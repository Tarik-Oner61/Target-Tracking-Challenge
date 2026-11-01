import argparse
import base64
import queue
import sys
import threading
import tkinter as tk
from tkinter import ttk
from pathlib import Path
from time import monotonic

import cv2
import torch
from ultralytics import YOLO

KOK = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(KOK / "targeting_system"))

from haberlesme import SimulasyonBaglantisi, SeriBaglanti
from hizalama import hizalama_karari

from datetime import datetime
from tkinter.scrolledtext import ScrolledText


# Arayüz renkleri
ARKA = "#F3F5F8"
PANEL = "#FFFFFF"
KENAR = "#E2E7EE"
METIN = "#334155"
SOLUK = "#7C899C"
MAVI = "#6685BA"
YESIL = "#528B78"
SARI = "#A88647"
KIRMIZI = "#BC7180"


def kamera_iscisi(kareler, hatalar, cikis):
    """Kamerayı ve modeli çalıştırır; arayüz veya UART'a dokunmaz."""
    kamera = None

    try:
        model_yolu = KOK / "yolo/models/drone_yolo11n.pt"
        if not model_yolu.is_file():
            raise FileNotFoundError(f"Model bulunamadi: {model_yolu}")

        model = YOLO(str(model_yolu))
        aygit = "mps" if torch.backends.mps.is_available() else "cpu"

        if sys.platform == "darwin":
            kamera = cv2.VideoCapture(0, cv2.CAP_AVFOUNDATION)
        else:
            kamera = cv2.VideoCapture(0)

        if not kamera.isOpened():
            raise RuntimeError("Kamera acilamadi.")

        kayip_baslangici = monotonic()

        while not cikis.is_set():
            basarili, goruntu = kamera.read()
            alinan_zaman = monotonic()

            if not basarili:
                raise RuntimeError("Kameradan goruntu alinamadi.")

            sonuc = model.predict(
                goruntu,
                imgsz=320,
                conf=0.50,
                classes=[0],
                device=aygit,
                save=False,
                verbose=False,
            )[0]

            if cikis.is_set():
                break

            cizim = sonuc.plot()
            yukseklik, genislik = goruntu.shape[:2]
            merkez = (genislik // 2, yukseklik // 2)

            yatay = dikey = 0
            hata_x = hata_y = None
            guven = None
            adet = len(sonuc.boxes)

            cv2.drawMarker(
                cizim, merkez, (255, 255, 255),
                cv2.MARKER_CROSS, 30, 2
            )

            if adet > 0:
                kayip_baslangici = None
                secilen = int(sonuc.boxes.conf.argmax().item())
                guven = float(sonuc.boxes.conf[secilen].item())
                x1, y1, x2, y2 = sonuc.boxes.xyxy[secilen].tolist()
                hedef = (int((x1 + x2) / 2), int((y1 + y2) / 2))

                hata_x = hedef[0] - merkez[0]
                hata_y = hedef[1] - merkez[1]

                karar, yatay, dikey = hizalama_karari(
                    hata_x, hata_y, genislik, yukseklik
                )

                cv2.circle(cizim, hedef, 6, (0, 255, 255), -1)
                cv2.line(cizim, merkez, hedef, (0, 255, 255), 2)

            else:
                simdi = monotonic()
                if kayip_baslangici is None:
                    kayip_baslangici = simdi

                sure = simdi - kayip_baslangici
                if sure < 1.0:
                    karar = "HEDEF_YOK"
                else:
                    asama = int((sure - 1.0) / 2.0)
                    yatay = 1 if asama % 2 == 0 else -1
                    karar = "ARAMA"

            # Görsel bilgiler karar hesabını değiştirmez.
            bilgi = {
                "karar": karar,
                "yatay": yatay,
                "dikey": dikey,
                "hata_x": hata_x,
                "hata_y": hata_y,
                "guven": guven,
                "adet": adet,
                "aygit": aygit.upper(),
            }

            try:
                kareler.get_nowait()
            except queue.Empty:
                pass

            kareler.put_nowait(
                (alinan_zaman, goruntu, cizim, bilgi)
            )

    except Exception as hata:
        hatalar.put(str(hata))
    finally:
        if kamera is not None:
            kamera.release()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--port",
        help="Verilmezse simulasyon; verilirse gercek seri port."
    )
    args = parser.parse_args()

    baglanti = (
        SeriBaglanti(args.port)
        if args.port else SimulasyonBaglantisi()
    )

    pencere = tk.Tk()
    pencere.title("Marmara Rover | Hedef Takip")
    pencere.geometry("1180x760")
    pencere.minsize(980, 680)
    pencere.configure(bg=ARKA)

    # Clam teması macOS'ta da düğme renklerini uygulayabilsin.
    stil = ttk.Style(pencere)
    stil.theme_use("clam")

    for ad, renk, uzerinde in [
        ("Baslat.TButton", "#7893BD", "#6782AC"),
        ("Durdur.TButton", "#BE8490", "#AD7380"),
    ]:
        stil.configure(
            ad,
            font=("Helvetica", 13, "bold"),
            foreground="white",
            background=renk,
            borderwidth=0,
            padding=(16, 13),
        )
        stil.map(
            ad,
            background=[("disabled", KENAR), ("active", uzerinde)],
            foreground=[("disabled", SOLUK)],
        )

    kareler = queue.Queue(maxsize=1)
    hatalar = queue.Queue()
    cikis = threading.Event()

    aktif = False
    kapaniyor = False
    hata_var = False
    son_kare = None
    baslatma_zamani = 0.0

    def yazi(ebeveyn, metin, boyut=11, renk=METIN, kalin=False):
        return tk.Label(
            ebeveyn,
            text=metin,
            bg=ebeveyn.cget("bg"),
            fg=renk,
            font=("Helvetica", boyut, "bold" if kalin else "normal"),
            anchor="w",
        )

    # Üst başlık
    baslik = tk.Frame(pencere, bg=ARKA)
    baslik.pack(fill="x", padx=24, pady=(22, 18))

    yazi(baslik, "MARMARA ROVER", 23, METIN, True).pack(side="left")

    mod = "SERİ BAĞLANTI" if args.port else "SİMÜLASYON"
    tk.Label(
        baslik,
        text=f"  {mod}  ",
        bg="#16304A",
        fg=MAVI,
        font=("Helvetica", 11, "bold"),
        padx=10,
        pady=8,
    ).pack(side="right")

    # Alt bilgi, ana alan büyüdüğünde de görünür kalsın.
    alt = tk.Frame(pencere, bg=ARKA)
    alt.pack(side="bottom", fill="x", padx=24, pady=(10, 16))
    yazi(
        alt,
        "ESC: Durdur  •  Durdurulduğunda canlı görüntü devam eder.",
        10, SOLUK
    ).pack(anchor="w")
    yazi(
        alt,
        "Fiziksel motor doğrulaması yapılmadı.",
        10, SOLUK
    ).pack(anchor="w", pady=(3, 0))

    govde = tk.Frame(pencere, bg=ARKA)
    govde.pack(fill="both", expand=True, padx=24)
    govde.columnconfigure(0, weight=1)
    govde.columnconfigure(1, weight=0)
    govde.rowconfigure(0, weight=1)

    # Sol: canlı görüntü
    sol = tk.Frame(
        govde, bg=PANEL, highlightbackground=KENAR, highlightthickness=1
    )
    sol.grid(row=0, column=0, sticky="nsew", padx=(0, 18))

    video_baslik = tk.Frame(sol, bg=PANEL)
    video_baslik.pack(fill="x", padx=16, pady=14)
    yazi(video_baslik, "CANLI GÖRÜNTÜ", 12, METIN, True).pack(side="left")
    kamera_etiketi = yazi(video_baslik, "Hazırlanıyor", 10, SOLUK)
    kamera_etiketi.pack(side="right")

    video_kutu = tk.Frame(sol, bg="#070D17")
    video_kutu.pack(fill="both", expand=True, padx=12, pady=(0, 12))
    video_kutu.pack_propagate(False)

    goruntu_alani = tk.Label(
        video_kutu,
        text="Model ve kamera açılıyor…",
        bg="#070D17",
        fg=SOLUK,
        font=("Helvetica", 13),
    )
    goruntu_alani.pack(fill="both", expand=True)

    # Sağ: durum ve hedef bilgileri
    sag = tk.Frame(
        govde, bg=PANEL, width=300,
        highlightbackground=KENAR, highlightthickness=1
    )
    sag.grid(row=0, column=1, sticky="ns")
    sag.pack_propagate(False)

    yazi(sag, "SİSTEM DURUMU", 10, SOLUK, True).pack(
        fill="x", padx=20, pady=(20, 8)
    )
    durum_baslik = yazi(sag, "DURDURULDU", 20, SOLUK, True)
    durum_baslik.pack(fill="x", padx=20)

    durum_detay = tk.Label(
        sag,
        text="Başlat düğmesini bekliyor.",
        bg=PANEL,
        fg=SOLUK,
        font=("Helvetica", 11),
        justify="left",
        anchor="nw",
        wraplength=255,
    )
    durum_detay.pack(fill="x", padx=20, pady=(8, 18))

    def ayirici():
        tk.Frame(sag, bg=KENAR, height=1).pack(
            fill="x", padx=20, pady=10
        )

    def bilgi_satiri(ad, ilk="—"):
        cerceve = tk.Frame(sag, bg=PANEL)
        cerceve.pack(fill="x", padx=20, pady=7)
        yazi(cerceve, ad, 11, SOLUK).pack(side="left")
        deger = yazi(cerceve, ilk, 12, METIN, True)
        deger.pack(side="right")
        return deger

    ayirici()
    hedef_etiketi = bilgi_satiri("Hedef")
    guven_etiketi = bilgi_satiri("Güven skoru")
    x_etiketi = bilgi_satiri("X merkez hatası")
    y_etiketi = bilgi_satiri("Y merkez hatası")
    aygit_etiketi = bilgi_satiri("İşlem aygıtı")
    ayirici()

    yazi(sag, "SON KOMUT", 10, SOLUK, True).pack(
        fill="x", padx=20, pady=(8, 6)
    )
    komut_etiketi = tk.Label(
        sag,
        text="—",
        bg="#0B1525",
        fg=MAVI,
        font=("Menlo", 16, "bold"),
        anchor="w",
        padx=12,
        pady=12,
    )
    komut_etiketi.pack(fill="x", padx=20)

    dugmeler = tk.Frame(sag, bg=PANEL)
    dugmeler.pack(side="bottom", fill="x", padx=20, pady=20)

    # Kamera panelinin altında kaydırılabilir komut geçmişi.
    gecmis_paneli = tk.Frame(govde, bg=PANEL)
    gecmis_paneli.grid(
        row=1, column=0, columnspan=2,
        sticky="ew", pady=(14, 0)
    )

    gecmis_baslik = tk.Frame(gecmis_paneli, bg=PANEL)
    gecmis_baslik.pack(fill="x", padx=12, pady=(10, 6))

    yazi(
        gecmis_baslik,
        "KOMUT GEÇMİŞİ",
        11, METIN, True
    ).pack(side="left")

    gecmis = ScrolledText(
        gecmis_paneli,
        height=5,
        font=("Menlo", 10),
        bg=PANEL,
        fg=METIN,
        relief="flat",
        borderwidth=0,
        highlightthickness=0,
        wrap="word",
        state="disabled",
    )
    gecmis.pack(fill="x", padx=12, pady=(0, 10))

    kayit_sayisi = 0

    def gecmisi_temizle():
        nonlocal kayit_sayisi
        gecmis.configure(state="normal")
        gecmis.delete("1.0", "end")
        gecmis.configure(state="disabled")
        kayit_sayisi = 0

    ttk.Button(
        gecmis_baslik,
        text="Temizle",
        command=gecmisi_temizle,
    ).pack(side="right")

    def gecmise_ekle(mesaj):
        nonlocal kayit_sayisi

        # Kullanıcı eski kayıtları okuyorsa görünümü aşağı çekme.
        en_altta = gecmis.yview()[1] >= 0.99
        saat = datetime.now().strftime("%H:%M:%S.%f")[:-3]

        gecmis.configure(state="normal")
        gecmis.insert("end", f"{saat}  {mesaj}\n")
        kayit_sayisi += 1

        if kayit_sayisi > 500:
            gecmis.delete("1.0", "2.0")
            kayit_sayisi -= 1

        if en_altta:
            gecmis.see("end")

        gecmis.configure(state="disabled")

    # Bağlantının gerçekten yazdığı komutları gözlemle.
    # Zamanlama veya mesaj içeriği değiştirilmez.
    asil_yaz = baglanti._yaz

    def kayitli_yaz(komut):
        try:
            asil_yaz(komut)
        except Exception as hata:
            gecmise_ekle(
                f"YAZMA HATASI | {komut.strip()} | {hata}"
            )
            raise
        else:
            kaynak = "PORTA YAZILDI" if args.port else "SİMÜLASYON"
            gecmise_ekle(f"{kaynak} | {komut.strip()}")

    baglanti._yaz = kayitli_yaz

    def durum_goster(baslik, detay, renk):
        durum_baslik.configure(text=baslik, fg=renk)
        durum_detay.configure(text=detay)

    def bilgileri_temizle():
        hedef_etiketi.configure(text="—", fg=SOLUK)
        for etiket in (
            guven_etiketi, x_etiketi, y_etiketi, aygit_etiketi
        ):
            etiket.configure(text="—")

    def durdur():
        nonlocal aktif, hata_var
        aktif = False
        gecmise_ekle("SİSTEM | DURDURMA İSTEĞİ")
        bilgileri_temizle()
        try:
            baglanti.durdur()
            komut_etiketi.configure(text="STOP", fg=SOLUK)
            durum_goster(
                "DURDURULDU", "Görüntü açık; hareket isteği kapalı.", SOLUK
            )
        except Exception as hata:
            hata_var = True
            komut_etiketi.configure(text="STOP HATASI", fg=KIRMIZI)
            durum_goster("BAĞLANTI HATASI", str(hata), KIRMIZI)

    def baslat():
        nonlocal aktif, baslatma_zamani
        if hata_var or kapaniyor:
            return

        if son_kare is None or monotonic() - son_kare > 0.5:
            durum_goster(
                "BEKLENİYOR", "Güncel kamera sonucu henüz hazır değil.", SARI
            )
            return

        baslatma_zamani = monotonic()
        aktif = True
        gecmise_ekle("KULLANICI | BAŞLAT")
        durum_goster("BAŞLATILDI", "Yeni kamera sonucu bekleniyor.", MAVI)

    def kapat():
        nonlocal kapaniyor
        if kapaniyor:
            return

        kapaniyor = True
        durdur()
        cikis.set()
        baslat_dugmesi.configure(state="disabled")
        durdur_dugmesi.configure(state="disabled")
        durum_goster("KAPATILIYOR", "Kamera bağlantısı bırakılıyor.", SOLUK)
        kapanisi_bekle()

    def kapanisi_bekle():
        if isci.is_alive():
            pencere.after(50, kapanisi_bekle)
            return

        try:
            baglanti.kapat()
        except Exception as hata:
            print(f"Kapanista baglanti hatasi: {hata}")
        finally:
            # Pencere kapandıktan sonra Text alanına yazılmasını önle.
            baglanti._yaz = asil_yaz
            pencere.destroy()

    baslat_dugmesi = ttk.Button(
        dugmeler, text="BAŞLAT", command=baslat, style="Baslat.TButton"
    )
    baslat_dugmesi.pack(fill="x", pady=(0, 10))

    durdur_dugmesi = ttk.Button(
        dugmeler, text="DURDUR", command=durdur, style="Durdur.TButton"
    )
    durdur_dugmesi.pack(fill="x")

    def hedef_bilgilerini_goster(bilgi):
        hedef_etiketi.configure(
            text=f"Drone · {bilgi['adet']}" if bilgi["adet"] else "Bulunamadı",
            fg=YESIL if bilgi["adet"] else SOLUK,
        )
        guven = bilgi["guven"]
        guven_etiketi.configure(text=f"{guven:.2f}" if guven is not None else "—")

        for etiket, deger in [
            (x_etiketi, bilgi["hata_x"]),
            (y_etiketi, bilgi["hata_y"]),
        ]:
            etiket.configure(
                text=f"{deger:+d} px" if deger is not None else "—"
            )

        aygit_etiketi.configure(text=bilgi["aygit"])

    def guncelle():
        nonlocal hata_var, son_kare

        if kapaniyor:
            return

        try:
            hata = hatalar.get_nowait()
        except queue.Empty:
            hata = None

        if hata is not None:
            durdur()
            hata_var = True
            durum_goster("KAMERA / MODEL HATASI", hata, KIRMIZI)

        try:
            zaman, ham_kare, isaretli_kare, bilgi = kareler.get_nowait()
        except queue.Empty:
            pass
        else:
            son_kare = zaman

            # Durdurulmuş durumda yalnızca sade kamera önizlemesi.
            goster = (
                aktif
                and zaman >= baslatma_zamani
                and monotonic() - zaman <= 0.5
            )
            kare = isaretli_kare if goster else ham_kare

            # Görüntüyü alana sığdır; en-boy oranını koru.
            h, w = kare.shape[:2]
            alan_w = max(1, video_kutu.winfo_width() - 8)
            alan_h = max(1, video_kutu.winfo_height() - 8)
            oran = min(alan_w / w, alan_h / h)
            boyut = (max(1, int(w * oran)), max(1, int(h * oran)))
            kucuk = cv2.resize(kare, boyut)

            basarili, png = cv2.imencode(".png", kucuk)
            if not basarili:
                raise RuntimeError("Arayuz goruntusu olusturulamadi.")

            foto = tk.PhotoImage(
                data=base64.b64encode(png.tobytes()).decode("ascii"),
                format="png",
            )
            goruntu_alani.configure(image=foto, text="")
            goruntu_alani.image = foto

            if (
                aktif
                and zaman >= baslatma_zamani
                and monotonic() - zaman <= 0.5
            ):
                hedef_bilgilerini_goster(bilgi)

            if (
                aktif
                and zaman >= baslatma_zamani
                and monotonic() - zaman <= 0.5
            ):
                yatay, dikey = bilgi["yatay"], bilgi["dikey"]
                baglanti.gonder(yatay, dikey)

                son_komut = baglanti.son_komut
                komut_etiketi.configure(
                    text=son_komut.strip() if son_komut else "—",
                    fg=MAVI,
                )

                kararlar = {
                    "HIZALI": (
                        "GÖRÜNTÜDE HİZALI",
                        "Hedef merkezi tolerans alanının içinde.",
                        YESIL,
                    ),
                    "HIZALANIYOR": (
                        "HİZALAMA İSTEĞİ",
                        "Hedef merkezine doğru yön komutu üretiliyor.",
                        MAVI,
                    ),
                    "HEDEF_YOK": (
                        "HEDEF BEKLENİYOR",
                        "Arama öncesi kısa bekleme; hareket isteği sıfır.",
                        SARI,
                    ),
                    "ARAMA": (
                        "ARAMA İSTEĞİ",
                        "Yatay yön isteği iki saniyede bir değişiyor.",
                        SARI,
                    ),
                }
                durum_goster(*kararlar[bilgi["karar"]])

        taze = son_kare is not None and monotonic() - son_kare <= 0.5
        kamera_etiketi.configure(
            text="GÜNCEL" if taze else "GÖRÜNTÜ BEKLENİYOR",
            fg=YESIL if taze else SARI,
        )

        if not taze:
            hedef_etiketi.configure(text="Güncel veri yok", fg=SOLUK)
            for etiket in (guven_etiketi, x_etiketi, y_etiketi):
                etiket.configure(text="—")

        if aktif and not taze:
            durdur()
            durum_goster(
                "DURDURULDU",
                "Görüntü gecikti. Devam etmek için yeniden Başlat.",
                SARI,
            )

        baslat_dugmesi.configure(
            state="disabled" if hata_var or aktif or not taze else "normal"
        )
        pencere.after(30, guvenli_guncelle)

    def guvenli_guncelle():
        nonlocal hata_var
        try:
            guncelle()
        except Exception as hata:
            durdur()
            hata_var = True
            baslat_dugmesi.configure(state="disabled")
            durum_goster("UYGULAMA HATASI", str(hata), KIRMIZI)

    isci = threading.Thread(
        target=kamera_iscisi,
        args=(kareler, hatalar, cikis),
        daemon=True,
    )
    isci.start()

    pencere.protocol("WM_DELETE_WINDOW", kapat)
    pencere.bind("<Escape>", lambda olay: durdur())
    pencere.after(30, guvenli_guncelle)

    try:
        pencere.mainloop()
    finally:
        cikis.set()
        try:
            baglanti.kapat()
        except Exception as hata:
            print(f"Son STOP/port kapatma hatasi: {hata}")


if __name__ == "__main__":
    main()
