#include <Arduino.h>
#include <string.h>

// Seçilen pinler: takımın mevcut bağlantısı değildir.
// Gerçek bağlantıya göre değiştirilmeli.
const uint8_t YAW_STEP = 2;
const uint8_t YAW_DIR = 3;
const uint8_t PITCH_STEP = 4;
const uint8_t PITCH_DIR = 5;

// Fiziksel eksen yönüne göre ters çevrilebilir.
const bool YAW_TERS = false;
const bool PITCH_TERS = false;

// Başlangıç ayarları; donanım üzerinde ayarlanmamıştır.
const unsigned long ADIM_ARALIGI_US = 5000;  // En fazla ~200 darbe/s.
const unsigned long KOMUT_ZAMAN_ASIMI_MS = 500;

// Açılıştaki konuma göre darbe sayısı sınırları.
// Bunlar derece veya ölçülmüş fiziksel konum değildir.
const long YAW_MIN = -200;
const long YAW_MAX = 200;
const long PITCH_MIN = -100;
const long PITCH_MAX = 100;

int8_t yawYon = 0;
int8_t pitchYon = 0;

long yawKonum = 0;
long pitchKonum = 0;

unsigned long sonKomutMs = 0;
unsigned long sonAdimUs = 0;

char satir[32];
uint8_t uzunluk = 0;
bool satiriAtla = false;


void durdur() {
  yawYon = 0;
  pitchYon = 0;
  digitalWrite(YAW_STEP, LOW);
  digitalWrite(PITCH_STEP, LOW);
}


void komutuIsle(const char* mesaj) {
  if (strcmp(mesaj, "STOP") == 0) {
    durdur();
    sonKomutMs = millis();
    return;
  }

  // Yalnızca protokolün izin verdiği tam mesajları kabul et.
  // Böylece eksik, ek alanlı veya taşan sayılı mesajlar reddedilir.
  char beklenen[16];

  for (int y = -1; y <= 1; y++) {
    for (int p = -1; p <= 1; p++) {
      snprintf(beklenen, sizeof(beklenen), "MOVE %d %d", y, p);

      if (strcmp(mesaj, beklenen) == 0) {
        yawYon = y;
        pitchYon = p;
        sonKomutMs = millis();
        return;
      }
    }
  }

  // Geçersiz mesaj, hareketi durdurur.
  durdur();
}


void seriOku() {
  // Yoğun seri veri, motor ve zaman aşımı kontrollerini engellemesin.
  uint8_t okunan = 0;

  while (Serial.available() > 0 && okunan < 32) {
    char c = (char)Serial.read();
    okunan++;

    if (c == '\n') {
      if (!satiriAtla) {
        satir[uzunluk] = '\0';
        komutuIsle(satir);
      }
      uzunluk = 0;
      satiriAtla = false;
      continue;
    }

    if (satiriAtla) {
      continue;
    }

    // Protokol LF kullanır; diğer kontrol karakterleri geçersizdir.
    if (c < 32 || c > 126 || uzunluk >= sizeof(satir) - 1) {
      durdur();
      uzunluk = 0;
      satiriAtla = true;  // Sonraki LF'ye kadar mesajın kalanını at.
      continue;
    }

    satir[uzunluk++] = c;
  }
}


void eksenAdimi(
  uint8_t stepPin,
  uint8_t dirPin,
  int8_t yon,
  bool ters,
  long &konum,
  long altSinir,
  long ustSinir
) {
  if (yon == 0) {
    return;
  }

  long yeniKonum = konum + yon;

  // Sınır dışına giden darbeyi üretme; geri dönüşe izin ver.
  if (yeniKonum < altSinir || yeniKonum > ustSinir) {
    return;
  }

  bool dirSeviyesi = (yon > 0);
  if (ters) {
    dirSeviyesi = !dirSeviyesi;
  }

  digitalWrite(dirPin, dirSeviyesi ? HIGH : LOW);
  delayMicroseconds(5);

  digitalWrite(stepPin, HIGH);
  delayMicroseconds(5);
  digitalWrite(stepPin, LOW);

  konum = yeniKonum;
}


void setup() {
  pinMode(YAW_STEP, OUTPUT);
  pinMode(YAW_DIR, OUTPUT);
  pinMode(PITCH_STEP, OUTPUT);
  pinMode(PITCH_DIR, OUTPUT);

  digitalWrite(YAW_DIR, LOW);
  digitalWrite(PITCH_DIR, LOW);
  durdur();

  Serial.begin(115200);
  sonKomutMs = millis();
  sonAdimUs = micros();
}


void loop() {
  seriOku();

  // unsigned fark hesabı, zaman sayacı taşmasına dayanıklıdır.
  if ((unsigned long)(millis() - sonKomutMs) >= KOMUT_ZAMAN_ASIMI_MS) {
    durdur();
  }

  unsigned long simdiUs = micros();

  if ((unsigned long)(simdiUs - sonAdimUs) >= ADIM_ARALIGI_US) {
    sonAdimUs = simdiUs;

    eksenAdimi(
      YAW_STEP, YAW_DIR, yawYon, YAW_TERS,
      yawKonum, YAW_MIN, YAW_MAX
    );

    eksenAdimi(
      PITCH_STEP, PITCH_DIR, pitchYon, PITCH_TERS,
      pitchKonum, PITCH_MIN, PITCH_MAX
    );
  }
}