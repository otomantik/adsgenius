"""
Search Terms Analysis Page
Arama Terimleri Analizi - Gereksiz vs Dönüşüm Getiren Terimler
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np
import os

st.set_page_config(
    page artwork="📊 Search Terms Analysis",
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
    .high-performance {
        background-color: #00b894;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-weight: bold;
    }
    .medium-performance {
        background-color: #fdcb6e;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-weight: bold;
    }
    .low-performance {
        background-color: #e17055;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-weight: bold;
    }
    .waste-keyword {
        background-color: #636e72;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Page Header
st.markdown('<h1 class="main-header">🔍 Search Terms Analysis</h1>', unsafe_allow_html=True)
st.markdown('<h2 style="text-align: center; color: #666;">Gereksiz vs Dönüşüm Getiren Arama Terimleri Analizi</h2>', unsafe_allow_html=True)

# Initialize session state
if 'search_terms_data' not in st.session_state:
    st.session_state.search_terms_data = None

# Sidebar Configuration
st.sidebar.markdown("## 🎯 Analysis Configuration")
st.sidebar.markdown("---")

# File selection options
st.sidebar.markdown("### 📁 Data Source")

upload_option = st.sidebar.radio(
    "Choose data source:",
    ["Upload CSV File", "Use Existing File"],
    help="Upload your own CSV or use existing data"
)

selected_file = None
uploaded_df = None

if upload_option == "Upload CSV File":
    st.sidebar.markdown("### 📤 Upload Your CSV")
    
    uploaded_file = st.sidebar.file_uploader(
        "Choose a CSV file",
        type="csv",
        help="Upload your search terms CSV file with columns: Arama terimi, Maliyet, Dönüşümler, Tıklamalar, Gösterimler"
    )
    
    if uploaded_file is not None:
        try:
            uploaded_df = pd.read_csv(uploaded_file, encoding='utf-8-sig')
            st.sidebar.success(f"✅ File uploaded: {uploaded_file.name}")
            st.sidebar.info(f"📊 {len(uploaded_df)} keywords loaded")
        except Exception as e:
            st.sidebar.error(f"❌ Error loading file: {str(e)}")
            st.stop()
    else:
        st.sidebar.info("👆 Please upload a CSV file to continue")
        st.stop()

else:
    # Use existing files
    available_files = []
    for file in os.listdir('data'):
        if 'arama_terimleri' in file.lower() and file.endswith('.csv'):
            available_files.append(file)

    if available_files:
        selected_file = st.sidebar.selectbox(
            "**Select Search Terms File**",
            available_files,
            help="Choose the search terms CSV file to analyze"
        )
    else:
        st.sidebar.error("No search terms CSV files found in data/ folder")
        st.stop()

# Analysis parameters
st.sidebar.markdown("### 📊 Analysis Parameters")

# Performance thresholds
min_conversion_rate = st.sidebar.slider(
    "Minimum Conversion Rate (%)",
    min_value=0.1,
    max_value=10.0,
    value=2.0,
    step=0.1,
    help="Minimum conversion rate to consider a keyword as performing"
)

max_cpc_threshold = st.sidebar.slider(
    "Maximum CPC Threshold (TL)",
    min_value=1.0,
    max_value=20.0,
    value=8.0,
    step=0.5,
    help="Maximum cost per click to consider a keyword as efficient"
)

min_impressions = st.sidebar.slider(
    "Minimum Impressions",
    min_value=100,
    max_value=10000,
    value=1000,
    step=100,
    help="Minimum impressions to consider a keyword as significant"
)

st.sidebar.markdown("---")

# Load and analyze data
@st.cache_data
def load_and_analyze_search_terms(file_path=None, uploaded_df=None):
    """Load and analyze search terms data"""
    try:
        if uploaded_df is not None:
            df = uploaded_df.copy()
        else:
            df = pd.read_csv(file_path, encoding='utf-8-sig')
        
        # Clean column names
        df.columns = df.columns.str.strip()
        
        # Calculate performance metrics
        df['CPC'] = df['Maliyet'] / df['Tıklamalar']
        df['Conversion_Rate'] = (df['Dönüşümler'] / df['Tıklamalar']) * 100
        df['CTR'] = (df['Tıklamalar'] / df['Gösterimler']) * 100
        df['Cost_Per_Conversion'] = df['Maliyet'] / df['Dönüşümler']
        df['ROAS'] = (df['Dönüşümler'] * 850) / df['Maliyet']  # Assuming 850 TL avg ticket
        
        # Classify keywords
        def classify_keyword(row):
            if row['Conversion_Rate'] >= min_conversion_rate and row['CPC'] <= max_cpc_threshold and row['Gösterimler'] >= min_impressions:
                return 'High Performance'
            elif row['Conversion_Rate'] >= min_conversion_rate * 0.5 and row['CPC'] <= max_cpc_threshold * 1.5:
                return 'Medium Performance'
            elif row['Conversion_Rate'] < min_conversion_rate * 0.3 or row['CPC'] > max_cpc_threshold * 2:
                return 'Waste Keywords'
            else:
                return 'Low Performance'
        
        df['Performance_Category'] = df.apply(classify_keyword, axis=1)
        
        return df
        
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None

# Load data
if upload_option == "Upload CSV File" and uploaded_df is not None:
    df = load_and_analyze_search_terms(uploaded_df=uploaded_df)
else:
    df = load_and_analyze_search_terms(file_path=f'data/{selected_file}')

if df is not None:
    st.session_state.search_terms_data = df
    
    # Main metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Total Keywords", len(df))
    with col2:
        st.metric("Total Cost", f"{df['Maliyet'].sum():,.0f} TL")
    with col3:
        st.metric("Total Conversions", f"{df['Dönüşümler'].sum():,.0f}")
    with col4:
        st.metric("Avg CPC", f"{df['CPC'].mean():.2f} TL")
    with col5:
        st.metric("Avg Conversion Rate", f"{df['Conversion_Rate'].mean():.2f}%")
    
    st.markdown("---")
    
    # Performance distribution
    st.markdown("## 📊 Performance Distribution")
    
    performance_counts = df['Performance_Category'].value_counts()
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Pie chart
        fig_pie = px.pie(
            values=performance_counts.values,
            names=performance_counts.index,
            title="Keyword Performance Distribution",
            color_discrete_map={
                'High Performance': '#00b894',
                'Medium Performance': '#fdcb6e',
                'Low Performance': '#e17055',
                'Waste Keywords': '#636e72'
            }
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        # Bar chart
        fig_bar = px.bar(
            x=performance_counts.index,
            y=performance_counts.values,
            title="Keyword Performance Count",
            color=performance_counts.index,
            color_discrete_map={
                'High Performance': '#00b894',
                'Medium Performance': '#fdcb6e',
                'Low Performance': '#e17055',
                'Waste Keywords': '#636e72'
            }
        )
        fig_bar.update_layout(showlegend=False)
        st.plotly_chart(fig_bar, use_container_width=True)
    
    # Detailed analysis
    st.markdown("## 🔍 Detailed Analysis")
    
    # Top performers
    st.markdown("### 🏆 Top Performing Keywords")
    top_performers = df[df['Performance_Category'] == 'High Performance'].nlargest(10, 'Conversion_Rate')
    
    if not top_performers.empty:
        st.dataframe(
            top_performers[['Arama terimi', 'Conversion_Rate', 'CPC', 'Dönüşümler', 'Maliyet', 'ROAS']],
            use_container_width=True
        )
    else:
        st.info("No high performing keywords found with current criteria.")
    
    # Waste keywords
    st.markdown("### 🗑️ Waste Keywords (High Cost, Low Performance)")
    waste_keywords = df[df['Performance_Category'] == 'Waste Keywords'].nsmallest(10, 'Conversion_Rate')
    
    if not waste_keywords.empty:
        st.dataframe(
            waste_keywords[['Arama terimi', 'Conversion_Rate', 'CPC', 'Dönüşümler', 'Maliyet']],
            use_container_width=True
        )
        
        # Calculate potential savings
        waste_cost = waste_keywords['Maliyet'].sum()
        st.metric("Potential Cost Savings", f"{waste_cost:,.0f} TL")
    else:
        st.info("No waste keywords found with current criteria.")
    
    # Performance scatter plot
    st.markdown("### 📈 Performance Scatter Analysis")
    
    fig_scatter = px.scatter(
        df,
        x='CPC',
        y='Conversion_Rate',
        size='Maliyet',
        color='Performance_Category',
        hover_data=['Arama terimi', 'Tıklamalar', 'Dönüşümler'],
        title="CPC vs Conversion Rate Analysis",
        color_discrete_map={
            'High Performance': '#00b894',
            'Medium Performance': '#fdcb6e',
            'Low Performance': '#e17055',
            'Waste Keywords': '#636e72'
        }
    )
    
    # Add threshold lines
    fig_scatter.add_hline(y=min_conversion_rate, line_dash="dash", line_color="red", annotation_text=f"Min Conv Rate: {min_conversion_rate}%")
    fig_scatter.add_vline(x=max_cpc_threshold, line_dash="dash", line_color="red", annotation_text=f"Max CPC: {max_cpc_threshold} TL")
    
    st.plotly_chart(fig_scatter, use_container_width=True)
    
    # Recommendations
    st.markdown("## 💡 Recommendations")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### ✅ Keep These Keywords")
        keep_keywords = df[df['Performance_Category'] == 'High Performance']
        if not keep_keywords.empty:
            st.markdown(f"**{len(keep_keywords)} keywords** performing well:")
            for keyword in keep_keywords['Arama terimi'].head(5):
                st.markdown(f"• {keyword}")
        else:
            st.info("No high performing keywords to keep.")
    
    with col2:
        st.markdown("### ❌ Consider Removing These Keywords")
        remove_keywords = df[df['Performance_Category'] == 'Waste Keywords']
        if not remove_keywords.empty:
            st.markdown(f"**{len(remove_keywords)} keywords** wasting budget:")
            for keyword in remove_keywords['Arama terimi'].head(5):
                st.markdown(f"• {keyword}")
        else:
            st.info("No waste keywords to remove.")
    
    # Export options
    st.markdown("## 📥 Export Analysis")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Export all data
        csv_data = df.to_csv(index=False)
        st.download_button(
            label="📊 Download Full Analysis",
            data=csv_data,
            file_name=f"search_terms_analysis_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    
    with col2:
        # Export high performers
        if not top_performers.empty:
            high_perf_csv = top_performers.to_csv(index=False)
            st.download_button(
                label="🏆 Download Top Performers",
                data=high_perf_csv,
                file_name=f"top_performers_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    
    with col3:
        # Export waste keywords
        if not waste_keywords.empty:
            waste_csv = waste_keywords.to_csv(index=False)
            st.download_button(
                label="🗑️ Download Waste Keywords",
                data=waste_csv,
                file_name=f"waste_keywords_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )

else:
    st.error("Failed to load search terms data. Please check the file format.")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem;'>
    <p>🔍 <strong>Search Terms Analysis</strong> | Marketing Intelligence Platform</p>
    <p>Data-driven keyword optimization for maximum ROI</p>
</div>
""", unsafe_allow_html=True)
