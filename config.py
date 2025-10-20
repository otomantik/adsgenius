"""
Configuration file for Marketing Intelligence Platform
Store your API keys here (DO NOT commit to public repositories)
"""

import os

# Google Places API Key - Environment variable'dan oku
GOOGLE_PLACES_API_KEY = os.getenv('GOOGLE_PLACES_API_KEY')

# Bahçelievler Core Center Coordinates (Used as reference point)
CORE_CENTER_LAT = 41.015137
CORE_CENTER_LON = 28.978359

# API Configuration
USE_REAL_PLACES_DATA = True  # Set to False to use simulated competitor data
USE_CSV_PLACES_DATA = True  # Set to True to use pre-fetched CSV data (faster, saves API quota)
CSV_PLACES_FILE = 'data/istanbul_all_batteries_with_ads.csv'  # Path to pre-fetched places CSV
MAX_PLACES_RESULTS = 60  # Number of real competitors to fetch per search


