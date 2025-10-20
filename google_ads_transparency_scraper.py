#!/usr/bin/env python3
"""
Google Ads Transparency Center Scraper
İstanbul'daki reklam verenlerini çek
"""

import requests
import pandas as pd
import time
import json
import re
from urllib.parse import urljoin, urlparse
import random
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class GoogleAdsTransparencyScraper:
    def __init__(self):
        self.session = requests.Session()
        self.base_url = "https://adstransparency.google.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'tr-TR,tr;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        }
        self.session.headers.update(self.headers)
        
        # Antika ve gümüşçü anahtar kelimeleri
        self.antique_keywords = [
            'antika', 'antique', 'vintage', 'eski', 'koleksiyon', 'mezat',
            'gümüş', 'silver', 'gümüşçü', 'gümüş takı', 'gümüş ev eşyası',
            'gümüş aksesuar', 'gümüş yemek takımı', 'gümüş çatal bıçak'
        ]
        
        # Rate limiting için
        self.request_count = 0
        self.max_requests_per_minute = 10
        
    def random_delay(self, min_delay=3, max_delay=8):
        """Random bekleme süresi"""
        delay = random.uniform(min_delay, max_delay)
        print(f"  Waiting {delay:.1f} seconds...")
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
            print(f"  Rate limit: waiting 60 seconds...")
            time.sleep(60)
        
        # User-Agent rotation
        if self.request_count % 5 == 0:
            self.rotate_user_agent()
        
        try:
            response = self.session.get(url, params=params, timeout=15)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            print(f"  Request error: {e}")
            return None
    
    def search_istanbul_advertisers(self, keyword):
        """İstanbul'daki reklam verenlerini ara"""
        print(f"  Searching for: {keyword}")
        
        # Google Ads Transparency Center search URL
        search_url = f"{self.base_url}/search"
        
        params = {
            'q': keyword,
            'region': 'TR',  # Türkiye
            'ad_type': 'ALL',
            'date_range': 'ALL_TIME'
        }
        
        response = self.make_request(search_url, params)
        if not response:
            return []
        
        # Sayfa içeriğini analiz et
        content = response.text
        
        # JSON verilerini çıkar
        advertisers = self.extract_advertisers_from_content(content, keyword)
        
        return advertisers
    
    def extract_advertisers_from_content(self, content, keyword):
        """Sayfa içeriğinden reklam veren bilgilerini çıkar"""
        advertisers = []
        
        # JSON-LD structured data ara
        json_pattern = r'<script type="application/ld\+json">(.*?)</script>'
        json_matches = re.findall(json_pattern, content, re.DOTALL)
        
        for json_str in json_matches:
            try:
                data = json.loads(json_str)
                if self.is_antique_silver_related(data, keyword):
                    advertisers.append(data)
            except json.JSONDecodeError:
                continue
        
        # HTML içeriğinden reklam veren bilgilerini çıkar
        html_advertisers = self.extract_from_html(content, keyword)
        advertisers.extend(html_advertisers)
        
        return advertisers
    
    def is_antique_silver_related(self, data, keyword):
        """Veri antika/gümüşçü ile ilgili mi kontrol et"""
        if not isinstance(data, dict):
            return False
        
        # Metin içeriğini kontrol et
        text_content = str(data).lower()
        
        for antique_keyword in self.antique_keywords:
            if antique_keyword in text_content:
                return True
        
        return False
    
    def extract_from_html(self, content, keyword):
        """HTML içeriğinden reklam veren bilgilerini çıkar"""
        advertisers = []
        
        # Reklam veren isimlerini ara
        advertiser_pattern = r'<div[^>]*class="[^"]*advertiser[^"]*"[^>]*>([^<]+)</div>'
        advertiser_matches = re.findall(advertiser_pattern, content, re.IGNORECASE)
        
        for advertiser_name in advertiser_matches:
            if self.is_antique_silver_related({'name': advertiser_name}, keyword):
                advertisers.append({
                    'name': advertiser_name.strip(),
                    'keyword': keyword,
                    'source': 'html_extraction',
                    'timestamp': datetime.now().isoformat()
                })
        
        # Reklam metinlerini ara
        ad_text_pattern = r'<div[^>]*class="[^"]*ad-text[^"]*"[^>]*>([^<]+)</div>'
        ad_text_matches = re.findall(ad_text_pattern, content, re.IGNORECASE)
        
        for ad_text in ad_text_matches:
            if self.is_antique_silver_related({'text': ad_text}, keyword):
                advertisers.append({
                    'ad_text': ad_text.strip(),
                    'keyword': keyword,
                    'source': 'ad_text_extraction',
                    'timestamp': datetime.now().isoformat()
                })
        
        return advertisers
    
    def get_advertiser_details(self, advertiser_name):
        """Reklam veren detaylarını çek"""
        print(f"    Getting details for: {advertiser_name}")
        
        # Advertiser detail URL
        detail_url = f"{self.base_url}/advertiser/{advertiser_name}"
        
        response = self.make_request(detail_url)
        if not response:
            return {}
        
        content = response.text
        
        # Detay bilgilerini çıkar
        details = self.extract_advertiser_details(content)
        details['name'] = advertiser_name
        
        return details
    
    def extract_advertiser_details(self, content):
        """Reklam veren detaylarını çıkar"""
        details = {}
        
        # Reklam sayısı
        ad_count_pattern = r'(\d+)\s+ads?'
        ad_count_match = re.search(ad_count_pattern, content)
        if ad_count_match:
            details['ad_count'] = int(ad_count_match.group(1))
        
        # Harcama tahmini
        spend_pattern = r'[\$€₺](\d+(?:,\d{3})*(?:\.\d{2})?)'
        spend_matches = re.findall(spend_pattern, content)
        if spend_matches:
            details['estimated_spend'] = spend_matches[0]
        
        # Reklam türleri
        ad_types = []
        if 'search' in content.lower():
            ad_types.append('Search')
        if 'display' in content.lower():
            ad_types.append('Display')
        if 'video' in content.lower():
            ad_types.append('Video')
        
        if ad_types:
            details['ad_types'] = ', '.join(ad_types)
        
        return details
    
    def scrape_istanbul_antique_silver_advertisers(self):
        """İstanbul'daki antika/gümüşçü reklam verenlerini çek"""
        print("Starting Google Ads Transparency Center Scraping")
        print("=" * 60)
        
        all_advertisers = []
        
        # Arama terimleri
        search_terms = [
            'antika istanbul',
            'antique istanbul',
            'gümüş istanbul',
            'silver istanbul',
            'vintage istanbul',
            'antika mağazası istanbul',
            'gümüşçü istanbul',
            'antika satış istanbul',
            'gümüş takı istanbul',
            'antika koleksiyon istanbul'
        ]
        
        for i, term in enumerate(search_terms):
            print(f"\nSearch {i+1}/{len(search_terms)}: {term}")
            
            # Reklam verenleri ara
            advertisers = self.search_istanbul_advertisers(term)
            
            if advertisers:
                print(f"  Found {len(advertisers)} advertisers")
                
                # Her reklam veren için detay çek
                for advertiser in advertisers:
                    if 'name' in advertiser:
                        details = self.get_advertiser_details(advertiser['name'])
                        advertiser.update(details)
                    
                    all_advertisers.append(advertiser)
                    
                    # Rate limiting
                    self.random_delay(2, 5)
            else:
                print(f"  No advertisers found")
            
            # Arama arası bekleme
            self.random_delay(5, 10)
        
        return all_advertisers
    
    def save_to_csv(self, advertisers, filename):
        """Reklam verenleri CSV'ye kaydet"""
        if not advertisers:
            print("No advertisers to save")
            return
        
        df = pd.DataFrame(advertisers)
        
        # Sütunları düzenle
        columns_to_keep = [
            'name', 'keyword', 'source', 'ad_count', 'estimated_spend',
            'ad_types', 'timestamp'
        ]
        
        # Mevcut sütunları kontrol et
        available_columns = [col for col in columns_to_keep if col in df.columns]
        df = df[available_columns]
        
        # CSV'ye kaydet
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        
        print(f"Saved {len(df)} advertisers to {filename}")
        
        # İstatistikler
        print(f"\nScraping Statistics:")
        print(f"- Total advertisers found: {len(df)}")
        print(f"- Unique advertisers: {df['name'].nunique()}")
        
        if 'ad_count' in df.columns:
            total_ads = df['ad_count'].sum()
            print(f"- Total ads: {total_ads}")
        
        if 'ad_types' in df.columns:
            ad_types = df['ad_types'].value_counts()
            print(f"- Ad types distribution:")
            for ad_type, count in ad_types.items():
                print(f"  * {ad_type}: {count}")

def main():
    print("Google Ads Transparency Center Scraper")
    print("İstanbul Antika & Gümüşçü Reklam Verenleri")
    print("=" * 60)
    
    scraper = GoogleAdsTransparencyScraper()
    
    try:
        # İstanbul'daki antika/gümüşçü reklam verenlerini çek
        advertisers = scraper.scrape_istanbul_antique_silver_advertisers()
        
        # CSV'ye kaydet
        output_file = 'data/istanbul_antique_silver_google_ads_advertisers.csv'
        scraper.save_to_csv(advertisers, output_file)
        
        print(f"\nScraping completed successfully!")
        print(f"Results saved to: {output_file}")
        
    except KeyboardInterrupt:
        print("\nScraping interrupted by user")
    except Exception as e:
        print(f"\nError during scraping: {e}")

if __name__ == "__main__":
    main()
