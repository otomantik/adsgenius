#!/usr/bin/env python3
"""
İstanbul'daki Antika ve Gümüşçüleri Google Places API ile çek
"""

import requests
import pandas as pd
import time
import json
from config import GOOGLE_PLACES_API_KEY

def search_places_antique_silver(query, location, radius=50000):
    """
    Google Places API ile antika/gümüşçü arama - Nearby Search kullan
    """
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    
    # Location'ı lat,lng formatına çevir
    lat, lng = location.split(',')
    
    params = {
        'location': f"{lat},{lng}",
        'radius': radius,
        'keyword': query,
        'key': GOOGLE_PLACES_API_KEY,
        'language': 'tr'
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        print(f"Response status: {response.status_code}")
        print(f"Response text (first 200 chars): {response.text[:200]}")
        
        data = response.json()
        
        if data['status'] == 'OK':
            return data['results']
        else:
            print(f"API Error: {data['status']}")
            if 'error_message' in data:
                print(f"Error message: {data['error_message']}")
            return []
            
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        return []
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        print(f"Response text: {response.text if 'response' in locals() else 'No response'}")
        return []
    except Exception as e:
        print(f"Unexpected error: {e}")
        return []

def get_place_details(place_id):
    """
    Place ID ile detaylı bilgi çek
    """
    url = "https://maps.googleapis.com/maps/api/place/details/json"
    
    params = {
        'place_id': place_id,
        'fields': 'name,formatted_address,formatted_phone_number,website,rating,user_ratings_total,business_status,types,geometry',
        'key': GOOGLE_PLACES_API_KEY,
        'language': 'tr'
    }
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        if data['status'] == 'OK':
            return data['result']
        else:
            print(f"Details API Error: {data['status']}")
            return None
            
    except Exception as e:
        print(f"Details request error: {e}")
        return None

def detect_ads_potential(place_data):
    """
    Reklam verme potansiyelini tespit et
    """
    rating = place_data.get('rating', 0)
    review_count = place_data.get('user_ratings_total', 0)
    business_types = place_data.get('types', [])
    
    # Yüksek rating ve review sayısı = reklam verme ihtimali yüksek
    if rating >= 4.0 and review_count >= 50:
        return True, 'high'
    elif rating >= 3.5 and review_count >= 20:
        return True, 'medium'
    elif rating >= 3.0 and review_count >= 10:
        return True, 'low'
    else:
        return False, 'low'

def main():
    print("Antika ve Gümüşçü İşletmeleri Çekiliyor...")
    
    # İstanbul merkez koordinatları
    istanbul_center = "41.015137,28.978359"
    
    # Arama terimleri - basit İngilizce terimler
    search_queries = [
        "antique shop",
        "silver dealer",
        "antique furniture",
        "silver jewelry",
        "antique store",
        "silverware",
        "antique gallery",
        "jewelry store",
        "antique collection",
        "silver goods",
        "antique market",
        "gold silver",
        "antique dealer",
        "precious metals",
        "antique center"
    ]
    
    all_places = []
    seen_place_ids = set()
    
    for i, query in enumerate(search_queries):
        print(f"({i+1}/{len(search_queries)}) Aranıyor: {query}")
        
        places = search_places_antique_silver(query, istanbul_center)
        
        for place in places:
            place_id = place.get('place_id')
            
            if place_id and place_id not in seen_place_ids:
                seen_place_ids.add(place_id)
                
                # Detaylı bilgi çek
                details = get_place_details(place_id)
                
                if details:
                    # Reklam potansiyeli tespit et
                    has_ads, ads_confidence = detect_ads_potential(details)
                    
                    place_info = {
                        'place_id': place_id,
                        'name': details.get('name', ''),
                        'address': details.get('formatted_address', ''),
                        'latitude': details.get('geometry', {}).get('location', {}).get('lat', 0),
                        'longitude': details.get('geometry', {}).get('location', {}).get('lng', 0),
                        'rating': details.get('rating', 0),
                        'user_ratings_total': details.get('user_ratings_total', 0),
                        'business_status': details.get('business_status', 'OPERATIONAL'),
                        'types': ', '.join(details.get('types', [])),
                        'formatted_phone_number': details.get('formatted_phone_number', ''),
                        'website': details.get('website', ''),
                        'has_ads': has_ads,
                        'ads_confidence': ads_confidence,
                        'search_query': query
                    }
                    
                    all_places.append(place_info)
                    print(f"  + {place_info['name']} - Rating: {place_info['rating']} - Ads: {has_ads}")
                
                # API rate limit için bekle
                time.sleep(0.1)
        
        # Her arama sonrası kısa bekle
        time.sleep(1)
    
    # DataFrame oluştur
    if all_places:
        df = pd.DataFrame(all_places)
        
        # CSV'ye kaydet
        csv_filename = 'data/istanbul_antique_silver_dealers.csv'
        df.to_csv(csv_filename, index=False, encoding='utf-8-sig')
        
        print(f"\nToplam {len(df)} işletme bulundu!")
        print(f"Veriler {csv_filename} dosyasına kaydedildi.")
        
        # İstatistikler
        print(f"\nİstatistikler:")
        print(f"- Toplam işletme: {len(df)}")
        print(f"- Reklam veren (yüksek potansiyel): {len(df[df['has_ads'] == True])}")
        print(f"- Ortalama rating: {df['rating'].mean():.2f}")
        print(f"- En yüksek rating: {df['rating'].max():.2f}")
        
        # İlçe dağılımı
        print(f"\nİlçe Dağılımı:")
        if 'address' in df.columns:
            # Adreslerden ilçe çıkar
            df['district'] = df['address'].str.extract(r'([^,]+),?\s*İstanbul')
            district_counts = df['district'].value_counts().head(10)
            print(district_counts)
        
    else:
        print("Hiç işletme bulunamadı!")

if __name__ == "__main__":
    main()
