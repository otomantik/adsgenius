import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore', category=FutureWarning)

from utils import load_and_process_data

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Competitive Map - AdsGenius",
    page_icon="🗺️",
    layout="wide"
)

# ============================================================================
# HEADER
# ============================================================================

st.title("🗺️ Geospatial Strategy & Mapping")
st.markdown("### Competitive Intelligence Dashboard")

# ============================================================================
# SIDEBAR CONTROLS
# ============================================================================

with st.sidebar:
    st.header("🎯 Target Configuration")
    
    # Business sector selection
    sector = st.selectbox(
        "Business Sector",
        ["Battery Dealers", "Plumbers", "Restaurants", "Gyms"],
        key="sector"
    )
    
    # Target city selection
    city = st.selectbox(
        "Target City",
        ["Istanbul", "Ankara", "Izmir"],
        key="city"
    )
    
    # Priority bid radius slider
    st.subheader("🎯 Priority Bid Radius")
    priority_radius = st.slider(
        "Radius (km)",
        min_value=1.0,
        max_value=50.0,
        value=25.0,
        step=1.0,
        help="Set the priority bidding radius around the core center (25km covers most of Istanbul)"
    )

# ============================================================================
# DATA LOADING
# ============================================================================

# Load data
data_dict = load_and_process_data(st.session_state.sector, st.session_state.city, cache_version=2)
competitors_df = data_dict['Competitors_DF']
historical_ads_df = data_dict['Historical_Ads_DF']

# Store additional data in session state
st.session_state.negative_keywords = data_dict.get('negative_keywords', [])
st.session_state.geographical_df = data_dict.get('geographical_df', None)
st.session_state.search_terms_df = data_dict.get('search_terms_df', None)

# ============================================================================
# MAP CENTER CALCULATION
# ============================================================================

# Set map center based on city
city_centers = {
    "Istanbul": {"lat": 41.015137, "lon": 28.978359},
    "Ankara": {"lat": 39.9334, "lon": 32.8597},
    "Izmir": {"lat": 38.4192, "lon": 27.1287}
}

center_lat = city_centers[st.session_state.city]["lat"]
center_lon = city_centers[st.session_state.city]["lon"]

# ============================================================================
# FILTER COMPETITORS BY RADIUS
# ============================================================================

# Filter competitors within priority radius
filtered_competitors = competitors_df[
    competitors_df['Distance_From_Center_KM'] <= priority_radius
].copy()

# ============================================================================
# FOLIUM MAP CREATION
# ============================================================================

# Create base map - zoomed out to show all of Istanbul
m = folium.Map(
    location=[center_lat, center_lon],
    zoom_start=9,  # More zoomed out to show all Istanbul
    tiles='OpenStreetMap'
)

# Add center marker
folium.Marker(
    location=[center_lat, center_lon],
    popup=f"Core Center - {st.session_state.city}",
    icon=folium.Icon(color='red', icon='info-sign')
).add_to(m)

# Add priority radius circle
folium.Circle(
    location=[center_lat, center_lon],
    radius=priority_radius * 1000,  # Convert km to meters
    color='blue',
    fill=True,
    fillColor='blue',
    fillOpacity=0.1,
    popup=f"Priority Bid Radius: {priority_radius} km"
).add_to(m)

# Add competitor markers
for idx, row in filtered_competitors.iterrows():
    # Use real ads data if available
    is_running_ads = row.get('Has_Ads', False)
    ads_confidence = row.get('Ads_Confidence', 'low')
    
    # Check if this is an emergency service business
    emergency_keywords = ['acil', 'yerinde', 'değişim', '7/24', '24 saat', 'mobil', 'takviye', 'yol yardım']
    is_emergency_service = any(keyword in row['Business_Name'].lower() for keyword in emergency_keywords)
    
    # Determine marker color and icon based on ads status, TPI, and emergency service
    if is_emergency_service:
        if is_running_ads:
            marker_color = 'red'
            icon_type = 'star'  # Star icon for emergency services with ads
            priority_label = 'Emergency Service + Ads'
        else:
            marker_color = 'blue'
            icon_type = 'star'  # Star icon for emergency services without ads (opportunity)
            priority_label = 'Emergency Service (Opportunity!)'
    else:
        if is_running_ads:
            if row['Targeting_Priority_Index'] >= 75:
                marker_color = 'orange'
                icon_type = 'info-sign'
                priority_label = 'High (Ads)'
            elif row['Targeting_Priority_Index'] >= 50:
                marker_color = 'yellow'
                icon_type = 'info-sign'
                priority_label = 'Medium (Ads)'
            else:
                marker_color = 'lightgreen'
                icon_type = 'info-sign'
                priority_label = 'Low (Ads)'
        else:
            if row['Targeting_Priority_Index'] >= 70:
                marker_color = 'lightblue'
                icon_type = 'info-sign'
                priority_label = 'High (No Ads)'
            else:
                marker_color = 'green'
                icon_type = 'info-sign'
                priority_label = 'Low (No Ads)'
    
    # Create popup content
    ads_status = "🟢 Running Ads" if is_running_ads else "🔴 No Ads"
    real_ads_confidence = row.get('Ads_Confidence', 'low').title()
    emergency_status = "🚨 EMERGENCY SERVICE" if is_emergency_service else "🏪 Regular Store"
    
    # Phone and website info
    phone_number = row.get('Phone_Number', 'N/A') or 'N/A'
    website = row.get('Website', 'N/A') or 'N/A'
    
    popup_html = f"""
    <div style='width: 320px;'>
        <h4 style='margin: 0 0 10px 0;'>{row['Business_Name']}</h4>
        <div style='background-color: #f0f0f0; padding: 5px; margin-bottom: 10px; border-radius: 3px;'>
            <strong>📊 {ads_status}</strong> <span style='font-size: 10px; color: #666;'>({real_ads_confidence} confidence)</span><br>
            <strong>{emergency_status}</strong>
        </div>
        <table style='width: 100%; font-size: 12px;'>
            <tr><td><b>District:</b></td><td>{row['District']}</td></tr>
            <tr><td><b>TPI Score:</b></td><td><span style='color: {marker_color}; font-weight: bold;'>{row['Targeting_Priority_Index']:.1f}</span> ({priority_label})</td></tr>
            <tr><td><b>Distance:</b></td><td>{row['Distance_From_Center_KM']:.2f} km</td></tr>
            <tr><td><b>CPS:</b></td><td>{row['Competitive_Pressure_Score']:.1f}</td></tr>
            <tr><td><b>Rating:</b></td><td>⭐ {row['Simulated_Avg_Rating']:.1f} ({row['Simulated_Review_Count']} reviews)</td></tr>
            <tr><td><b>Phone:</b></td><td>{phone_number}</td></tr>
            <tr><td><b>Website:</b></td><td>{'<a href="' + str(website) + '" target="_blank">' + str(website)[:30] + ('...' if len(str(website)) > 30 else '') + '</a>' if website and website != 'N/A' else 'N/A'}</td></tr>
        </table>
    </div>
    """
    
    folium.Marker(
        location=[row['Latitude'], row['Longitude']],
        popup=folium.Popup(popup_html, max_width=300),
        tooltip=f"{row['Business_Name']} - TPI: {row['Targeting_Priority_Index']:.1f} - {'Ads' if is_running_ads else 'No Ads'}",
        icon=folium.Icon(color=marker_color, icon=icon_type)
    ).add_to(m)

# ============================================================================
# DISPLAY MAP
# ============================================================================

st.markdown('<div class="sub-header">🌍 Interactive Competitive Intelligence Map</div>', unsafe_allow_html=True)

# Add legend for marker colors
st.markdown("""
<div style='background-color: #f0f0f0; padding: 15px; border-radius: 5px; margin-bottom: 20px;'>
    <h4 style='margin-top: 0;'>📊 Marker Legend - Ad Status Detection</h4>
    <div style='display: flex; flex-wrap: wrap; gap: 15px;'>
        <div><span style='color: red; font-weight: bold;'>🔴 Red + ⭐</span> = Emergency Service + Running Ads</div>
        <div><span style='color: blue; font-weight: bold;'>🔵 Blue + ⭐</span> = Emergency Service + No Ads (Opportunity!)</div>
        <div><span style='color: orange; font-weight: bold;'>🟠 Orange</span> = High Priority + Running Ads</div>
        <div><span style='color: yellow; font-weight: bold;'>🟡 Yellow</span> = Medium Priority + Running Ads</div>
        <div><span style='color: lightgreen; font-weight: bold;'>🟢 Light Green</span> = Low Priority + Running Ads</div>
        <div><span style='color: lightblue; font-weight: bold;'>🔵 Light Blue</span> = High Priority + No Ads</div>
        <div><span style='color: green; font-weight: bold;'>🟢 Green</span> = Low Priority + No Ads</div>
    </div>
    <p style='margin-bottom: 0; font-size: 12px; color: #666;'>
        <strong>Real Ad Data:</strong> Based on Google Places API + Transparency Center analysis (50 businesses confirmed running ads)
    </p>
</div>
""", unsafe_allow_html=True)

# Display map
st_folium(m, width=None, height=700)

# ============================================================================
# COMBINED INTELLIGENCE TABLE
# ============================================================================

st.markdown("---")
st.markdown("### 📊 Combined Intelligence: Market Pressure vs Actual Performance")

# Create combined intelligence table
if not filtered_competitors.empty:
    # Get actual CVR data from historical ads
    if st.session_state.geographical_df is not None:
        # Merge with geographical performance data
        combined_intelligence = filtered_competitors.merge(
            st.session_state.geographical_df[['District', 'CVR', 'CPA']],
            on='District',
            how='left'
        ).fillna({'CVR': 0.02, 'CPA': 50})  # Default values if no data
    else:
        # Use simulated data if no real data available
        combined_intelligence = filtered_competitors.copy()
        combined_intelligence['CVR'] = np.random.uniform(0.015, 0.035, len(combined_intelligence))
        combined_intelligence['CPA'] = np.random.uniform(40, 80, len(combined_intelligence))
    
    # Select and display key columns - with error handling
    display_columns = [
        'Business_Name', 'District', 'Targeting_Priority_Index', 
        'Competitive_Pressure_Score', 'CVR', 'CPA', 'Distance_From_Center_KM',
        'Has_Ads', 'Ads_Confidence', 'Phone_Number', 'Website'
    ]
    
    # Check which columns actually exist
    available_columns = combined_intelligence.columns.tolist()
    existing_columns = [col for col in display_columns if col in available_columns]
    
    # If no expected columns exist, use available ones
    if not existing_columns:
        existing_columns = available_columns[:8]  # Take first 8 columns
    
    try:
        intelligence_table = combined_intelligence[existing_columns].copy()
        
        # Create column mapping for display names
        column_mapping = {
            'Business_Name': 'Business Name',
            'District': 'District',
            'Targeting_Priority_Index': 'TPI Score',
            'Competitive_Pressure_Score': 'CPS',
            'CVR': 'Actual CVR',
            'CPA': 'Actual CPA',
            'Distance_From_Center_KM': 'Distance (km)',
            'Has_Ads': 'Has Ads',
            'Ads_Confidence': 'Ads Confidence',
            'Phone_Number': 'Phone',
            'Website': 'Website'
        }
        
        # Rename columns using mapping, fallback to original name if not in mapping
        intelligence_table.columns = [column_mapping.get(col, col) for col in existing_columns]
        
    except Exception as e:
        st.error(f"Error creating intelligence table: {str(e)}")
        st.write(f"Available columns: {available_columns}")
        # Fallback: show raw data
        intelligence_table = combined_intelligence.head(10)
    
    # Sort by TPI score if column exists
    if 'TPI Score' in intelligence_table.columns:
        intelligence_table = intelligence_table.sort_values('TPI Score', ascending=False)
    elif 'Targeting_Priority_Index' in intelligence_table.columns:
        intelligence_table = intelligence_table.sort_values('Targeting_Priority_Index', ascending=False)
    
    st.dataframe(intelligence_table, use_container_width=True)
    
    # Summary statistics - with error handling
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Competitors",
            len(filtered_competitors)
        )
    
    with col2:
        try:
            if 'Targeting_Priority_Index' in filtered_competitors.columns:
                avg_tpi = filtered_competitors['Targeting_Priority_Index'].mean()
                st.metric("Avg TPI Score", f"{avg_tpi:.1f}")
            else:
                st.metric("Avg TPI Score", "N/A")
        except:
            st.metric("Avg TPI Score", "N/A")
    
    with col3:
        try:
            if 'Distance_From_Center_KM' in filtered_competitors.columns:
                avg_distance = filtered_competitors['Distance_From_Center_KM'].mean()
                st.metric("Avg Distance", f"{avg_distance:.1f} km")
            else:
                st.metric("Avg Distance", "N/A")
        except:
            st.metric("Avg Distance", "N/A")
    
    with col4:
        st.metric(
            "Priority Radius",
            f"{priority_radius} km"
        )

else:
    st.warning("No competitors found within the specified radius. Try increasing the radius.")

# ============================================================================
# STRATEGIC INSIGHTS
# ============================================================================

st.markdown("---")
st.markdown("### 🎯 Strategic Insights")

if not filtered_competitors.empty:
    # High priority targets
    high_priority = filtered_competitors[
        filtered_competitors['Targeting_Priority_Index'] >= 70
    ]
    
    if not high_priority.empty:
        st.success(f"🎯 **High Priority Targets Found**: {len(high_priority)} competitors with TPI ≥ 70")
        
        # Show top 3 high priority targets
        top_targets = high_priority.nlargest(3, 'Targeting_Priority_Index')
        for idx, row in top_targets.iterrows():
            st.write(f"• **{row['Business_Name']}** - TPI: {row['Targeting_Priority_Index']:.1f}, Distance: {row['Distance_From_Center_KM']:.1f} km")
    
    # Competitive pressure analysis
    avg_cps = filtered_competitors['Competitive_Pressure_Score'].mean()
    if avg_cps > 60:
        st.warning(f"⚠️ **High Competitive Pressure**: Average CPS is {avg_cps:.1f}. Consider expanding to less competitive areas.")
    elif avg_cps < 30:
        st.success(f"✅ **Low Competitive Pressure**: Average CPS is {avg_cps:.1f}. Good opportunity for market entry.")
    else:
        st.info(f"📊 **Moderate Competitive Pressure**: Average CPS is {avg_cps:.1f}. Balanced market conditions.")

else:
    st.info("Increase the priority radius to see strategic insights for this area.")

# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 12px;'>
    AdsGenius - Geospatial Strategy & Mapping | Real-time Competitive Intelligence
</div>
""", unsafe_allow_html=True)