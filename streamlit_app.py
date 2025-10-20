"""
Global/Local Marketing Intelligence Platform
Executive Command Center - Main Dashboard

Professional Command Center for Google Ads Experts
"""

import warnings
warnings.filterwarnings('ignore', category=FutureWarning)

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Import core data engine
from utils import (
    load_and_process_data,
    get_available_sectors,
    get_available_cities,
    get_sector_config
)


# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Marketing Intelligence Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================================
# CUSTOM CSS STYLING
# ============================================================================

st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
        border-bottom: 3px solid #ff7f0e;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.8rem;
        font-weight: 600;
        color: #2c3e50;
        margin-top: 2rem;
        margin-bottom: 1rem;
        border-left: 5px solid #1f77b4;
        padding-left: 1rem;
    }
    .metric-container {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .info-box {
        background-color: #e3f2fd;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #2196f3;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3e0;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #ff9800;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================

def initialize_session_state():
    """Initialize session state variables for cross-page persistence"""
    if 'sector' not in st.session_state:
        st.session_state.sector = 'Battery Dealers'
    if 'city' not in st.session_state:
        st.session_state.city = 'Istanbul'
    if 'data_loaded' not in st.session_state:
        st.session_state.data_loaded = False

initialize_session_state()


# ============================================================================
# SIDEBAR - CONTROL PANEL
# ============================================================================

st.sidebar.markdown("## 🎯 Control Panel")
st.sidebar.markdown("---")

# Sector Selection
available_sectors = get_available_sectors()
selected_sector = st.sidebar.selectbox(
    "**Business Sector**",
    available_sectors,
    index=available_sectors.index(st.session_state.sector),
    help="Select the business sector for market analysis"
)

# City Selection
available_cities = get_available_cities()
selected_city = st.sidebar.selectbox(
    "**Target City**",
    available_cities,
    index=available_cities.index(st.session_state.city),
    help="Select the target city for geographic analysis"
)

# Update session state if selections changed
if selected_sector != st.session_state.sector or selected_city != st.session_state.city:
    st.session_state.sector = selected_sector
    st.session_state.city = selected_city
    st.session_state.data_loaded = False

st.sidebar.markdown("---")

# Load Data Button
if st.sidebar.button("🔄 Refresh Data", use_container_width=True):
    st.cache_data.clear()
    st.session_state.data_loaded = False
    st.rerun()

# Information Panel
st.sidebar.markdown("### ℹ️ Platform Info")
st.sidebar.info(f"""
**Current Configuration:**
- Sector: {st.session_state.sector}
- City: {st.session_state.city}
- Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}
""")

st.sidebar.markdown("---")
st.sidebar.markdown("### 📱 Navigation")
st.sidebar.info("""
Use the sidebar to navigate between:
1. **Executive Dashboard** (This Page)
2. **Competitive Map** - Geospatial Strategy
3. **Optimization Simulator** - Scenario Testing
""")


# ============================================================================
# MAIN CONTENT - EXECUTIVE COMMAND CENTER
# ============================================================================

st.markdown('<div class="main-header">📊 Executive Command Center</div>', unsafe_allow_html=True)

# Welcome message
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown(f"""
    <div class="info-box">
    <h3 style='text-align: center; margin: 0;'>Marketing Intelligence Platform</h3>
    <p style='text-align: center; margin: 0.5rem 0 0 0;'>
    Comprehensive Google Ads Strategy Dashboard for <strong>{st.session_state.sector}</strong> in <strong>{st.session_state.city}</strong>
    </p>
    </div>
    """, unsafe_allow_html=True)


# ============================================================================
# DATA LOADING
# ============================================================================

with st.spinner(f"🔍 Loading market intelligence for {st.session_state.sector} in {st.session_state.city}..."):
    try:
        data_dict = load_and_process_data(st.session_state.sector, st.session_state.city, cache_version=2)
        competitors_df = data_dict['Competitors_DF']
        historical_ads_df = data_dict['Historical_Ads_DF']
        
        # Store additional data in session state for other pages
        st.session_state.negative_keywords = data_dict.get('negative_keywords', [])
        st.session_state.geographical_df = data_dict.get('geographical_df', None)
        st.session_state.search_terms_df = data_dict.get('search_terms_df', None)
        st.session_state.data_loaded = True
    except Exception as e:
        st.error(f"❌ Error loading data: {str(e)}")
        st.stop()


# ============================================================================
# SECTION 1: LIVE KPI DASHBOARD
# ============================================================================

st.markdown('<div class="sub-header">📈 Live KPI Dashboard</div>', unsafe_allow_html=True)

# Calculate KPIs
max_tpi = competitors_df['Targeting_Priority_Index'].max()
avg_cpa = historical_ads_df['CPA'].mean()
avg_ctr = historical_ads_df['CTR'].mean()
total_revenue_potential = competitors_df['Daily_Revenue_Estimate'].sum()
total_conversions = historical_ads_df['Conversions'].sum()

# Get sector configuration for calculations
sector_config = get_sector_config(st.session_state.sector)
avg_ticket_value = sector_config['avg_ticket']

# Display KPIs in columns
kpi_col1, kpi_col2, kpi_col3, kpi_col4, kpi_col5 = st.columns(5)

with kpi_col1:
    st.metric(
        label="🎯 Max TPI Score",
        value=f"{max_tpi:.1f}",
        delta="High Priority",
        help="Maximum Targeting Priority Index across all competitors"
    )

with kpi_col2:
    st.metric(
        label="💰 Actual CPA",
        value=f"₺{avg_cpa:.2f}",
        delta=f"{((avg_cpa / avg_ticket_value) * 100):.1f}% of ticket",
        delta_color="inverse",
        help="Average Cost Per Acquisition from historical ads"
    )

with kpi_col3:
    st.metric(
        label="👆 Actual CTR",
        value=f"{avg_ctr:.2f}%",
        delta="Industry Avg: 5%",
        delta_color="normal",
        help="Average Click-Through Rate from historical campaigns"
    )

with kpi_col4:
    st.metric(
        label="💵 Daily Revenue Potential",
        value=f"₺{total_revenue_potential:,.0f}",
        delta="Market Estimate",
        help="Total estimated daily revenue potential across all locations"
    )

with kpi_col5:
    st.metric(
        label="✅ Total Conversions",
        value=f"{total_conversions}",
        delta="Last 90 Days",
        help="Total conversions from historical ad campaigns"
    )


# ============================================================================
# SECTION 2: PLOTLY SUNBURST CHART - Revenue Hierarchy
# ============================================================================

st.markdown('<div class="sub-header">🌞 Revenue Distribution by District & TPI</div>', unsafe_allow_html=True)

# Create TPI categories for better visualization
competitors_df['TPI_Category'] = pd.cut(
    competitors_df['Targeting_Priority_Index'],
    bins=[0, 33, 66, 100],
    labels=['Low Priority (0-33)', 'Medium Priority (34-66)', 'High Priority (67-100)']
)

# Aggregate data for sunburst
sunburst_data = competitors_df.groupby(['District', 'TPI_Category'], observed=True).agg({
    'Daily_Revenue_Estimate': 'sum',
    'Targeting_Priority_Index': 'mean'
}).reset_index()

# Filter out any zero or negative values to prevent ZeroDivisionError
sunburst_data = sunburst_data[sunburst_data['Daily_Revenue_Estimate'] > 0].copy()

# Create sunburst chart
fig_sunburst = px.sunburst(
    sunburst_data,
    path=['District', 'TPI_Category'],
    values='Daily_Revenue_Estimate',
    color='Targeting_Priority_Index',
    color_continuous_scale='RdYlGn',
    title=f'Simulated Revenue Distribution: {st.session_state.sector} in {st.session_state.city}',
    hover_data={'Targeting_Priority_Index': ':.2f'},
)

fig_sunburst.update_traces(
    textinfo='label+percent parent',
    hovertemplate='<b>%{label}</b><br>Revenue: ₺%{value:,.2f}<br>Avg TPI: %{color:.2f}<extra></extra>'
)

fig_sunburst.update_layout(
    height=600,
    font=dict(size=12),
    coloraxis_colorbar=dict(
        title="Avg TPI Score",
        thicknessmode="pixels",
        thickness=15,
        lenmode="pixels",
        len=300
    )
)

st.plotly_chart(fig_sunburst, use_container_width=True)


# ============================================================================
# SECTION 3: TREND ANALYSIS - Cost vs Conversions Over Time
# ============================================================================

st.markdown('<div class="sub-header">📊 Trend Analysis: Cost vs Conversions Over Time</div>', unsafe_allow_html=True)

# Aggregate by date
daily_trends = historical_ads_df.groupby('Date').agg({
    'Cost': 'sum',
    'Conversions': 'sum',
    'Clicks': 'sum',
    'Impressions': 'sum'
}).reset_index()

# Create dual-axis line chart
fig_trends = go.Figure()

# Add Cost line
fig_trends.add_trace(go.Scatter(
    x=daily_trends['Date'],
    y=daily_trends['Cost'],
    name='Daily Cost',
    mode='lines+markers',
    line=dict(color='#e74c3c', width=2),
    marker=dict(size=6),
    yaxis='y',
    hovertemplate='Date: %{x}<br>Cost: ₺%{y:,.2f}<extra></extra>'
))

# Add Conversions line
fig_trends.add_trace(go.Scatter(
    x=daily_trends['Date'],
    y=daily_trends['Conversions'],
    name='Daily Conversions',
    mode='lines+markers',
    line=dict(color='#27ae60', width=2),
    marker=dict(size=6),
    yaxis='y2',
    hovertemplate='Date: %{x}<br>Conversions: %{y}<extra></extra>'
))

# Update layout with dual axis
fig_trends.update_layout(
    title='Historical Performance: Cost vs Conversions (Last 90 Days)',
    xaxis=dict(title='Date'),
    yaxis=dict(
        title='Cost (₺)',
        titlefont=dict(color='#e74c3c'),
        tickfont=dict(color='#e74c3c')
    ),
    yaxis2=dict(
        title='Conversions',
        titlefont=dict(color='#27ae60'),
        tickfont=dict(color='#27ae60'),
        anchor='x',
        overlaying='y',
        side='right'
    ),
    hovermode='x unified',
    height=500,
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    )
)

st.plotly_chart(fig_trends, use_container_width=True)


# ============================================================================
# SECTION 4: DETAILED DATA TABLES
# ============================================================================

st.markdown('<div class="sub-header">📋 Detailed Market Intelligence</div>', unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["🗺️ Top Competitors by TPI", "📊 Best Performing Districts", "🔍 Recent Ads Performance"])

with tab1:
    st.markdown("#### Top 20 High-Priority Targets")
    
    top_competitors = competitors_df.nlargest(20, 'Targeting_Priority_Index')[
        ['District', 'Business_Name', 'Targeting_Priority_Index', 
         'Competitive_Pressure_Score', 'Daily_Revenue_Estimate', 
         'Distance_From_Center_KM', 'Simulated_Avg_Rating']
    ].copy()
    
    # Format columns
    top_competitors['Daily_Revenue_Estimate'] = top_competitors['Daily_Revenue_Estimate'].apply(lambda x: f"₺{x:,.2f}")
    top_competitors['Distance_From_Center_KM'] = top_competitors['Distance_From_Center_KM'].apply(lambda x: f"{x:.2f} km")
    
    st.dataframe(
        top_competitors,
        use_container_width=True,
        height=400,
        hide_index=True
    )

with tab2:
    st.markdown("#### District Performance Summary")
    
    district_summary = competitors_df.groupby('District').agg({
        'Targeting_Priority_Index': 'mean',
        'Daily_Revenue_Estimate': 'sum',
        'Competitive_Pressure_Score': 'mean',
        'Competitor_ID': 'count'
    }).reset_index()
    
    district_summary.columns = ['District', 'Avg TPI', 'Total Revenue Potential', 'Avg CPS', 'Competitor Count']
    district_summary = district_summary.sort_values('Avg TPI', ascending=False)
    
    # Format columns
    district_summary['Total Revenue Potential'] = district_summary['Total Revenue Potential'].apply(lambda x: f"₺{x:,.2f}")
    district_summary['Avg TPI'] = district_summary['Avg TPI'].apply(lambda x: f"{x:.2f}")
    district_summary['Avg CPS'] = district_summary['Avg CPS'].apply(lambda x: f"{x:.2f}")
    
    st.dataframe(
        district_summary,
        use_container_width=True,
        height=400,
        hide_index=True
    )

with tab3:
    st.markdown("#### Last 20 Ad Campaign Entries")
    
    recent_ads = historical_ads_df.nlargest(20, 'Date')[
        ['Date', 'Ads_District', 'Search_Term', 'Impressions', 
         'Clicks', 'Conversions', 'Cost', 'CTR', 'CVR', 'CPA']
    ].copy()
    
    # Format columns
    recent_ads['Date'] = recent_ads['Date'].dt.strftime('%Y-%m-%d')
    recent_ads['Cost'] = recent_ads['Cost'].apply(lambda x: f"₺{x:.2f}")
    recent_ads['CPA'] = recent_ads['CPA'].apply(lambda x: f"₺{x:.2f}" if x > 0 else "N/A")
    recent_ads['CTR'] = recent_ads['CTR'].apply(lambda x: f"{x:.2f}%")
    recent_ads['CVR'] = recent_ads['CVR'].apply(lambda x: f"{x:.2f}%")
    
    st.dataframe(
        recent_ads,
        use_container_width=True,
        height=400,
        hide_index=True
    )


# ============================================================================
# SECTION 5: INSIGHTS & RECOMMENDATIONS
# ============================================================================

st.markdown('<div class="sub-header">💡 Strategic Insights</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    # Top district insight
    top_district = district_summary.iloc[0]
    st.markdown(f"""
    <div class="info-box">
    <h4>🎯 Highest Priority District</h4>
    <p><strong>{top_district['District']}</strong> shows the highest targeting potential with an average TPI of <strong>{top_district['Avg TPI']}</strong>.</p>
    <p>Consider increasing bid multipliers by 20-30% for this district.</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    # CPA optimization insight
    optimal_cpa = avg_ticket_value * 0.20  # 20% of ticket value
    st.markdown(f"""
    <div class="warning-box">
    <h4>💰 CPA Optimization Opportunity</h4>
    <p>Current CPA: <strong>₺{avg_cpa:.2f}</strong></p>
    <p>Target CPA: <strong>₺{optimal_cpa:.2f}</strong> (20% of ticket value)</p>
    <p>Potential savings: <strong>₺{(avg_cpa - optimal_cpa) * total_conversions:,.2f}</strong></p>
    </div>
    """, unsafe_allow_html=True)


# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #7f8c8d; padding: 1rem;'>
    <p><strong>Marketing Intelligence Platform v1.0</strong></p>
    <p>Developed for Google Ads Professionals | Data updated: {}</p>
    <p>⚠️ Currently using simulated data. Integrate with Google Ads API for live data.</p>
</div>
""".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')), unsafe_allow_html=True)

