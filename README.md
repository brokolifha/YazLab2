# Drone Filo Görev Planlama ve Rota Optimizasyonu

Bu proje, bir drone filosunun görev planlaması ve rota optimizasyonu için A* algoritması, genetik algoritmalar ve kısıtlılık tatmin problemleri (CSP) gibi yapay zeka tekniklerini kullanmaktadır.
Farklı senaryolar üzerinde testler gerçekleştirilmiş ve sonuçlar görselleştirilmiştir.

## İçerik

- `main.py`: Ana uygulama dosyası.
- `data_generator.py`: Senaryo verilerini oluşturan modül.
- `pathfinding.py`: A* algoritması ile rota bulma işlemleri.
- `genetic.py`: Genetik algoritma ile rota optimizasyonu.
- `csp.py`: Kısıtlılık tatmin problemleri için görev atama modülü.
- `models.py`: Veri modelleri ve yapılandırmalar.
- `visualization.py`: Sonuçların görselleştirilmesi.
- `Senaryo1_*.png` / `Senaryo2_*.png`: Senaryo sonuçlarının görselleri.
- `Senaryo1_results.txt` / `Senaryo2_results.txt`: Senaryo sonuçlarının metin dosyaları.
- `Rapor.pdf`: Proje raporu.
- `2425_yazLab_II_drone_filo.pdf`: Proje sunumu veya ek dokümantasyon.

## Kurulum

1. Python 3.x sürümünü sisteminize kurun.
2. Gerekli kütüphaneleri yükleyin:

   ```bash
   pip install -r requirements.txt
   ```

   Not: `requirements.txt` dosyası mevcut değilse, kullanılan kütüphaneleri manuel olarak yükleyin.

## Kullanım

1. Veri setini oluşturun:

   ```bash
   python data_generator.py
   ```

2. Ana uygulamayı çalıştırın:

   ```bash
   python main.py
   ```

3. Sonuçları `Senaryo*_results.txt` dosyalarında ve ilgili görsellerde inceleyebilirsiniz.

## Katkıda Bulunma

Katkılarınızı memnuniyetle karşılıyoruz! Lütfen önce bir konu açarak ne üzerinde çalışmak istediğinizi belirtin.

## Lisans

Bu proje MIT Lisansı altında lisanslanmıştır. Daha fazla bilgi için `LICENSE` dosyasını inceleyin.
