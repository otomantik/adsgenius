#!/usr/bin/env python3
"""
Gelişmiş Google Ads Tespit Sistemi
Gerçek Google Ads reklam verenlerini tespit et
"""

import requests
import pandas as pd
import time
import json
import re
from urllib.parse import urlparse, urljoin
import warnings
warnings.filterwarnings('ignore')

def check_google_ads_library(business_name):
    """
    Google Ads Library API kullanarak reklam kontrolü
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'application/json',
        'Accept-Language': 'tr-TR,tr;q=0.9,en;q=0.8'
    }
    
    # Google Ads Library URL
    ads_library_url = "https://adstransparency.google.com/"
    
    try:
        response = requests.get(ads_library_url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            # Sayfa içeriğinde business name arama
            content = response.text.lower()
            business_lower = business_name.lower()
            
            # Eğer sayfa içeriğinde business name varsa
            if business_lower in content:
                return True, 'found_in_ads_library'
            
        return False, 'not_found_in_library'
        
    except Exception as e:
        return False, f'error: {str(e)}'

def check_google_search_ads_advanced(business_name):
    """
    Gelişmiş Google Search reklam kontrolü
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'tr-TR,tr;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
    
    # Business name ile Google Search
    search_query = business_name.replace(' ', '+')
    search_url = f"https://www.google.com/search?q={search_query}&gl=tr&hl=tr"
    
    try:
        response = requests.get(search_url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            content = response.text.lower()
            
            # Google Ads göstergeleri (daha kapsamlı)
            ads_indicators = [
                'sponsored',
                'advertisement', 
                'reklam',
                'sponsorlu',
                'adsbygoogle',
                'google-ads',
                'advertisement',
                'promoted',
                'sponsored result',
                'ad result',
                'google ads',
                'adsense',
                'adwords'
            ]
            
            # Eğer sayfa içeriğinde ads göstergeleri varsa
            ads_found = any(indicator in content for indicator in ads_indicators)
            
            if ads_found:
                return True, 'ads_detected_in_search'
            
            # Ek kontrol: "Sponsored" etiketli sonuçlar
            sponsored_count = content.count('sponsored')
            if sponsored_count > 0:
                return True, f'sponsored_results_found: {sponsored_count}'
            
        return False, 'no_ads_in_search'
        
    except Exception as e:
        return False, f'error: {str(e)}'

def check_website_ads_advanced(business_website):
    """
    Gelişmiş website Google Ads kontrolü
    """
    if not business_website or business_website == 'N/A' or business_website == '':
        return False, 'no_website'
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'tr-TR,tr;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
    
    try:
        # Website'e git
        response = requests.get(business_website, headers=headers, timeout=15)
        
        if response.status_code == 200:
            content = response.text.lower()
            
            # Google Ads göstergeleri (daha kapsamlı)
            ads_indicators = [
                'adsbygoogle',
                'google-ads',
                'googletagmanager',
                'google-analytics',
                'gtag',
                'googleadservices',
                'doubleclick',
                'google ads',
                'adsense',
                'adwords',
                'google adsense',
                'google adwords',
                'google advertising',
                'google ads script',
                'adsbygoogle.js',
                'googleads.g.doubleclick.net'
            ]
            
            # Eğer website'de Google Ads kodları varsa
            ads_found = any(indicator in content for indicator in ads_indicators)
            
            if ads_found:
                # Hangi tür ads kodu bulunduğunu tespit et
                found_indicators = [indicator for indicator in ads_indicators if indicator in content]
                return True, f'ads_code_found: {found_indicators[0]}'
            
            # Ek kontrol: Google Tag Manager
            if 'googletagmanager' in content:
                return True, 'google_tag_manager_found'
            
        return False, 'no_ads_code'
        
    except Exception as e:
        return False, f'error: {str(e)}'

def check_facebook_ads(business_name, business_website=None):
    """
    Facebook Ads kontrolü
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    # Facebook Ads Library URL
    facebook_ads_url = "https://www.facebook.com/ads/library/"
    
    try:
        response = requests.get(facebook_ads_url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            content = response.text.lower()
            business_lower = business_name.lower()
            
            # Eğer sayfa içeriğinde business name varsa
            if business_lower in content:
                return True, 'found_in_facebook_ads'
            
        return False, 'not_found_in_facebook'
        
    except Exception as e:
        return False, f'error: {str(e)}'

def detect_comprehensive_ads(business_name, business_website=None):
    """
    Kapsamlı reklam tespit sistemi
    """
    print(f"Checking {business_name} for comprehensive ads...")
    
    results = {
        'business_name': business_name,
        'google_ads_library': False,
        'google_search_ads': False,
        'website_ads': False,
        'facebook_ads': False,
        'total_score': 0,
        'confidence': 'low'
    }
    
    # 1. Google Ads Library kontrolü
    library_result, library_reason = check_google_ads_library(business_name)
    results['google_ads_library'] = library_result
    results['library_reason'] = library_reason
    
    # 2. Google Search reklam kontrolü
    search_result, search_reason = check_google_search_ads_advanced(business_name)
    results['google_search_ads'] = search_result
    results['search_reason'] = search_reason
    
    # 3. Website Google Ads kontrolü
    website_result, website_reason = check_website_ads_advanced(business_website)
    results['website_ads'] = website_result
    results['website_reason'] = website_reason
    
    # 4. Facebook Ads kontrolü
    facebook_result, facebook_reason = check_facebook_ads(business_name, business_website)
    results['facebook_ads'] = facebook_result
    results['facebook_reason'] = facebook_reason
    
    # Score hesapla
    total_score = sum([library_result, search_result, website_result, facebook_result])
    results['total_score'] = total_score
    
    # Confidence hesapla
    if total_score >= 3:
        results['confidence'] = 'very_high'
    elif total_score >= 2:
        results['confidence'] = 'high'
    elif total_score >= 1:
        results['confidence'] = 'medium'
    else:
        results['confidence'] = 'low'
    
    # Final decision
    results['has_ads'] = total_score >= 1
    
    print(f"  Google Ads Library: {library_result} ({library_reason})")
    print(f"  Google Search Ads: {search_result} ({search_reason})")
    print(f"  Website Ads: {website_result} ({website_reason})")
    print(f"  Facebook Ads: {facebook_result} ({facebook_reason})")
    print(f"  Total Score: {total_score}/4")
    print(f"  Final: {results['has_ads']} (confidence: {results['confidence']})")
    
    return results

def update_csv_with_comprehensive_ads(csv_file, output_file, sample_size=None):
    """
    CSV dosyasındaki işletmeleri kapsamlı reklam verileri ile güncelle
    """
    print(f"Loading CSV file: {csv_file}")
    
    # CSV'yi yükle
    df = pd.read_csv(csv_file, encoding='utf-8-sig')
    
    # Sample size belirtilmişse sadece o kadar işletme kontrol et
    if sample_size:
        df = df.head(sample_size)
        print(f"Checking {len(df)} businesses (sample size: {sample_size})...")
    else:
        print(f"Checking {len(df)} businesses for comprehensive ads...")
    
    # Yeni sütunlar ekle
    df['comprehensive_has_ads'] = False
    df['comprehensive_ads_confidence'] = 'low'
    df['ads_total_score'] = 0
    df['google_ads_library'] = False
    df['google_search_ads'] = False
    df['website_ads'] = False
    df['facebook_ads'] = False
    
    # Her işletme için kontrol et
    for idx, row in df.iterrows():
        business_name = row.get('name', '')
        business_website = row.get('website', '')
        
        if business_name:
            print(f"\n({idx+1}/{len(df)}) Checking: {business_name}")
            
            # Kapsamlı reklam kontrolü
            ads_result = detect_comprehensive_ads(business_name, business_website)
            
            # Sonuçları DataFrame'e kaydet
            df.at[idx, 'comprehensive_has_ads'] = ads_result['has_ads']
            df.at[idx, 'comprehensive_ads_confidence'] = ads_result['confidence']
            df.at[idx, 'ads_total_score'] = ads_result['total_score']
            df.at[idx, 'google_ads_library'] = ads_result['google_ads_library']
            df.at[idx, 'google_search_ads'] = ads_result['google_search_ads']
            df.at[idx, 'website_ads'] = ads_result['website_ads']
            df.at[idx, 'facebook_ads'] = ads_result['facebook_ads']
            
            # API rate limit için bekle
            time.sleep(3)
    
    # Güncellenmiş CSV'yi kaydet
    df.to_csv(output_file, index=False, encoding='utf-8-sig')
    
    print(f"\nUpdated CSV saved to: {output_file}")
    
    # İstatistikler
    comprehensive_ads_count = df['comprehensive_has_ads'].sum()
    avg_score = df['ads_total_score'].mean()
    
    print(f"\nComprehensive Ads Statistics:")
    print(f"- Total businesses: {len(df)}")
    print(f"- Comprehensive ads advertisers: {comprehensive_ads_count}")
    print(f"- Percentage: {(comprehensive_ads_count/len(df)*100):.1f}%")
    print(f"- Average score: {avg_score:.2f}/4")
    
    # Confidence dağılımı
    confidence_counts = df['comprehensive_ads_confidence'].value_counts()
    print(f"\nConfidence Distribution:")
    for confidence, count in confidence_counts.items():
        print(f"- {confidence}: {count}")
    
    # Score dağılımı
    score_counts = df['ads_total_score'].value_counts()
    print(f"\nScore Distribution:")
    for score, count in score_counts.items():
        print(f"- Score {score}: {count}")
    
    return df

def main():
    print("Advanced Google Ads Detection Script")
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
        result = detect_comprehensive_ads(business['name'], business['website'])
        print("-" * 30)
    
    # Tam CSV güncelleme (isteğe bağlı)
    print("\nOptions:")
    print("1. Test with 10 businesses (quick)")
    print("2. Test with 50 businesses (medium)")
    print("3. Test with all businesses (slow)")
    print("4. Exit")
    
    choice = input("\nEnter your choice (1-4): ")
    
    if choice == '1':
        csv_file = 'data/istanbul_antique_silver_dealers.csv'
        output_file = 'data/istanbul_antique_silver_dealers_comprehensive_ads_10.csv'
        update_csv_with_comprehensive_ads(csv_file, output_file, sample_size=10)
    elif choice == '2':
        csv_file = 'data/istanbul_antique_silver_dealers.csv'
        output_file = 'data/istanbul_antique_silver_dealers_comprehensive_ads_50.csv'
        update_csv_with_comprehensive_ads(csv_file, output_file, sample_size=50)
    elif choice == '3':
        csv_file = 'data/istanbul_antique_silver_dealers.csv'
        output_file = 'data/istanbul_antique_silver_dealers_comprehensive_ads_full.csv'
        update_csv_with_comprehensive_ads(csv_file, output_file)
    else:
        print("Exiting...")

if __name__ == "__main__":
    main()

