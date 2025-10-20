#!/usr/bin/env python3
"""
Gerçek Google Ads reklam verenlerini tespit et
Google Ads Transparency Center API kullanarak
"""

import requests
import pandas as pd
import time
import json
from config import GOOGLE_PLACES_API_KEY
import urllib.parse

def check_google_ads_transparency(business_name, business_domain=None):
    """
    Google Ads Transparency Center'da reklam kontrolü
    """
    # Google Ads Transparency Center API endpoint
    # Bu API gerçek reklam verenlerini gösterir
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    # Business name ile arama
    search_query = business_name.replace(' ', '+')
    
    # Google Ads Transparency Center URL
    transparency_url = f"https://transparencyreport.google.com/political-ads/region/TR"
    
    # Alternatif: Google Ads Library (daha detaylı)
    ads_library_url = "https://adstransparency.google.com/"
    
    try:
        # Basit HTTP isteği ile kontrol
        response = requests.get(transparency_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            # Sayfa içeriğinde business name arama
            content = response.text.lower()
            business_lower = business_name.lower()
            
            # Eğer sayfa içeriğinde business name varsa, reklam veriyor olabilir
            if business_lower in content:
                return True, 'found_in_transparency'
            
        return False, 'not_found'
        
    except Exception as e:
        print(f"Transparency check error for {business_name}: {e}")
        return False, 'error'

def check_google_search_ads(business_name):
    """
    Google Search'te reklam kontrolü
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    # Business name ile Google Search
    search_query = urllib.parse.quote_plus(business_name)
    search_url = f"https://www.google.com/search?q={search_query}"
    
    try:
        response = requests.get(search_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            content = response.text.lower()
            
            # Google Ads göstergeleri
            ads_indicators = [
                'sponsored',
                'advertisement',
                'reklam',
                'sponsorlu',
                'adsbygoogle',
                'google-ads'
            ]
            
            # Eğer sayfa içeriğinde ads göstergeleri varsa
            ads_found = any(indicator in content for indicator in ads_indicators)
            
            if ads_found:
                return True, 'ads_detected_in_search'
            
        return False, 'no_ads_in_search'
        
    except Exception as e:
        print(f"Search ads check error for {business_name}: {e}")
        return False, 'error'

def check_website_for_ads(business_website):
    """
    Business website'inde Google Ads kontrolü
    """
    if not business_website or business_website == 'N/A':
        return False, 'no_website'
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        # Website'e git
        response = requests.get(business_website, headers=headers, timeout=10)
        
        if response.status_code == 200:
            content = response.text.lower()
            
            # Google Ads göstergeleri
            ads_indicators = [
                'adsbygoogle',
                'google-ads',
                'googletagmanager',
                'google-analytics',
                'gtag',
                'googleadservices'
            ]
            
            # Eğer website'de Google Ads kodları varsa
            ads_found = any(indicator in content for indicator in ads_indicators)
            
            if ads_found:
                return True, 'ads_code_found'
            
        return False, 'no_ads_code'
        
    except Exception as e:
        print(f"Website ads check error for {business_website}: {e}")
        return False, 'error'

def detect_real_google_ads(business_name, business_website=None):
    """
    Gerçek Google Ads reklam verenlerini tespit et
    """
    print(f"Checking {business_name} for real Google Ads...")
    
    results = {
        'business_name': business_name,
        'transparency_center': False,
        'search_ads': False,
        'website_ads': False,
        'confidence': 'low'
    }
    
    # 1. Google Ads Transparency Center kontrolü
    transparency_result, transparency_reason = check_google_ads_transparency(business_name)
    results['transparency_center'] = transparency_result
    results['transparency_reason'] = transparency_reason
    
    # 2. Google Search'te reklam kontrolü
    search_result, search_reason = check_google_search_ads(business_name)
    results['search_ads'] = search_result
    results['search_reason'] = search_reason
    
    # 3. Website'de Google Ads kontrolü
    website_result, website_reason = check_website_for_ads(business_website)
    results['website_ads'] = website_result
    results['website_reason'] = website_reason
    
    # Confidence hesapla
    positive_checks = sum([transparency_result, search_result, website_result])
    
    if positive_checks >= 2:
        results['confidence'] = 'high'
    elif positive_checks == 1:
        results['confidence'] = 'medium'
    else:
        results['confidence'] = 'low'
    
    # Final decision
    results['has_real_ads'] = positive_checks >= 1
    
    print(f"  Transparency: {transparency_result} ({transparency_reason})")
    print(f"  Search Ads: {search_result} ({search_reason})")
    print(f"  Website Ads: {website_result} ({website_reason})")
    print(f"  Final: {results['has_real_ads']} (confidence: {results['confidence']})")
    
    return results

def update_csv_with_real_ads(csv_file, output_file):
    """
    CSV dosyasındaki işletmeleri gerçek Google Ads verileri ile güncelle
    """
    print(f"Loading CSV file: {csv_file}")
    
    # CSV'yi yükle
    df = pd.read_csv(csv_file, encoding='utf-8-sig')
    
    print(f"Checking {len(df)} businesses for real Google Ads...")
    
    # Yeni sütunlar ekle
    df['real_has_ads'] = False
    df['real_ads_confidence'] = 'low'
    df['transparency_center'] = False
    df['search_ads'] = False
    df['website_ads'] = False
    
    # Her işletme için kontrol et
    for idx, row in df.iterrows():
        business_name = row.get('name', '')
        business_website = row.get('website', '')
        
        if business_name:
            print(f"\n({idx+1}/{len(df)}) Checking: {business_name}")
            
            # Gerçek Google Ads kontrolü
            ads_result = detect_real_google_ads(business_name, business_website)
            
            # Sonuçları DataFrame'e kaydet
            df.at[idx, 'real_has_ads'] = ads_result['has_real_ads']
            df.at[idx, 'real_ads_confidence'] = ads_result['confidence']
            df.at[idx, 'transparency_center'] = ads_result['transparency_center']
            df.at[idx, 'search_ads'] = ads_result['search_ads']
            df.at[idx, 'website_ads'] = ads_result['website_ads']
            
            # API rate limit için bekle
            time.sleep(2)
    
    # Güncellenmiş CSV'yi kaydet
    df.to_csv(output_file, index=False, encoding='utf-8-sig')
    
    print(f"\nUpdated CSV saved to: {output_file}")
    
    # İstatistikler
    real_ads_count = df['real_has_ads'].sum()
    print(f"\nReal Google Ads Statistics:")
    print(f"- Total businesses: {len(df)}")
    print(f"- Real Google Ads advertisers: {real_ads_count}")
    print(f"- Percentage: {(real_ads_count/len(df)*100):.1f}%")
    
    # Confidence dağılımı
    confidence_counts = df['real_ads_confidence'].value_counts()
    print(f"\nConfidence Distribution:")
    for confidence, count in confidence_counts.items():
        print(f"- {confidence}: {count}")
    
    return df

def main():
    print("Real Google Ads Detection Script")
    print("=" * 50)
    
    # Test için birkaç işletme
    test_businesses = [
        {"name": "Berol Antik", "website": "http://www.berolantik.com/"},
        {"name": "Horhor Antikacılar Çarşısı", "website": None},
        {"name": "Fener Antik Mezat", "website": None},
        {"name": "Silver Group", "website": None},
        {"name": "Coşar Silver - Wholesale", "website": None}
    ]
    
    print("Testing with sample businesses:")
    for business in test_businesses:
        result = detect_real_google_ads(business['name'], business['website'])
        print("-" * 30)
    
    # Tam CSV güncelleme (isteğe bağlı)
    user_input = input("\nDo you want to update the full CSV file? (y/n): ")
    if user_input.lower() == 'y':
        csv_file = 'data/istanbul_antique_silver_dealers.csv'
        output_file = 'data/istanbul_antique_silver_dealers_real_ads.csv'
        update_csv_with_real_ads(csv_file, output_file)

if __name__ == "__main__":
    main()
