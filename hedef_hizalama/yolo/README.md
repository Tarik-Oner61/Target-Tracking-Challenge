# Dataset ve YOLO modeli

Dataset bilgilerini, eğitim sonuçlarını ve eğitilmiş YOLO modelini bu klasörde teslim edin. Drone veri setleri tarafımızdan sağlanmaktadır; adaylardan ayrıca veri seti araştırmaları beklenmemektedir. YOLO sürümü seçimi ve model eğitimi adaya aittir.

Sağlanan iki veri setinin bağlantıları [dataset/README.md](dataset/README.md) dosyasındadır. Eğitimde bu kaynaklardan kullanılan veri seti/sürüm bilgilerini belgeleyin.

- `dataset/`: veri seti kaynağı, kullanım/lisans bilgisi, sınıflar ve eğitim/doğrulama/test bölünmesi gibi açıklamalar.
- `results/`: eğitim sonuçları, tespit başarısını gösteren ölçümler ve örnek çıktılar.
- `models/`: eğitilmiş model dosyası ve hangi eğitimden üretildiğini açıklayan bilgiler.

Kullanılan eğitim komutunu ve modelin targeting_system tarafından nasıl yüklendiğini belgeleyin. Büyük model/veri dosyaları için Git LFS kullanılabilir.

Repo kökündeki [hedef-drone.jpeg](../../hedef-drone.jpeg) görevin hedef referans fotoğrafıdır; tek başına eğitilmiş model veya eğitim veri seti değildir.
