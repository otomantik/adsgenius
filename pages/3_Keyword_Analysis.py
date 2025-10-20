"""
Keyword Analysis Page
Anahtar Kelime Analizi ve Reklam Performans Raporları
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np

# Import core data engine
from utils import (
    load_and_process_data,
    get_available_sectors,
    get_available_cities,
    get_sector_config
)

st.set_page_config(
    page_title="Keyword Analysis - Marketing Intelligence",
    page_icon="🔍",
    layout="wide"
)

st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
        margin-bottom: 2rem;
        border-bottom: 3px solid #1f77b4;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    .keyword-high {
        background-color: #ff6b6b;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-weight: bold;
    }
    .keyword-medium {
        background-color: #feca57;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-weight: bold;
    }
    .keyword-low {
        background-color: #48dbfb;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Page Header
st.markdown('<h1 class="main-header">🔍 Keyword Analysis & Performance Reports</h1>', unsafe_allow_html=True)

# Initialize session state
if 'keyword_data' not in st.session_state:
    st.session_state.keyword_data = {}

# Sidebar Configuration
st.sidebar.markdown("## 🎯 Keyword Analysis Configuration")
st.sidebar.markdown("---")

# Get current sector and city from session state
current_sector = st.session_state.get('sector', 'Battery Dealers')
current_city = st.session_state.get('city', 'Istanbul')

st.sidebar.info(f"**Current Analysis:** {current_sector} in {current_city}")

# Keyword Analysis Type Selection
analysis_type = st.sidebar.selectbox(
    "**Analysis Type**",
    ["Competitor Keywords", "Market Trends", "Performance Metrics", "Custom Keywords"],
    help="Select the type of keyword analysis to perform"
)

st.sidebar.markdown("---")

# Main Content Area
if analysis_type == "Competitor Keywords":
    st.markdown("## 🏢 Competitor Keyword Analysis")
    
    # Load competitor data
    try:
        competitors_df, intelligence_df = load_and_process_data(current_sector, current_city)
        
        if not competitors_df.empty:
            # Filter advertisers
            advertisers_df = competitors_df[competitors_df.get('is_running_ads', False)]
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Competitors", len(competitors_df))
            with col2:
                st.metric("Active Advertisers", len(advertisers_df))
            with col3:
                st.metric("Advertiser Rate", f"{(len(advertisers_df)/len(competitors_df)*100):.1f}%")
            with col4:
                avg_rating = competitors_df['rating'].mean() if 'rating' in competitors_df.columns else 0
                st.metric("Avg Rating", f"{avg_rating:.1f}")
            
            # Keyword analysis based on business names and types
            st.markdown("### 📊 Business Type Analysis")
            
            # Extract business types from data
            business_types = []
            if 'business_status' in competitors_df.columns:
                business_types = competitors_df['business_status'].value_counts()
            
            # Create business type distribution
            if not business_types.empty:
                fig = px.pie(
                    values=business_types.values,
                    names=business_types.index,
                    title="Business Type Distribution",
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Competitor analysis table
            st.markdown("### 🏆 Top Competitors by Rating")
            
            if 'rating' in competitors_df.columns:
                top_competitors = competitors_df.nlargest(10, 'rating')[['name', 'rating', 'user_ratings_total', 'is_running_ads']]
                st.dataframe(top_competitors, use_container_width=True)
            
        else:
            st.warning("No competitor data available for the selected sector.")
            
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")

elif analysis_type == "Market Trends":
    st.markdown("## 📈 Market Trend Analysis")
    
    # Generate sample trend data
    dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='M')
    
    # Sample keyword trends for different sectors
    keyword_trends = {
        'Battery Dealers': {
            'akü satış': np.random.normal(100, 20, len(dates)),
            'oto akü': np.random.normal(80, 15, len(dates)),
            'akü servisi': np.random.normal(60, 10, len(dates))
        },
        'Antique Dealers': {
            'antika satış': np.random.normal(120, 25, len(dates)),
            'vintage mobilya': np.random.normal(90, 18, len(dates)),
            'eski eşya': np.random.normal(70, 12, len(dates))
        },
        'Silver Dealers': {
            'gümüş takı': np.random.normal(110, 22, len(dates)),
            'gümüş ev eşyası': np.random.normal(85, 16, len(dates)),
            'gümüşçü': np.random.normal(65, 11, len(dates))
        }
    }
    
    if current_sector in keyword_trends:
        trends_data = keyword_trends[current_sector]
        
        # Create trend chart
        fig = go.Figure()
        
        for keyword, values in trends_data.items():
            fig.add_trace(go.Scatter(
                x=dates,
                y=values,
                mode='lines+markers',
                name=keyword,
                line=dict(width=3)
            ))
        
        fig.update_layout(
            title=f"Keyword Search Trends - {current_sector}",
            xaxis_title="Month",
            yaxis_title="Search Volume",
            hovermode='x unified',
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Keyword performance table
        st.markdown("### 📊 Keyword Performance Summary")
        
        performance_data = []
        for keyword, values in trends_data.items():
            performance_data.append({
                'Keyword': keyword,
                'Avg Volume': np.mean(values),
                'Growth Rate': ((values[-1] - values[0]) / values[0] * 100),
                'Volatility': np.std(values),
                'Trend': '📈' if values[-1] > values[0] else '📉'
            })
        
        performance_df = pd.DataFrame(performance_data)
        performance_df = performance_df.sort_values('Avg Volume', ascending=False)
        
        st.dataframe(performance_df, use_container_width=True)
    
    else:
        st.info(f"Trend data not available for {current_sector}. Please select a supported sector.")

elif analysis_type == "Performance Metrics":
    st.markdown("## 🎯 Performance Metrics Analysis")
    
    # Sample performance metrics
    metrics = {
        'Click-Through Rate (CTR)': {
            'Battery Dealers': {'value': 3.2, 'trend': '+0.5%'},
            'Antique Dealers': {'value': 2.8, 'trend': '+0.3%'},
            'Silver Dealers': {'value': 3.1, 'trend': '+0.7%'}
        },
        'Conversion Rate': {
            'Battery Dealers': {'value': 8.5, 'trend': '+1.2%'},
            'Antique Dealers': {'value': 6.2, 'trend': '+0.8%'},
            'Silver Dealers': {'value': 7.8, 'trend': '+1.0%'}
        },
        'Cost Per Click (CPC)': {
            'Battery Dealers': {'value': 2.4, 'trend': '-0.2 TL'},
            'Antique Dealers': {'value': 4.1, 'trend': '+0.3 TL'},
            'Silver Dealers': {'value': 3.7, 'trend': '+0.1 TL'}
        },
        'Return on Ad Spend (ROAS)': {
            'Battery Dealers': {'value': 4.2, 'trend': '+0.3'},
            'Antique Dealers': {'value': 3.8, 'trend': '+0.5'},
            'Silver Dealers': {'value': 4.0, 'trend': '+0.4'}
        }
    }
    
    # Display metrics for current sector
    if current_sector in metrics['Click-Through Rate (CTR)']:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📊 Current Performance")
            
            for metric_name, sector_data in metrics.items():
                if current_sector in sector_data:
                    data = sector_data[current_sector]
                    st.metric(
                        metric_name,
                        data['value'],
                        data['trend']
                    )
        
        with col2:
            st.markdown("### 📈 Cross-Sector Comparison")
            
            # Create comparison chart
            metric_names = list(metrics.keys())
            sector_values = []
            
            for metric_name in metric_names:
                if current_sector in metrics[metric_name]:
                    sector_values.append(metrics[metric_name][current_sector]['value'])
                else:
                    sector_values.append(0)
            
            fig = px.bar(
                x=metric_names,
                y=sector_values,
                title=f"Performance Comparison - {current_sector}",
                color=sector_values,
                color_continuous_scale='Viridis'
            )
            fig.update_layout(
                xaxis_tickangle=-45,
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
    
    else:
        st.warning(f"Performance data not available for {current_sector}")

elif analysis_type == "Custom Keywords":
    st.markdown("## 🔧 Custom Keyword Analysis")
    
    st.markdown("### 📝 Add Your Keywords")
    
    # Keyword input section
    col1, col2 = st.columns([2, 1])
    
    with col1:
        keyword_input = st.text_area(
            "Enter keywords (one per line):",
            placeholder="akü satış\noto akü\nakü servisi",
            height=150
        )
    
    with col2:
        st.markdown("**Keyword Categories:**")
        categories = st.multiselect(
            "Select categories:",
            ["Brand", "Product", "Service", "Location", "Long-tail"],
            default=["Product", "Service"]
        )
    
    if keyword_input:
        keywords = [k.strip() for k in keyword_input.split('\n') if k.strip()]
        
        if keywords:
            st.markdown("### 📊 Keyword Analysis Results")
            
            # Generate sample analysis for keywords
            analysis_data = []
            for keyword in keywords:
                # Simulate keyword difficulty and volume
                difficulty = np.random.uniform(30, 90)
                volume = np.random.uniform(100, 5000)
                cpc = np.random.uniform(1.5, 8.0)
                
                analysis_data.append({
                    'Keyword': keyword,
                    'Search Volume': f"{volume:,.0f}",
                    'Difficulty': f"{difficulty:.0f}%",
                    'CPC': f"{cpc:.2f} TL",
                    'Competition': 'High' if difficulty > 70 else 'Medium' if difficulty > 40 else 'Low'
                })
            
            analysis_df = pd.DataFrame(analysis_data)
            
            # Add styling to competition column
            def style_competition(val):
                if val == 'High':
                    return 'background-color: #ff6b6b; color: white; padding: 0.3rem 0.8rem; border-radius: 15px;'
                elif val == 'Medium':
                    return 'background-color: #feca57; color: white; padding: 0.3rem 0.8rem; border-radius: 15px;'
                else:
                    return 'background-color: #48dbfb; color: white; padding: 0.3rem 0.8rem; border-radius: 15px;'
            
            styled_df = analysis_df.style.applymap(style_competition, subset=['Competition'])
            st.dataframe(styled_df, use_container_width=True)
            
            # Keyword recommendations
            st.markdown("### 💡 Keyword Recommendations")
            
            # Generate recommendations based on sector
            sector_config = get_sector_config(current_sector)
            if sector_config:
                recommended_keywords = sector_config.get('business_types', [])
                
                if recommended_keywords:
                    st.markdown("**Suggested keywords based on your sector:**")
                    for keyword in recommended_keywords[:5]:
                        st.markdown(f"• {keyword}")
            
            # Export option
            st.markdown("### 📥 Export Analysis")
            csv_data = analysis_df.to_csv(index=False)
            st.download_button(
                label="Download Keyword Analysis CSV",
                data=csv_data,
                file_name=f"keyword_analysis_{current_sector.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem;'>
    <p>🔍 <strong>Keyword Analysis</strong> | Marketing Intelligence Platform</p>
    <p>Real-time competitive intelligence for data-driven marketing decisions</p>
</div>
""", unsafe_allow_html=True)
