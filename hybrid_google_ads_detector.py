#!/usr/bin/env python3
"""
Hybrid Google Ads Detection System
3 seviyeli veri toplama sistemi
"""

import requests
import pandas as pd
import time
import json
import re
from urllib.parse import urlparse, urljoin
import random
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

class HybridGoogleAdsDetector:
    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'tr-TR,tr;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        self.session.headers.update(self.headers)
        
        # Google Ads göstergeleri
        self.google_ads_indicators = [
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
            'googleads.g.doubleclick.net',
            'googlesyndication.com',
            'googleadservices.com'
        ]
        
        # Rate limiting
        self.request_count = 0
        self.max_requests_per_minute = 15
        
    def random_delay(self, min_delay=1, max_delay=3):
        """Random bekleme süresi"""
        delay = random.uniform(min_delay, max_delay)
        print(f"    Waiting {delay:.1f} seconds...")
        time.sleep(delay)
        
    def rotate_user_agent(self):
        """User-Agent rotation"""
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15'
        ]
        self.session.headers['User-Agent'] = random.choice(user_agents)
        
    def make_request(self, url, params=None):
        """Güvenli HTTP isteği"""
        self.request_count += 1
        
        # Rate limiting
        if self.request_count % self.max_requests_per_minute == 0:
            print(f"    Rate limit: waiting 60 seconds...")
            time.sleep(60)
        
        # User-Agent rotation
        if self.request_count % 5 == 0:
            self.rotate_user_agent()
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            print(f"    Request error: {e}")
            return None
    
    # SEVIYE 1: Rating + Review Analizi (mevcut veriler)
    def level1_rating_review_analysis(self, business_name, rating, review_count):
        """Seviye 1: Rating + Review analizi"""
        print(f"    Level 1: Rating + Review Analysis")
        
        # Yüksek rating ve review sayısı = reklam verme ihtimali yüksek
        if rating >= 4.0 and review_count >= 50:
            return True, 'high', 'High rating (4.0+) and many reviews (50+)'
        elif rating >= 3.5 and review_count >= 20:
            return True, 'medium', 'Good rating (3.5+) and decent reviews (20+)'
        elif rating >= 3.0 and review_count >= 10:
            return True, 'low', 'Average rating (3.0+) and some reviews (10+)'
        else:
            return False, 'low', 'Low rating or few reviews'
    
    # SEVIYE 2: Website Google Ads Kodu Kontrolü
    def level2_website_ads_check(self, business_website):
        """Seviye 2: Website Google Ads kodu kontrolü"""
        print(f"    Level 2: Website Ads Code Check")
        
        if not business_website or business_website == 'N/A' or business_website == '':
            return False, 'low', 'No website available'
        
        # Website'e git
        response = self.make_request(business_website)
        if not response:
            return False, 'low', 'Website not accessible'
        
        content = response.text.lower()
        
        # Google Ads göstergelerini ara
        found_indicators = []
        for indicator in self.google_ads_indicators:
            if indicator in content:
                found_indicators.append(indicator)
        
        if found_indicators:
            confidence = 'high' if len(found_indicators) >= 3 else 'medium'
            return True, confidence, f'Found Google Ads codes: {", ".join(found_indicators[:3])}'
        else:
            return False, 'low', 'No Google Ads codes found'
    
    # SEVIYE 3: Google Search "Sponsored" Tespit
    def level3_google_search_ads_check(self, business_name):
        """Seviye 3: Google Search'te reklam kontrolü"""
        print(f"    Level 3: Google Search Ads Check")
        
        # Business name ile Google Search
        search_query = business_name.replace(' ', '+')
        search_url = f"https://www.google.com/search?q={search_query}&gl=tr&hl=tr"
        
        response = self.make_request(search_url)
        if not response:
            return False, 'low', 'Google search not accessible'
        
        content = response.text.lower()
        
        # Google Ads göstergeleri
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
        found_indicators = []
        for indicator in ads_indicators:
            if indicator in content:
                found_indicators.append(indicator)
        
        if found_indicators:
            # "Sponsored" etiketli sonuç sayısını say
            sponsored_count = content.count('sponsored')
            confidence = 'high' if sponsored_count >= 2 else 'medium'
            return True, confidence, f'Found ads indicators: {", ".join(found_indicators[:3])} (Sponsored count: {sponsored_count})'
        else:
            return False, 'low', 'No ads indicators found in search results'
    
    def comprehensive_ads_detection(self, business_name, business_website, rating, review_count):
        """Kapsamlı reklam tespit sistemi"""
        print(f"  Comprehensive analysis for: {business_name}")
        
        results = {
            'business_name': business_name,
            'website': business_website,
            'rating': rating,
            'review_count': review_count,
            'level1_result': False,
            'level1_confidence': 'low',
            'level1_reason': '',
            'level2_result': False,
            'level2_confidence': 'low',
            'level2_reason': '',
            'level3_result': False,
            'level3_confidence': 'low',
            'level3_reason': '',
            'total_score': 0,
            'final_confidence': 'low',
            'final_has_ads': False
        }
        
        # Seviye 1: Rating + Review analizi
        level1_result, level1_confidence, level1_reason = self.level1_rating_review_analysis(
            business_name, rating, review_count
        )
        results['level1_result'] = level1_result
        results['level1_confidence'] = level1_confidence
        results['level1_reason'] = level1_reason
        
        # Seviye 2: Website Google Ads kodu kontrolü
        level2_result, level2_confidence, level2_reason = self.level2_website_ads_check(business_website)
        results['level2_result'] = level2_result
        results['level2_confidence'] = level2_confidence
        results['level2_reason'] = level2_reason
        
        # Seviye 3: Google Search reklam kontrolü
        level3_result, level3_confidence, level3_reason = self.level3_google_search_ads_check(business_name)
        results['level3_result'] = level3_result
        results['level3_confidence'] = level3_confidence
        results['level3_reason'] = level3_reason
        
        # Toplam skor hesapla
        total_score = sum([level1_result, level2_result, level3_result])
        results['total_score'] = total_score
        
        # Final confidence hesapla
        if total_score >= 3:
            results['final_confidence'] = 'very_high'
        elif total_score >= 2:
            results['final_confidence'] = 'high'
        elif total_score >= 1:
            results['final_confidence'] = 'medium'
        else:
            results['final_confidence'] = 'low'
        
        # Final decision
        results['final_has_ads'] = total_score >= 1
        
        print(f"    Level 1 (Rating): {level1_result} ({level1_confidence}) - {level1_reason}")
        print(f"    Level 2 (Website): {level2_result} ({level2_confidence}) - {level2_reason}")
        print(f"    Level 3 (Search): {level3_result} ({level3_confidence}) - {level3_reason}")
        print(f"    Total Score: {total_score}/3")
        print(f"    Final: {results['final_has_ads']} (confidence: {results['final_confidence']})")
        
        return results
    
    def analyze_csv_businesses(self, csv_file, output_file, sample_size=None):
        """CSV dosyasındaki işletmeleri analiz et"""
        print(f"Loading CSV file: {csv_file}")
        
        # CSV'yi yükle
        df = pd.read_csv(csv_file, encoding='utf-8-sig')
        
        # Sample size belirtilmişse sadece o kadar işletme analiz et
        if sample_size:
            df = df.head(sample_size)
            print(f"Analyzing {len(df)} businesses (sample size: {sample_size})...")
        else:
            print(f"Analyzing {len(df)} businesses...")
        
        # Yeni sütunlar ekle
        df['level1_result'] = False
        df['level1_confidence'] = 'low'
        df['level1_reason'] = ''
        df['level2_result'] = False
        df['level2_confidence'] = 'low'
        df['level2_reason'] = ''
        df['level3_result'] = False
        df['level3_confidence'] = 'low'
        df['level3_reason'] = ''
        df['total_score'] = 0
        df['final_confidence'] = 'low'
        df['final_has_ads'] = False
        
        # Her işletme için analiz et
        for idx, row in df.iterrows():
            business_name = row.get('name', '')
            business_website = row.get('website', '')
            rating = row.get('rating', 0)
            review_count = row.get('user_ratings_total', 0)
            
            if business_name:
                print(f"\n({idx+1}/{len(df)}) Analyzing: {business_name}")
                
                # Kapsamlı analiz
                analysis_result = self.comprehensive_ads_detection(
                    business_name, business_website, rating, review_count
                )
                
                # Sonuçları DataFrame'e kaydet
                for key, value in analysis_result.items():
                    if key in df.columns:
                        df.at[idx, key] = value
                
                # Rate limiting
                self.random_delay(1, 2)
        
        # Güncellenmiş CSV'yi kaydet
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
        
        print(f"\nAnalysis completed!")
        print(f"Results saved to: {output_file}")
        
        # İstatistikler
        final_ads_count = df['final_has_ads'].sum()
        avg_score = df['total_score'].mean()
        
        print(f"\nHybrid Analysis Statistics:")
        print(f"- Total businesses analyzed: {len(df)}")
        print(f"- Final ads advertisers: {final_ads_count}")
        print(f"- Percentage: {(final_ads_count/len(df)*100):.1f}%")
        print(f"- Average score: {avg_score:.2f}/3")
        
        # Confidence dağılımı
        confidence_counts = df['final_confidence'].value_counts()
        print(f"\nFinal Confidence Distribution:")
        for confidence, count in confidence_counts.items():
            print(f"- {confidence}: {count}")
        
        # Score dağılımı
        score_counts = df['total_score'].value_counts()
        print(f"\nScore Distribution:")
        for score, count in score_counts.items():
            print(f"- Score {score}: {count}")
        
        # Seviye bazında istatistikler
        level1_count = df['level1_result'].sum()
        level2_count = df['level2_result'].sum()
        level3_count = df['level3_result'].sum()
        
        print(f"\nLevel-wise Statistics:")
        print(f"- Level 1 (Rating): {level1_count} businesses")
        print(f"- Level 2 (Website): {level2_count} businesses")
        print(f"- Level 3 (Search): {level3_count} businesses")
        
        return df

def main():
    print("Hybrid Google Ads Detection System")
    print("3-Level Comprehensive Analysis")
    print("=" * 50)
    
    detector = HybridGoogleAdsDetector()
    
    print("\nOptions:")
    print("1. Test with 5 businesses (quick test)")
    print("2. Test with 20 businesses (medium)")
    print("3. Test with 50 businesses (comprehensive)")
    print("4. Test with all 196 businesses (full analysis)")
    
    choice = input("\nEnter your choice (1-4): ")
    
    csv_file = 'data/istanbul_antique_silver_dealers.csv'
    
    if choice == '1':
        output_file = 'data/istanbul_antique_silver_hybrid_analysis_5.csv'
        detector.analyze_csv_businesses(csv_file, output_file, sample_size=5)
    elif choice == '2':
        output_file = 'data/istanbul_antique_silver_hybrid_analysis_20.csv'
        detector.analyze_csv_businesses(csv_file, output_file, sample_size=20)
    elif choice == '3':
        output_file = 'data/istanbul_antique_silver_hybrid_analysis_50.csv'
        detector.analyze_csv_businesses(csv_file, output_file, sample_size=50)
    elif choice == '4':
        output_file = 'data/istanbul_antique_silver_hybrid_analysis_full.csv'
        detector.analyze_csv_businesses(csv_file, output_file)
    else:
        print("Invalid choice. Exiting...")

if __name__ == "__main__":
    main()

