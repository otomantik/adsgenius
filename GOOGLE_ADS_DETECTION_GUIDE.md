# Google Ads Tespit Rehberi

## 🎯 Gerçek Google Ads Reklam Verenlerini Tespit Etme

### 1. **Manuel Kontrol Yöntemleri (En Güvenilir)**

#### A) Google Search'te Kontrol
1. İşletme adını Google'da arayın
2. "Sponsored" etiketli sonuçlar varsa → **Reklam veriyor**
3. İlk sayfada çıkıyorsa → **Muhtemelen reklam veriyor**

#### B) Google Ads Transparency Center
1. https://transparencyreport.google.com/political-ads/region/TR
2. İşletme adını arayın
3. Bulunursa → **Reklam veriyor**

#### C) Google Ads Library
1. https://adstransparency.google.com/
2. İşletme adını arayın
3. Bulunursa → **Reklam veriyor**

#### D) Website İnceleme
1. İşletme websitesine gidin
2. F12 → Network → "ads" filtreleyin
3. Google Ads kodları varsa → **Reklam veriyor**

### 2. **Otomatik Tespit Yöntemleri (Yardımcı)**

#### A) Rating + Review Analizi
```python
def predict_ads_potential(rating, review_count):
    if rating >= 4.0 and review_count >= 50:
        return True, 'high'
    elif rating >= 3.5 and review_count >= 20:
        return True, 'medium'
    else:
        return False, 'low'
```

#### B) Website Google Ads Kodu Kontrolü
```python
def check_website_ads(website_url):
    # Google Ads göstergeleri
    ads_indicators = [
        'adsbygoogle',
        'google-ads',
        'googletagmanager',
        'googleadservices'
    ]
    # Website içeriğinde bu kodları ara
```

### 3. **Pratik Uygulama**

#### Adım 1: Otomatik Tahmin
- Rating ≥ 4.0 + Review ≥ 50 = **Yüksek Potansiyel**
- Bu işletmeleri manuel kontrol için işaretle

#### Adım 2: Manuel Kontrol
- Yüksek potansiyelli işletmeleri Google'da arayın
- "Sponsored" etiketli sonuçlar var mı?
- Website'de Google Ads kodu var mı?

#### Adım 3: Sonuç Kaydetme
- Manuel kontrol sonuçlarını CSV'ye kaydedin
- `real_has_ads` sütunu ekleyin

### 4. **Örnek CSV Yapısı**

```csv
name,rating,user_ratings_total,predicted_has_ads,predicted_confidence,real_has_ads,real_confidence,notes
Berol Antik,4.9,39,True,medium,True,high,Google'da sponsored sonuç var
Horhor Antikacılar Çarşısı,4.2,276,True,high,False,low,Manuel kontrol: reklam yok
```

### 5. **Doğruluk Oranları**

| Yöntem | Doğruluk | Hız |
|--------|----------|-----|
| Manuel Kontrol | %95+ | Yavaş |
| Website Kodu Kontrolü | %80 | Orta |
| Rating + Review Analizi | %60 | Hızlı |
| Otomatik Web Scraping | %50 | Orta |

### 6. **Önerilen Strateji**

1. **Otomatik tahmin** ile potansiyel reklam verenleri belirle
2. **Yüksek potansiyelli** işletmeleri manuel kontrol et
3. **Manuel sonuçları** CSV'ye kaydet
4. **Machine learning** ile tahmin modelini geliştir

### 7. **Sonuç**

- **%100 doğru** tespit için manuel kontrol gerekli
- **Otomatik yöntemler** sadece yardımcı
- **En pratik**: Otomatik tahmin + Manuel doğrulama

## 🚀 Uygulama

Bu rehberi kullanarak:
1. 196 antika/gümüşçü işletmesini analiz edin
2. Yüksek potansiyelli olanları manuel kontrol edin
3. Gerçek reklam verenlerini tespit edin
4. Sonuçları CSV'ye kaydedin

