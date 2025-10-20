# 🎯 AdsGenius - Marketing Intelligence Platform

**AdsGenius**, Google Ads uzmanları için geliştirilmiş profesyonel bir **Global/Lokal Pazarlama İstihbarat Platformu**'dur. İstanbul'daki akü satıcıları sektöründe gerçek zamanlı rekabet analizi ve stratejik karar destek sistemi sağlar.

## 🚀 Demo

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-app-name.streamlit.app)

## 📊 Özellikler

- **🗺️ Interactive Harita**: Gerçek zamanlı rekabet analizi
- **📈 Live Dashboard**: KPI takibi ve performans metrikleri
- **🎯 Acil Hizmet Analizi**: 75 acil hizmet işletmesi tespit edildi
- **📊 Reklam Durumu**: 50 işletme reklam veriyor tespit edildi
- **🔍 Fırsat Analizi**: 48 acil hizmet işletmesi reklam vermiyor (%64 fırsat)

## 🏗️ Kurulum

### Gereksinimler
```bash
pip install -r requirements.txt
```

### Yapılandırma
1. `env.example` dosyasını `.env` olarak kopyalayın
2. Google Places API anahtarınızı `.env` dosyasına ekleyin
3. Uygulamayı çalıştırın:

```bash
streamlit run streamlit_app.py
```

## 📁 Proje Yapısı

```
AdsGenius/
├── 📁 data/                    # Veri dosyaları
├── 📁 pages/                   # Streamlit sayfaları
├── streamlit_app.py           # Ana dashboard
├── utils.py                   # Core data engine
├── config.py                  # API anahtarları
├── env.example                # Environment variables template
└── requirements.txt           # Python bağımlılıkları
```

## 🎯 Ana Bileşenler

### 1. Core Data Engine (`utils.py`)
- Google Places API entegrasyonu
- Haversine mesafe hesaplama
- Competitive Pressure Score (CPS) algoritması
- Targeting Priority Index (TPI) hesaplama

### 2. Geospatial Strategy (`pages/1_Competitive_Map.py`)
- Interactive Folium haritası
- Gerçek reklam durumu marker'ları
- Acil hizmet işletmeleri özel işaretleme
- TPI HeatMap overlay

### 3. Optimization Simulator (`pages/2_Optimization_Simulator.py`)
- Bid Multiplier Test + Monte Carlo
- Negative Keyword Impact analizi
- Günlük net kar tahminleme

## 📊 İstatistikler

- **Toplam işletme**: 162
- **Reklam veren**: 50 (%31)
- **Acil hizmet veren**: 75 (%46)
- **Fırsat işletmeleri**: 48 (%64)

## 🔧 Teknolojiler

- **Streamlit**: Web uygulaması framework
- **Folium**: Interactive haritalar
- **Plotly**: Gelişmiş visualizasyonlar
- **Pandas/NumPy**: Veri işleme
- **Google Places API**: Gerçek zamanlı veri

## 🚀 Deployment

### Streamlit Cloud
1. GitHub repository'nizi Streamlit Cloud'a bağlayın
2. Environment variables ekleyin:
   ```
   GOOGLE_PLACES_API_KEY = your_api_key_here
   ```
3. Deploy edin

### Heroku
1. Procfile zaten hazır
2. Environment variables ekleyin
3. Deploy edin

## 📝 Lisans

Bu proje MIT lisansı altında lisanslanmıştır.

## 🤝 Katkıda Bulunma

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/AmazingFeature`)
3. Commit yapın (`git commit -m 'Add some AmazingFeature'`)
4. Push yapın (`git push origin feature/AmazingFeature`)
5. Pull Request oluşturun

## 📞 İletişim

Proje hakkında sorularınız için issue açabilirsiniz.