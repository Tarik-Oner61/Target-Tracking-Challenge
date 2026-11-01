# Arduino bağlantısı ve haberleşme protokolü

## Doğrulama durumu

`motor_kontrol/motor_kontrol.ino`, Arduino UNO için hazırlanmıştır.
Henüz Arduino derleyicisiyle derlenmemiş ve fiziksel donanımda
test edilmemiştir.

Hedef donanım: iki adet 200 tam adım/devir NEMA17 ve TMC2209 sürücü.
Mikrostep ayarı, mekanik aktarım ve gerçek eksen yönleri doğrulanmamıştır.

## Seçilen sinyal pinleri

Bu pinler proje için seçilmiştir; takımın mevcut bağlantısı değildir.

| Arduino UNO | Sürücü sinyali |
|---|---|
| D2 | Yaw STEP |
| D3 | Yaw DIR |
| D4 | Pitch STEP |
| D5 | Pitch DIR |
| GND | Sürücü mantık devresinin ortak GND bağlantısı |

Motorlar Arduino pinlerinden beslenmez.
Motor beslemesi, sürücü akım sınırı, mantık gerilimi, mikrostep
ve EN bağlantısı kullanılan TMC2209 modülüne göre ayrıca
doğrulanmalıdır. Bu tablo tam bir güç bağlantı şeması değildir.

EN pini yazılımla kontrol edilmez. STOP, STEP darbelerini keser;
sürücü devredeyse motor tutma akımı devam edebilir.

`YAW_TERS` ve `PITCH_TERS` sabitleri fiziksel yön eşlemesi için
değiştirilebilir. Görüntüde +X sağa, +Y aşağıya karşılık gelir;
bunların mekanik yön karşılığı gerçek sistemde doğrulanmalıdır.

## UART

Laptop, UNO'nun USB-seri bağlantısı üzerinden haberleşir.
UNO tarafında `Serial` kullanılır.

- Baud: 115200
- Veri: 8 bit
- Parite: yok
- Stop biti: 1
- Akış kontrolü: yok
- Kodlama: ASCII
- Mesaj sonu: LF (`\n`)

Bu UART bağlantısı laptop ile UNO arasındadır.
TMC2209'un kendi UART yapılandırma arayüzü kullanılmaz;
sürücülere STEP/DIR sinyali verilir.

## Mesajlar

| Mesaj | Davranış |
|---|---|
| `MOVE 1 0\n` | Yatay pozitif yön isteği |
| `MOVE -1 1\n` | Yatay negatif, dikey pozitif yön isteği |
| `STOP\n` | İki eksenin STEP darbelerini durdur |

Yönler yalnızca -1, 0 veya 1 olabilir.
Python, iki yön sıfırsa STOP üretir.
Arduino ayrıca `MOVE 0 0\n` mesajını kabul eder.

Boşluklar ve mesaj biçimi tam eşleşmelidir.
CRLF değil LF kullanılmalıdır.
Arduino bu sürümde ACK veya konum geri bildirimi göndermez.
Başarılı seri yazma, komutun uygulandığını kanıtlamaz.

## Zamanlama ve durdurma

Python, komut değiştiğinde hemen; değişmediğinde uygun çağrı
geldikçe en az 0.1 saniyelik aralıkla yeniden gönderir.
Bu işlem bağımsız bir arka plan zamanlayıcısı değildir.

Arduino son geçerli komuttan itibaren 500 ms boyunca yeni
geçerli komut alamazsa hareketi durdurur.

Geçersiz mesaj, kontrol karakteri veya fazla uzun satır da
hareketi durdurur. Hata kalıcı kilit oluşturmaz; daha sonra
gelen geçerli MOVE komutu hareketi yeniden başlatabilir.

Uygulama kapanışında STOP gönderilmeye çalışılır.
Bağlantı kopmuşsa STOP ulaştırılamayabilir; Arduino zaman aşımı
bu durum için ek yazılım önlemidir. Fiziksel acil durdurma değildir.

## Hız ve konum sınırları

- Adım aralığı: 5000 mikrosaniye.
- Eksen başına yaklaşık üst sınır: saniyede 200 STEP darbesi.
- Yaw darbe sayacı sınırı: -200 ile +200.
- Pitch darbe sayacı sınırı: -100 ile +100.

Bu değerler fiziksel sistemde ayarlanmamış başlangıç tercihleridir.
Darbe sayısı, mikrostep ve mekanik aktarım bilinmeden derece
veya gerçek motor konumu olarak yorumlanamaz.

Sayaçlar açılışta sıfır kabul edilir.
Homing, limit anahtarı, encoder ve adım kaçırma tespiti yoktur.
Yazılımsal sınırlar gerçek mekanik sınır garantisi sağlamaz.
İvmelenme/yavaşlama profili uygulanmamıştır.

## Planlanan yükleme yöntemi

Donanımlı doğrulama yapacak kişi için:

1. Arduino IDE'de `motor_kontrol/motor_kontrol.ino` dosyasını aç.
2. Kart olarak Arduino UNO'yu seç.
3. Önce Verify ile derle.
4. Sürücü, besleme, pin, yön ve hareket sınırlarını doğrula.
5. Doğru portu seçerek karta yükle.
6. Seri Monitör gibi portu kullanan diğer programları kapat.
7. Laptop uygulamasını doğru `--port` değeriyle çalıştır.

Bu adımlar henüz uygulanmamıştır.