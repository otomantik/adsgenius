"""
Core Data Engine for Marketing Intelligence Platform
Provides cached data generation and processing functions
"""

import pandas as pd
import numpy as np
import streamlit as st
from datetime import datetime, timedelta
from typing import Dict, Tuple
import math
import os
import requests
import time

# Try to import config, fall back to defaults if not available
try:
    from config import (
        GOOGLE_PLACES_API_KEY,
        CORE_CENTER_LAT,
        CORE_CENTER_LON,
        USE_REAL_PLACES_DATA,
        USE_CSV_PLACES_DATA,
        CSV_PLACES_FILE,
        MAX_PLACES_RESULTS
    )
except ImportError:
    # Default configuration if config.py doesn't exist
    GOOGLE_PLACES_API_KEY = None
    CORE_CENTER_LAT = 41.015137
    CORE_CENTER_LON = 28.978359
    USE_REAL_PLACES_DATA = False
    USE_CSV_PLACES_DATA = False
    CSV_PLACES_FILE = 'data/istanbul_all_batteries.csv'
    MAX_PLACES_RESULTS = 60


# ============================================================================
# DATA LOADING & CLEANING FUNCTIONS
# ============================================================================

def clean_numeric_value(value):
    """
    Clean numeric values from CSV - handle '--', '< 10', percentages, etc.
    
    Args:
        value: Raw value from CSV
    
    Returns:
        Float value or 0.0 if cannot be converted
    """
    if pd.isna(value) or value == '' or value == '--' or value == ' < 10' or value == '< 10':
        return 0.0
    
    if isinstance(value, str):
        # Remove spaces
        value = value.strip()
        
        # Handle percentage format (e.g., '10,50%')
        if '%' in value:
            value = value.replace('%', '').replace(',', '.').strip()
            try:
                return float(value) / 100
            except:
                return 0.0
        
        # Handle Turkish number format (comma as decimal)
        if ',' in value:
            value = value.replace('.', '').replace(',', '.')
        
        # Try to convert
        try:
            return float(value)
        except:
            return 0.0
    
    return float(value) if value else 0.0


def load_general_trend_csv(file_path: str = 'data/genel_trend_aylik.csv') -> pd.DataFrame:
    """
    Load general performance trend data (monthly/daily)
    
    Expected columns (Turkish): Tarih, Maliyet, Dönüşümler, Tıklamalar, Gösterimler, etc.
    
    Returns:
        DataFrame with standardized English column names
    """
    try:
        if not os.path.exists(file_path):
            st.warning(f"⚠️ CSV file not found: {file_path}. Using simulated data.")
            return None
        
        df = pd.read_csv(file_path, encoding='utf-8-sig')
        
        # Map Turkish column names to English
        column_mapping = {
            'Tarih': 'Date',
            'Maliyet': 'Cost',
            'Dönüşümler': 'Conversions',
            'Tıklamalar': 'Clicks',
            'Tıklama': 'Clicks',
            'Gösterimler': 'Impressions',
            'Gösterim': 'Impressions',
            'Dön. oranı': 'CVR',
            'Dönüşüm oranı': 'CVR',
            'TO': 'CTR',
            'Tıklama oranı': 'CTR',
            'Maliyet/dönüşüm': 'CPA',
            'Dönüşüm başına maliyet': 'CPA'
        }
        
        # Rename columns
        df = df.rename(columns=column_mapping)
        
        # Clean numeric columns
        numeric_columns = ['Cost', 'Conversions', 'Clicks', 'Impressions', 'CVR', 'CTR', 'CPA']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = df[col].apply(clean_numeric_value)
        
        # Parse date
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        
        # Calculate missing metrics
        if 'CTR' not in df.columns and 'Clicks' in df.columns and 'Impressions' in df.columns:
            df['CTR'] = np.where(df['Impressions'] > 0, 
                                 (df['Clicks'] / df['Impressions']) * 100, 0)
        
        if 'CVR' not in df.columns and 'Conversions' in df.columns and 'Clicks' in df.columns:
            df['CVR'] = np.where(df['Clicks'] > 0, 
                                 (df['Conversions'] / df['Clicks']) * 100, 0)
        
        if 'CPA' not in df.columns and 'Cost' in df.columns and 'Conversions' in df.columns:
            df['CPA'] = np.where(df['Conversions'] > 0, 
                                 df['Cost'] / df['Conversions'], 0)
        
        return df
    
    except Exception as e:
        st.error(f"❌ Error loading {file_path}: {str(e)}")
        return None


def load_geographical_performance_csv(file_path: str = 'data/cografi_performans.csv') -> pd.DataFrame:
    """
    Load geographical performance data by district
    
    Expected columns: İlçe/District, Maliyet, Dönüşümler, TO, Dön. oranı, etc.
    
    Returns:
        DataFrame with standardized column names
    """
    try:
        if not os.path.exists(file_path):
            st.warning(f"⚠️ CSV file not found: {file_path}. Using simulated data.")
            return None
        
        df = pd.read_csv(file_path, encoding='utf-8-sig')
        
        # Map Turkish column names
        column_mapping = {
            'İlçe': 'District',
            'Bölge': 'District',
            'Konum': 'District',
            'Maliyet': 'Cost',
            'Dönüşümler': 'Conversions',
            'Tıklamalar': 'Clicks',
            'Gösterimler': 'Impressions',
            'Dön. oranı': 'CVR',
            'TO': 'CTR',
            'Maliyet/dönüşüm': 'CPA'
        }
        
        df = df.rename(columns=column_mapping)
        
        # Clean numeric columns
        numeric_columns = ['Cost', 'Conversions', 'Clicks', 'Impressions', 'CVR', 'CTR', 'CPA']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = df[col].apply(clean_numeric_value)
        
        # Calculate missing metrics
        if 'CTR' not in df.columns and 'Clicks' in df.columns and 'Impressions' in df.columns:
            df['CTR'] = np.where(df['Impressions'] > 0, 
                                 (df['Clicks'] / df['Impressions']) * 100, 0)
        
        if 'CVR' not in df.columns and 'Conversions' in df.columns and 'Clicks' in df.columns:
            df['CVR'] = np.where(df['Clicks'] > 0, 
                                 (df['Conversions'] / df['Clicks']) * 100, 0)
        
        if 'CPA' not in df.columns and 'Cost' in df.columns and 'Conversions' in df.columns:
            df['CPA'] = np.where(df['Conversions'] > 0, 
                                 df['Cost'] / df['Conversions'], 0)
        
        return df
    
    except Exception as e:
        st.error(f"❌ Error loading {file_path}: {str(e)}")
        return None


def load_search_terms_csv(file_path: str = 'data/arama_terimleri.csv') -> pd.DataFrame:
    """
    Load search terms detail data
    
    Expected columns: Arama terimi, Maliyet, Dönüşümler, etc.
    
    Returns:
        DataFrame with search term performance
    """
    try:
        if not os.path.exists(file_path):
            st.warning(f"⚠️ CSV file not found: {file_path}. Using simulated data.")
            return None
        
        df = pd.read_csv(file_path, encoding='utf-8-sig')
        
        # Map Turkish column names
        column_mapping = {
            'Arama terimi': 'Search_Term',
            'Arama': 'Search_Term',
            'Terim': 'Search_Term',
            'Maliyet': 'Cost',
            'Dönüşümler': 'Conversions',
            'Tıklamalar': 'Clicks',
            'Gösterimler': 'Impressions',
            'Dön. oranı': 'CVR',
            'TO': 'CTR',
            'Maliyet/dönüşüm': 'CPA'
        }
        
        df = df.rename(columns=column_mapping)
        
        # Clean numeric columns
        numeric_columns = ['Cost', 'Conversions', 'Clicks', 'Impressions', 'CVR', 'CTR', 'CPA']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = df[col].apply(clean_numeric_value)
        
        return df
    
    except Exception as e:
        st.error(f"❌ Error loading {file_path}: {str(e)}")
        return None


def calculate_market_dominance_score(
    tpi: float,
    actual_cvr: float,
    actual_cpa: float,
    avg_cvr: float,
    avg_cpa: float
) -> float:
    """
    Calculate Market Dominance Score (MDS) combining market opportunity with actual performance
    
    Args:
        tpi: Targeting Priority Index (0-100)
        actual_cvr: Actual CVR for the district (%)
        actual_cpa: Actual CPA for the district
        avg_cvr: Average CVR across all districts (%)
        avg_cpa: Average CPA across all districts
    
    Returns:
        Market Dominance Score (0-100)
    """
    # TPI component (40% weight) - market opportunity
    tpi_component = (tpi / 100) * 40
    
    # CVR component (30% weight) - conversion efficiency
    cvr_ratio = actual_cvr / avg_cvr if avg_cvr > 0 else 1.0
    cvr_component = min(cvr_ratio, 2.0) * 15  # Cap at 2x average
    
    # CPA component (30% weight) - cost efficiency (inverse relationship)
    cpa_ratio = avg_cpa / actual_cpa if actual_cpa > 0 else 1.0
    cpa_component = min(cpa_ratio, 2.0) * 15  # Cap at 2x better than average
    
    mds = tpi_component + cvr_component + cpa_component
    
    return min(mds, 100)


# ============================================================================
# GOOGLE PLACES API INTEGRATION
# ============================================================================

def load_places_from_csv(csv_path: str = 'data/istanbul_all_batteries_with_ads.csv') -> list:
    """
    Load pre-fetched places data from CSV file
    This is faster and saves API quota
    
    Args:
        csv_path: Path to CSV file with places data
    
    Returns:
        List of place dictionaries in Google Places API format
    """
    if not os.path.exists(csv_path):
        return []
    
    try:
        df = pd.read_csv(csv_path, encoding='utf-8-sig')
        places = []
        for _, row in df.iterrows():
            
            place = {
                'place_id': row.get('place_id', ''),
                'name': row.get('name', ''),
                'vicinity': row.get('address', ''),
                'geometry': {
                    'location': {
                        'lat': row.get('latitude', 0),
                        'lng': row.get('longitude', 0)
                    }
                },
                'rating': row.get('rating', 0),
                'user_ratings_total': row.get('user_ratings_total', 0),
                'business_status': row.get('business_status', 'OPERATIONAL'),
                'types': row.get('types', 'business').split(', ') if pd.notna(row.get('types')) else ['business'],
                # Yeni alanlar
                'formatted_phone_number': row.get('formatted_phone_number', ''),
                'website': row.get('website', ''),
                'has_ads': row.get('has_ads', False),
                'ads_confidence': row.get('ads_confidence', 'low')
            }
            places.append(place)
        
        return places
        
    except Exception as e:
        st.warning(f"⚠️ Error loading CSV {csv_path}: {str(e)}")
        return []


def fetch_places_nearby(latitude: float, longitude: float, business_type: str, radius: int = 15000, api_key: str = None) -> list:
    """
    Fetch real competitor data from Google Places API
    
    Args:
        latitude: Center latitude
        longitude: Center longitude
        business_type: Type of business to search (e.g., 'car battery store', 'plumber')
        radius: Search radius in meters (default 15km)
        api_key: Google Places API key
    
    Returns:
        List of place dictionaries
    """
    if not api_key:
        return []
    
    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    
    all_places = []
    next_page_token = None
    
    try:
        # Google Places API allows up to 3 pages of 20 results each
        for page in range(3):  # Maximum 60 results
            params = {
                'location': f'{latitude},{longitude}',
                'radius': radius,
                'keyword': business_type,
                'key': api_key,
                'language': 'tr'
            }
            
            if next_page_token:
                params['pagetoken'] = next_page_token
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('status') == 'OK':
                    all_places.extend(data.get('results', []))
                    next_page_token = data.get('next_page_token')
                    
                    if not next_page_token:
                        break
                    
                    # Wait before next request (required by Google API)
                    time.sleep(2)
                else:
                    st.warning(f"⚠️ Google Places API: {data.get('status')} - {data.get('error_message', 'Unknown error')}")
                    break
            else:
                st.error(f"❌ Google Places API request failed: {response.status_code}")
                break
        
        return all_places
    
    except Exception as e:
        st.error(f"❌ Error fetching Places data: {str(e)}")
        return []


def process_places_to_competitors(places: list, center_lat: float, center_lon: float, districts: list) -> pd.DataFrame:
    """
    Convert Google Places API results to competitor DataFrame
    
    Args:
        places: List of places from Google Places API
        center_lat: Center latitude (Bahçelievler)
        center_lon: Center longitude (Bahçelievler)
        districts: List of district names
    
    Returns:
        DataFrame with competitor information
    """
    if not places:
        return pd.DataFrame()
    
    competitors_data = []
    
    for i, place in enumerate(places):
        # Extract place details
        name = place.get('name', f'Business {i+1}')
        place_lat = place.get('geometry', {}).get('location', {}).get('lat', center_lat)
        place_lon = place.get('geometry', {}).get('location', {}).get('lng', center_lon)
        rating = place.get('rating', 0.0)
        review_count = place.get('user_ratings_total', 0)
        business_status = place.get('business_status', 'OPERATIONAL')
        
        # Skip if not operational
        if business_status != 'OPERATIONAL':
            continue
        
        # Calculate distance from Bahçelievler center
        distance_km = haversine_distance(center_lat, center_lon, place_lat, place_lon)
        
        # Estimate district based on location (simple proximity to known districts)
        # In production, use reverse geocoding for accurate district
        district = np.random.choice(districts)  # Placeholder - ideally use reverse geocoding
        
        # Calculate market density (approximate)
        nearby_competitors = sum(1 for p in places if haversine_distance(
            place_lat, place_lon,
            p.get('geometry', {}).get('location', {}).get('lat', 0),
            p.get('geometry', {}).get('location', {}).get('lng', 0)
        ) < 2.0)  # Within 2km
        
        # Calculate CPS
        cps = calculate_competitive_pressure_score(
            review_count if review_count > 0 else 10,
            rating if rating > 0 else 3.5,
            distance_km,
            nearby_competitors
        )
        
        # Estimate revenue based on rating and reviews
        daily_revenue_estimate = (rating * 200) + (review_count * 2) + np.random.uniform(500, 2000)
        profit_margin = np.random.uniform(0.15, 0.35)
        
        
        competitors_data.append({
            'Competitor_ID': place.get('place_id', f'PLACE_{i+1}'),
            'Business_Name': name,
            'District': district,
            'Business_Type': place.get('types', ['business'])[0] if place.get('types') else 'business',
            'Latitude': round(place_lat, 6),
            'Longitude': round(place_lon, 6),
            'Distance_From_Center_KM': round(distance_km, 2),
            'Simulated_Avg_Rating': round(rating, 1) if rating > 0 else 0.0,
            'Simulated_Review_Count': review_count,
            'Market_Density': nearby_competitors,
            # Yeni alanlar
            'Phone_Number': place.get('formatted_phone_number', ''),
            'Website': place.get('website', ''),
            'Has_Ads': place.get('has_ads', False),
            'Ads_Confidence': place.get('ads_confidence', 'low'),
            'Competitive_Pressure_Score': round(cps, 2),
            'Daily_Revenue_Estimate': round(daily_revenue_estimate, 2),
            'Profit_Margin_Estimate': round(profit_margin, 2),
            'Is_Real_Data': True  # Flag to indicate this is real Places data
        })
    
    if not competitors_data:
        return pd.DataFrame()
    
    competitors_df = pd.DataFrame(competitors_data)
    
    # Calculate TPI
    competitors_df['Targeting_Priority_Index'] = normalize_to_tpi(
        competitors_df['Competitive_Pressure_Score']
    )
    
    return competitors_df


# ============================================================================
# GEOSPATIAL CALCULATIONS
# ============================================================================

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the Haversine distance between two points on Earth
    
    Args:
        lat1, lon1: Latitude and longitude of first point
        lat2, lon2: Latitude and longitude of second point
    
    Returns:
        Distance in kilometers
    """
    R = 6371  # Earth's radius in kilometers
    
    # Convert to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    return R * c


def calculate_competitive_pressure_score(
    review_count: int,
    rating: float,
    distance_km: float,
    market_density: int
) -> float:
    """
    Calculate the Competitive Pressure Score (CPS) based on multiple factors
    
    Args:
        review_count: Number of reviews (market presence indicator)
        rating: Average rating (quality indicator)
        distance_km: Distance from core center
        market_density: Number of competitors in the area
    
    Returns:
        Competitive Pressure Score (0-100)
    """
    # Review weight: More reviews = more established
    review_factor = min(review_count / 500, 1.0) * 30
    
    # Rating weight: Higher rating = stronger competitor
    rating_factor = (rating / 5.0) * 25
    
    # Distance weight: Closer competitors = higher pressure (inverse relationship)
    distance_factor = max(0, (15 - distance_km) / 15) * 25
    
    # Density weight: More competitors nearby = higher pressure
    density_factor = min(market_density / 20, 1.0) * 20
    
    cps = review_factor + rating_factor + distance_factor + density_factor
    
    return min(cps, 100)


def normalize_to_tpi(cps_series: pd.Series) -> pd.Series:
    """
    Normalize Competitive Pressure Score to Targeting Priority Index (1-100)
    Higher TPI = Higher opportunity (inverse of competitive pressure in some contexts)
    
    For marketing: High competition CAN mean high opportunity if managed correctly
    """
    # Normalize to 1-100 scale
    min_cps = cps_series.min()
    max_cps = cps_series.max()
    
    if max_cps == min_cps:
        return pd.Series([50] * len(cps_series))
    
    # Scale to 1-100, where higher CPS = higher TPI (opportunity)
    tpi = 1 + ((cps_series - min_cps) / (max_cps - min_cps)) * 99
    
    return tpi.round(2)


# ============================================================================
# CITY COORDINATES & DISTRICTS
# ============================================================================

CITY_COORDINATES = {
    'Istanbul': {
        'center': (CORE_CENTER_LAT, CORE_CENTER_LON),  # Bahçelievler coordinates
        'districts': [
            'Kadıköy', 'Beşiktaş', 'Şişli', 'Beyoğlu', 'Fatih', 'Üsküdar',
            'Maltepe', 'Kartal', 'Pendik', 'Ümraniye', 'Ataşehir', 'Bakırköy',
            'Bahçelievler', 'Esenler', 'Güngören', 'Zeytinburnu', 'Sarıyer',
            'Beykoz', 'Çekmeköy', 'Sancaktepe'
        ]
    },
    'Ankara': {
        'center': (39.925533, 32.866287),
        'districts': [
            'Çankaya', 'Keçiören', 'Yenimahalle', 'Mamak', 'Etimesgut',
            'Sincan', 'Altındağ', 'Gölbaşı', 'Pursaklar', 'Polatlı'
        ]
    },
    'Izmir': {
        'center': (38.423734, 27.142826),
        'districts': [
            'Konak', 'Karşıyaka', 'Bornova', 'Buca', 'Çiğli', 'Balçova',
            'Gaziemir', 'Narlıdere', 'Bayraklı', 'Güzelbahçe'
        ]
    }
}


SECTOR_TEMPLATES = {
    'Battery Dealers': {
        'business_types': ['Akü Satış', 'Akü Servisi', 'Oto Elektrik', 'Akü Değişim Noktası'],
        'places_api_keyword': 'akü satış oto servis',  # Google Places search term
        'avg_ticket': 850,  # TL
        'conversion_rate_range': (0.08, 0.15),
        'negative_keywords': [
            'bedava akü', 'ücretsiz', 'oyuncak akü', 'ikinci el akü',
            'hurda akü', 'eski akü', 'kullanılmış akü', 'fiyat sadece'
        ]
    },
    'Plumbers': {
        'business_types': ['Tesisatçı', 'Su Tesisatı', 'Kalorifer Tesisatı', 'Acil Tesisat'],
        'places_api_keyword': 'tesisatçı',  # Google Places search term
        'avg_ticket': 450,  # TL
        'conversion_rate_range': (0.10, 0.18),
        'negative_keywords': [
            'bedava', 'ücretsiz', 'iş arıyorum', 'eleman arıyorum',
            'kurs', 'eğitim', 'DIY', 'kendin yap'
        ]
    },
    'Electricians': {
        'business_types': ['Elektrikçi', 'Elektrik Tesisatı', 'Pano Montajı', 'Acil Elektrikçi'],
        'places_api_keyword': 'elektrikçi',  # Google Places search term
        'avg_ticket': 550,  # TL
        'conversion_rate_range': (0.09, 0.16),
        'negative_keywords': [
            'bedava', 'ücretsiz', 'iş ilanı', 'eleman',
            'maaş', 'kurs', 'sertifika'
        ]
    }
}


# ============================================================================
# MAIN DATA GENERATION FUNCTION
# ============================================================================

@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_and_process_data(sector_name: str, location_name: str, cache_version: int = 2) -> Dict[str, pd.DataFrame]:
    """
    Main data generation function - Creates simulated market and ads data
    
    Args:
        sector_name: Business sector (e.g., 'Battery Dealers')
        location_name: Target city (e.g., 'Istanbul')
    
    Returns:
        Dictionary containing 'Competitors_DF' and 'Historical_Ads_DF'
    """
    np.random.seed(42)  # For reproducibility
    
    # Get city and sector configuration
    city_config = CITY_COORDINATES.get(location_name, CITY_COORDINATES['Istanbul'])
    sector_config = SECTOR_TEMPLATES.get(sector_name, SECTOR_TEMPLATES['Battery Dealers'])
    
    center_lat, center_lon = city_config['center']
    districts = city_config['districts']
    
    # ========================================================================
    # A. LOAD/GENERATE COMPETITORS_DF (Market/Places Data)
    # ========================================================================
    
    competitors_df = pd.DataFrame()
    places = []
    
    # PRIORITY 1: Try to load from CSV (faster, comprehensive, saves API quota)
    if USE_CSV_PLACES_DATA and os.path.exists(CSV_PLACES_FILE):
        st.info(f"📂 Loading pre-fetched competitor data from CSV ({CSV_PLACES_FILE})...")
        places = load_places_from_csv(CSV_PLACES_FILE)
        
        if places:
            st.info(f"🔍 Processing {len(places)} places with {len(districts)} districts...")
            competitors_df = process_places_to_competitors(places, center_lat, center_lon, districts)
            if not competitors_df.empty:
                has_ads_count = competitors_df['Has_Ads'].sum() if 'Has_Ads' in competitors_df.columns else 0
                st.success(f"✅ Loaded {len(competitors_df)} real competitors from CSV! ({has_ads_count} with ads)")
            else:
                st.warning("⚠️ CSV data processing failed.")
                places = []  # Reset to try API
    
    # PRIORITY 2: Try Google Places API if CSV not available or failed
    if competitors_df.empty and USE_REAL_PLACES_DATA and GOOGLE_PLACES_API_KEY:
        st.info(f"🔄 Fetching real competitor data from Google Places API for {sector_name}...")
        
        # Get search keyword for this sector
        search_keyword = sector_config.get('places_api_keyword', sector_name.lower())
        
        # Fetch places from Google API
        places = fetch_places_nearby(
            latitude=center_lat,
            longitude=center_lon,
            business_type=search_keyword,
            radius=15000,  # 15km radius
            api_key=GOOGLE_PLACES_API_KEY
        )
        
        if places:
            # Process Places API results
            competitors_df = process_places_to_competitors(places, center_lat, center_lon, districts)
            
            if not competitors_df.empty:
                st.success(f"✅ Loaded {len(competitors_df)} real competitors from Google Places API!")
            else:
                st.warning("⚠️ Google Places returned data but processing failed. Using simulated data.")
        else:
            st.warning("⚠️ No data from Google Places API. Using simulated data.")
    
    # Fallback to simulated data if Places API not available or failed
    if competitors_df.empty:
        if not GOOGLE_PLACES_API_KEY:
            st.info("📊 Using simulated competitor data. Add Google Places API key to config.py for real data.")
        
        num_competitors = np.random.randint(60, 85)
        competitors_data = []
        
        for i in range(num_competitors):
            district = np.random.choice(districts)
            
            # Generate coordinates around center (within ~15km radius)
            lat_offset = np.random.uniform(-0.15, 0.15)
            lon_offset = np.random.uniform(-0.15, 0.15)
            comp_lat = center_lat + lat_offset
            comp_lon = center_lon + lon_offset
            
            distance_km = haversine_distance(center_lat, center_lon, comp_lat, comp_lon)
            
            business_type = np.random.choice(sector_config['business_types'])
            rating = np.random.uniform(3.0, 5.0)
            review_count = int(np.random.exponential(150) + 10)
            
            market_density = sum(1 for c in competitors_data if c['District'] == district) + 1
            
            cps = calculate_competitive_pressure_score(
                review_count, rating, distance_km, market_density
            )
            
            daily_revenue_estimate = np.random.uniform(500, 5000)
            profit_margin = np.random.uniform(0.15, 0.35)
            
            competitors_data.append({
                'Competitor_ID': f'COMP_{i+1:03d}',
                'Business_Name': f'{business_type} - {district} {i+1}',
                'District': district,
                'Business_Type': business_type,
                'Latitude': round(comp_lat, 6),
                'Longitude': round(comp_lon, 6),
                'Distance_From_Center_KM': round(distance_km, 2),
                'Simulated_Avg_Rating': round(rating, 1),
                'Simulated_Review_Count': review_count,
                'Market_Density': market_density,
                'Competitive_Pressure_Score': round(cps, 2),
                'Daily_Revenue_Estimate': round(daily_revenue_estimate, 2),
                'Profit_Margin_Estimate': round(profit_margin, 2),
                'Is_Real_Data': False  # Flag for simulated data
            })
        
        competitors_df = pd.DataFrame(competitors_data)
        
        # Calculate TPI (Targeting Priority Index)
        competitors_df['Targeting_Priority_Index'] = normalize_to_tpi(
            competitors_df['Competitive_Pressure_Score']
        )
    
    # ========================================================================
    # B. LOAD REAL HISTORICAL_ADS_DF (From CSV Files)
    # ========================================================================
    
    # Load CSV files
    general_trend_df = load_general_trend_csv()
    geographical_df = load_geographical_performance_csv()
    search_terms_df = load_search_terms_csv()
    
    # Initialize historical_ads_df
    historical_ads_df = pd.DataFrame()
    
    # If real data available, use it; otherwise fall back to simulation
    if general_trend_df is not None and not general_trend_df.empty:
        # Use general trend as base
        historical_ads_df = general_trend_df.copy()
        
        # Add district information if geographical data available
        if geographical_df is not None and not geographical_df.empty:
            # Create district-level entries by expanding general trend
            district_rows = []
            for _, row in historical_ads_df.iterrows():
                # For each date/general entry, create entries for top districts
                for _, geo_row in geographical_df.head(10).iterrows():  # Top 10 districts
                    district_entry = row.copy()
                    district_entry['Ads_District'] = geo_row.get('District', 'Unknown')
                    # Scale metrics by district contribution
                    district_contribution = geo_row.get('Conversions', 1) / geographical_df['Conversions'].sum() if geographical_df['Conversions'].sum() > 0 else 0.1
                    for col in ['Cost', 'Conversions', 'Clicks', 'Impressions']:
                        if col in district_entry:
                            district_entry[col] = district_entry[col] * district_contribution
                    district_rows.append(district_entry)
            
            if district_rows:
                historical_ads_df = pd.DataFrame(district_rows)
        else:
            # If no geographical data, distribute across city districts
            historical_ads_df['Ads_District'] = np.random.choice(districts, size=len(historical_ads_df))
        
        # Add search terms if available
        if search_terms_df is not None and not search_terms_df.empty and 'Search_Term' in search_terms_df.columns:
            top_search_terms = search_terms_df.nlargest(20, 'Conversions' if 'Conversions' in search_terms_df.columns else 'Cost')['Search_Term'].tolist()
            historical_ads_df['Search_Term'] = np.random.choice(
                top_search_terms if top_search_terms else [f'{sector_name}'], 
                size=len(historical_ads_df)
            )
        else:
            # Generate default search terms
            base_search_terms = [
                f'{sector_name.lower()} {location_name.lower()}',
                f'acil {sector_name.lower()}',
                f'en iyi {sector_name.lower()}',
                f'{sector_name.lower()} fiyat',
                f'{sector_name.lower()} yakın'
            ]
            historical_ads_df['Search_Term'] = np.random.choice(base_search_terms, size=len(historical_ads_df))
        
        # Ensure all required columns exist
        required_columns = ['Date', 'Ads_District', 'Search_Term', 'Cost', 'Conversions', 'Clicks', 'Impressions', 'CTR', 'CVR', 'CPA']
        for col in required_columns:
            if col not in historical_ads_df.columns:
                if col == 'Date':
                    historical_ads_df['Date'] = pd.date_range(end=datetime.now(), periods=len(historical_ads_df), freq='D')
                elif col in ['Ads_District']:
                    historical_ads_df[col] = np.random.choice(districts, size=len(historical_ads_df))
                elif col == 'Search_Term':
                    historical_ads_df[col] = f'{sector_name}'
                else:
                    historical_ads_df[col] = 0
        
    else:
        # FALLBACK: Generate simulated data if CSVs not found
        st.info("📊 CSV files not found. Using simulated data. Place CSV files in 'data/' directory for real data.")
        
        num_ads_entries = 100
        start_date = datetime.now() - timedelta(days=90)
        historical_ads_data = []
        
        base_search_terms = [
            f'{sector_name.lower()} {location_name.lower()}',
            f'acil {sector_name.lower()}',
            f'en iyi {sector_name.lower()}',
            f'{sector_name.lower()} fiyat',
            f'{sector_name.lower()} yakın'
        ]
        
        for i in range(num_ads_entries):
            days_ago = np.random.randint(0, 90)
            ad_date = start_date + timedelta(days=days_ago)
            district = np.random.choice(districts)
            search_term = np.random.choice(base_search_terms)
            
            impressions = int(np.random.uniform(100, 2000))
            clicks = int(impressions * np.random.uniform(0.02, 0.12))
            conversions = int(clicks * np.random.uniform(*sector_config['conversion_rate_range']))
            cost = round(clicks * np.random.uniform(2.5, 8.5), 2)
            
            ctr = (clicks / impressions * 100) if impressions > 0 else 0
            cvr = (conversions / clicks * 100) if clicks > 0 else 0
            cpa = (cost / conversions) if conversions > 0 else 0
            
            historical_ads_data.append({
                'Date': ad_date.strftime('%Y-%m-%d'),
                'Ads_District': district,
                'Search_Term': search_term,
                'Impressions': impressions,
                'Clicks': clicks,
                'Conversions': conversions,
                'Cost': cost,
                'CTR': round(ctr, 2),
                'CVR': round(cvr, 2),
                'CPA': round(cpa, 2)
            })
        
        historical_ads_df = pd.DataFrame(historical_ads_data)
        historical_ads_df['Date'] = pd.to_datetime(historical_ads_df['Date'])
    
    # Final processing
    historical_ads_df = historical_ads_df.sort_values('Date') if 'Date' in historical_ads_df.columns else historical_ads_df
    
    # Recalculate metrics to ensure consistency
    if 'Clicks' in historical_ads_df.columns and 'Impressions' in historical_ads_df.columns:
        historical_ads_df['CTR'] = np.where(
            historical_ads_df['Impressions'] > 0,
            (historical_ads_df['Clicks'] / historical_ads_df['Impressions']) * 100,
            0
        )
    
    if 'Conversions' in historical_ads_df.columns and 'Clicks' in historical_ads_df.columns:
        historical_ads_df['CVR'] = np.where(
            historical_ads_df['Clicks'] > 0,
            (historical_ads_df['Conversions'] / historical_ads_df['Clicks']) * 100,
            0
        )
    
    if 'Cost' in historical_ads_df.columns and 'Conversions' in historical_ads_df.columns:
        historical_ads_df['CPA'] = np.where(
            historical_ads_df['Conversions'] > 0,
            historical_ads_df['Cost'] / historical_ads_df['Conversions'],
            0
        )
    
    # Store negative keywords and geographical data in session state instead of attrs
    # (Pandas 2.2.0 has issues with DataFrame attrs in groupby operations)
    return {
        'Competitors_DF': competitors_df,
        'Historical_Ads_DF': historical_ads_df,
        'negative_keywords': sector_config['negative_keywords'],
        'geographical_df': geographical_df,
        'search_terms_df': search_terms_df
    }


# ============================================================================
# API PLACEHOLDER FUNCTIONS
# ============================================================================

def fetch_live_keyword_data(sector: str, location: str, language: str = 'tr') -> pd.DataFrame:
    """
    PLACEHOLDER: Real Google Ads API Integration
    
    This function should be replaced with actual Google Ads API calls using
    the KeywordPlanIdeaService to fetch live keyword data.
    
    Required Setup:
    1. Install google-ads library: pip install google-ads
    2. Configure google-ads.yaml with credentials
    3. Use KeywordPlanIdeaService.GenerateKeywordIdeas()
    
    Example Implementation:
    ```
    from google.ads.googleads.client import GoogleAdsClient
    
    client = GoogleAdsClient.load_from_storage('google-ads.yaml')
    keyword_plan_idea_service = client.get_service('KeywordPlanIdeaService')
    
    request = client.get_type('GenerateKeywordIdeasRequest')
    request.customer_id = 'YOUR_CUSTOMER_ID'
    request.language = language
    request.geo_target_constants.append('geoTargetConstants/2792')  # Turkey
    
    response = keyword_plan_idea_service.generate_keyword_ideas(request=request)
    ```
    
    Args:
        sector: Business sector
        location: Target location
        language: Language code
    
    Returns:
        DataFrame with keyword data (currently simulated)
    """
    # SIMULATION CODE - REPLACE WITH REAL API CALL
    print("⚠️  Using simulated data. Replace with Google Ads API integration.")
    
    keywords = [
        {'keyword': f'{sector} {location}', 'avg_monthly_searches': 1200, 'competition': 0.75},
        {'keyword': f'acil {sector}', 'avg_monthly_searches': 800, 'competition': 0.65},
        {'keyword': f'en iyi {sector}', 'avg_monthly_searches': 950, 'competition': 0.80},
    ]
    
    return pd.DataFrame(keywords)


def fetch_live_campaign_performance(customer_id: str, campaign_ids: list) -> pd.DataFrame:
    """
    PLACEHOLDER: Real Google Ads API Integration for Campaign Performance
    
    This function should be replaced with actual Google Ads API calls using
    the GoogleAdsService to fetch real campaign performance data.
    
    Required Setup:
    1. Use GoogleAdsService.search() or search_stream()
    2. Query campaign performance metrics
    
    Example Query:
    ```
    query = '''
        SELECT
            campaign.id,
            campaign.name,
            metrics.impressions,
            metrics.clicks,
            metrics.conversions,
            metrics.cost_micros
        FROM campaign
        WHERE segments.date DURING LAST_30_DAYS
    '''
    ```
    
    Args:
        customer_id: Google Ads customer ID
        campaign_ids: List of campaign IDs to fetch
    
    Returns:
        DataFrame with campaign performance (currently simulated)
    """
    # SIMULATION CODE - REPLACE WITH REAL API CALL
    print("⚠️  Using simulated data. Replace with Google Ads API integration.")
    
    return pd.DataFrame({
        'campaign_id': campaign_ids,
        'impressions': [5000, 3000],
        'clicks': [250, 180],
        'conversions': [25, 18]
    })


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_available_sectors() -> list:
    """Return list of available business sectors"""
    return list(SECTOR_TEMPLATES.keys())


def get_available_cities() -> list:
    """Return list of available cities"""
    return list(CITY_COORDINATES.keys())


def get_sector_config(sector_name: str) -> dict:
    """Get configuration for a specific sector"""
    return SECTOR_TEMPLATES.get(sector_name, SECTOR_TEMPLATES['Battery Dealers'])


def get_city_config(city_name: str) -> dict:
    """Get configuration for a specific city"""
    return CITY_COORDINATES.get(city_name, CITY_COORDINATES['Istanbul'])

