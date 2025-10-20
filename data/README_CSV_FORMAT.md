# 📊 CSV Data Files Guide

This directory should contain your real Google Ads performance data exported as CSV files. The application will automatically load and process these files.

---

## Required CSV Files

### 1. `genel_trend_aylik.csv` - General Performance Trend

**Purpose**: Time-series data showing overall account performance

**Required Columns** (Turkish or English):
- `Tarih` or `Date` - Date in format: YYYY-MM-DD or DD/MM/YYYY
- `Maliyet` or `Cost` - Total cost in your currency
- `Dönüşümler` or `Conversions` - Number of conversions
- `Tıklamalar` or `Clicks` - Number of clicks
- `Gösterimler` or `Impressions` - Number of impressions

**Optional Columns** (will be calculated if missing):
- `Dön. oranı` or `CVR` - Conversion rate (%)
- `TO` or `CTR` - Click-through rate (%)
- `Maliyet/dönüşüm` or `CPA` - Cost per acquisition

**Example Format**:
```csv
Tarih,Maliyet,Dönüşümler,Tıklamalar,Gösterimler
2024-01-01,1250.50,15,234,5678
2024-01-02,980.25,12,198,4523
```

**How to Export from Google Ads**:
1. Go to Campaigns → Reports
2. Select date range (recommended: last 90 days)
3. Add columns: Date, Cost, Conversions, Clicks, Impressions
4. Export as CSV

---

### 2. `cografi_performans.csv` - Geographical Performance

**Purpose**: District-level performance data for map calibration

**Required Columns**:
- `İlçe` or `District` or `Bölge` - District/Location name
- `Maliyet` or `Cost` - Total cost for this location
- `Dönüşümler` or `Conversions` - Number of conversions
- `Tıklamalar` or `Clicks` - Number of clicks

**Optional Columns**:
- `Gösterimler` or `Impressions` - Number of impressions
- `Dön. oranı` or `CVR` - Conversion rate (%)
- `TO` or `CTR` - Click-through rate (%)
- `Maliyet/dönüşüm` or `CPA` - Cost per acquisition

**Example Format**:
```csv
İlçe,Maliyet,Dönüşümler,Tıklamalar,Gösterimler
Kadıköy,5670.00,68,892,15234
Beşiktaş,4320.50,52,756,12890
Şişli,6890.75,75,1023,18765
```

**How to Export from Google Ads**:
1. Go to Campaigns → Locations
2. Select "User location" view
3. Filter for your target city (e.g., Istanbul)
4. Add columns: Location, Cost, Conversions, Clicks
5. Export as CSV

---

### 3. `arama_terimleri.csv` - Search Terms Detail

**Purpose**: Search term performance for negative keyword analysis

**Required Columns**:
- `Arama terimi` or `Search_Term` - The search term
- `Maliyet` or `Cost` - Cost for this search term
- `Dönüşümler` or `Conversions` - Number of conversions
- `Tıklamalar` or `Clicks` - Number of clicks

**Optional Columns**:
- `Gösterimler` or `Impressions` - Number of impressions
- `Dön. oranı` or `CVR` - Conversion rate (%)
- `TO` or `CTR` - Click-through rate (%)

**Example Format**:
```csv
Arama terimi,Maliyet,Dönüşümler,Tıklamalar,Gösterimler
akü satış istanbul,890.50,12,145,3456
acil akü servisi,1250.00,18,189,2890
en iyi akü,670.25,8,98,2145
```

**How to Export from Google Ads**:
1. Go to Campaigns → Keywords → Search Terms
2. Select date range
3. Add columns: Search term, Cost, Conversions, Clicks
4. Export as CSV

---

## Data Cleaning Features

The application automatically handles:

- ✅ **Non-numeric values**: '--', '< 10', empty cells → converted to 0
- ✅ **Percentage formats**: '10,50%' → 0.1050
- ✅ **Turkish number format**: '1.234,56' → 1234.56
- ✅ **Missing metrics**: Automatically calculates CVR, CTR, CPA if missing
- ✅ **Column name variants**: Supports both Turkish and English column names
- ✅ **Date formats**: Handles various date formats automatically

---

## File Encoding

**Important**: Save your CSV files with **UTF-8** encoding to properly display Turkish characters (ç, ğ, ı, İ, ö, ş, ü).

### How to ensure UTF-8 encoding:

**Excel**:
1. File → Save As
2. Choose "CSV UTF-8 (Comma delimited)"

**Google Sheets**:
1. File → Download → Comma Separated Values (.csv)
2. UTF-8 is automatic

---

## Testing Your CSV Files

1. Place your CSV files in this `data/` directory
2. Restart the Streamlit application
3. Check for loading messages:
   - ✅ Green message = Data loaded successfully
   - ⚠️ Yellow message = File not found or issues
   - ❌ Red message = Error loading file

4. Verify data in the dashboard:
   - Check if metrics match your Google Ads data
   - Verify district names appear correctly
   - Confirm dates are in correct order

---

## Sample Data Templates

If you don't have CSV files yet, the application will use simulated data. To get started with real data:

1. Export your last 30-90 days of data from Google Ads
2. Save in the formats described above
3. Place files in this directory
4. Refresh the application

---

## Troubleshooting

### "CSV file not found" Warning
- **Solution**: Check file names match exactly: `genel_trend_aylik.csv`, `cografi_performans.csv`, `arama_terimleri.csv`
- Check files are in the `data/` directory

### "Error loading CSV" Message
- **Solution**: Open CSV in text editor to check format
- Ensure first row contains column headers
- Check for special characters or encoding issues
- Verify comma (,) is used as delimiter

### Metrics showing as 0
- **Solution**: Check column names match expected names
- Verify numeric values don't contain text
- Ensure percentage signs are included in percentage columns

### Turkish characters displaying incorrectly
- **Solution**: Re-save file with UTF-8 encoding
- Use "CSV UTF-8" option in Excel

---

## Privacy & Security

⚠️ **Important**: CSV files in this directory are listed in `.gitignore` and will NOT be committed to version control. Your data remains private on your local machine.

---

## Need Help?

Check the main README.md for more information or review the code comments in `utils.py` for technical details on data loading and processing.


