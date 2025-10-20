"""
Optimization Simulator & Scenario Testing
Monte Carlo simulations and negative keyword impact analysis
"""

import warnings
warnings.filterwarnings('ignore', category=FutureWarning)

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Import core utilities
from utils import (
    load_and_process_data,
    get_sector_config
)


# ============================================================================
# PAGE CONFIGURATION
# ============================================================================

st.set_page_config(
    page_title="Optimization Simulator",
    page_icon="🎲",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================================
# CUSTOM CSS
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
    .scenario-box {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border: 2px solid #dee2e6;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #d4edda;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #ffc107;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #e3f2fd;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #2196f3;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================================
# SESSION STATE CHECK
# ============================================================================

if 'sector' not in st.session_state:
    st.session_state.sector = 'Battery Dealers'
if 'city' not in st.session_state:
    st.session_state.city = 'Istanbul'


# ============================================================================
# MONTE CARLO SIMULATION FUNCTIONS
# ============================================================================

def run_monte_carlo_simulation(
    base_conversions: float,
    base_cost: float,
    base_revenue_per_conversion: float,
    bid_multiplier: float,
    num_trials: int = 1000,
    profit_margin: float = 0.25
) -> dict:
    """
    Run Monte Carlo simulation to estimate net profit distribution
    
    Args:
        base_conversions: Average daily conversions
        base_cost: Average daily cost
        base_revenue_per_conversion: Revenue per conversion
        bid_multiplier: Bid adjustment multiplier (e.g., 1.5 for +50%)
        num_trials: Number of simulation trials
        profit_margin: Profit margin percentage
    
    Returns:
        Dictionary with simulation results
    """
    results = []
    
    for _ in range(num_trials):
        # Simulate cost with bid multiplier and random variation
        # Higher bids = more cost but potentially more conversions
        simulated_cost = base_cost * bid_multiplier * np.random.uniform(0.85, 1.15)
        
        # Simulate conversions with elasticity to bid changes
        # Positive bid multiplier increases conversions but with diminishing returns
        elasticity = 0.3  # 10% bid increase = ~3% conversion increase
        conversion_multiplier = 1 + ((bid_multiplier - 1) * elasticity)
        simulated_conversions = base_conversions * conversion_multiplier * np.random.uniform(0.7, 1.3)
        
        # Calculate revenue and profit
        simulated_revenue = simulated_conversions * base_revenue_per_conversion
        simulated_gross_profit = simulated_revenue * profit_margin
        simulated_net_profit = simulated_gross_profit - simulated_cost
        
        results.append({
            'cost': simulated_cost,
            'conversions': simulated_conversions,
            'revenue': simulated_revenue,
            'gross_profit': simulated_gross_profit,
            'net_profit': simulated_net_profit,
            'roi': ((simulated_gross_profit - simulated_cost) / simulated_cost * 100) if simulated_cost > 0 else 0
        })
    
    results_df = pd.DataFrame(results)
    
    return {
        'results_df': results_df,
        'avg_net_profit': results_df['net_profit'].mean(),
        'min_net_profit': results_df['net_profit'].min(),
        'max_net_profit': results_df['net_profit'].max(),
        'std_net_profit': results_df['net_profit'].std(),
        'avg_roi': results_df['roi'].mean(),
        'percentile_25': results_df['net_profit'].quantile(0.25),
        'percentile_75': results_df['net_profit'].quantile(0.75),
        'probability_positive': (results_df['net_profit'] > 0).sum() / len(results_df) * 100
    }


def calculate_negative_keyword_impact(
    historical_df: pd.DataFrame,
    negative_keywords: list,
    estimated_waste_rate: float = 0.15
) -> dict:
    """
    Calculate the impact of implementing negative keywords
    
    Args:
        historical_df: Historical ads performance data
        negative_keywords: List of negative keywords to implement
        estimated_waste_rate: Estimated percentage of wasted clicks
    
    Returns:
        Dictionary with impact metrics
    """
    # Calculate baseline metrics
    total_clicks = historical_df['Clicks'].sum()
    total_cost = historical_df['Cost'].sum()
    total_conversions = historical_df['Conversions'].sum()
    avg_cvr = historical_df['CVR'].mean()
    
    # Estimate waste (clicks on negative keywords)
    estimated_waste_clicks = total_clicks * estimated_waste_rate * len(negative_keywords) / 10
    estimated_waste_cost = (estimated_waste_clicks / total_clicks) * total_cost if total_clicks > 0 else 0
    
    # Calculate improvements
    new_total_clicks = total_clicks - estimated_waste_clicks
    new_total_cost = total_cost - estimated_waste_cost
    
    # CVR improvement (removing low-quality traffic)
    cvr_improvement = 10  # Conservative 10% CVR improvement
    new_cvr = avg_cvr * (1 + cvr_improvement / 100)
    
    # New conversions (same conversion rate applied to better quality traffic)
    new_conversions = total_conversions * (1 + cvr_improvement / 100)
    
    return {
        'waste_clicks': estimated_waste_clicks,
        'waste_cost': estimated_waste_cost,
        'cost_reduction': estimated_waste_cost,
        'cost_reduction_pct': (estimated_waste_cost / total_cost * 100) if total_cost > 0 else 0,
        'cvr_improvement': cvr_improvement,
        'new_cvr': new_cvr,
        'additional_conversions': new_conversions - total_conversions,
        'total_conversions_new': new_conversions
    }


# ============================================================================
# DATA LOADING
# ============================================================================

with st.spinner(f"🔍 Loading data for {st.session_state.city}..."):
    try:
        data_dict = load_and_process_data(st.session_state.sector, st.session_state.city, cache_version=2)
        competitors_df = data_dict['Competitors_DF']
        historical_ads_df = data_dict['Historical_Ads_DF']
        
        # Get negative keywords from data dict or session state
        negative_keywords_list = data_dict.get('negative_keywords', [])
        if not negative_keywords_list:
            sector_config = get_sector_config(st.session_state.sector)
            negative_keywords_list = sector_config['negative_keywords']
        
        # Store in session state for later use
        st.session_state.negative_keywords = negative_keywords_list
        st.session_state.geographical_df = data_dict.get('geographical_df', None)
        st.session_state.search_terms_df = data_dict.get('search_terms_df', None)
            
    except Exception as e:
        st.error(f"❌ Error loading data: {str(e)}")
        st.stop()


# Get sector configuration
sector_config = get_sector_config(st.session_state.sector)


# ============================================================================
# MAIN CONTENT
# ============================================================================

st.markdown('<div class="main-header">🎲 Optimization Simulator & Scenario Testing</div>', unsafe_allow_html=True)

st.markdown("""
<div class="info-box">
<p><strong>Welcome to the Optimization Lab!</strong> Use this powerful simulator to test different bidding strategies 
and negative keyword implementations before applying them to your live campaigns. All simulations use Monte Carlo methods 
with 1,000+ trials for statistical reliability.</p>
</div>
""", unsafe_allow_html=True)


# ============================================================================
# SCENARIO A: BID MULTIPLIER TEST
# ============================================================================

st.markdown('<div class="sub-header">📊 Scenario A: Bid Multiplier Impact Analysis</div>', unsafe_allow_html=True)

col_left, col_right = st.columns([1, 2])

with col_left:
    st.markdown('<div class="scenario-box">', unsafe_allow_html=True)
    st.markdown("### ⚙️ Simulation Parameters")
    
    # District selection
    available_districts = sorted(historical_ads_df['Ads_District'].unique().tolist())
    selected_district = st.selectbox(
        "**Select Target District**",
        available_districts,
        help="Choose a district to simulate bid changes"
    )
    
    # Bid multiplier slider
    bid_multiplier = st.slider(
        "**Bid Multiplier**",
        min_value=-50,
        max_value=300,
        value=0,
        step=10,
        format="%d%%",
        help="Adjust bid amount: negative = bid reduction, positive = bid increase"
    )
    
    # Convert percentage to multiplier
    bid_multiplier_value = 1 + (bid_multiplier / 100)
    
    st.metric(
        label="Effective Bid Multiplier",
        value=f"{bid_multiplier_value:.2f}x",
        delta=f"{bid_multiplier:+d}%"
    )
    
    # Number of trials
    num_trials = st.select_slider(
        "**Simulation Trials**",
        options=[500, 1000, 2000, 5000],
        value=1000,
        help="More trials = more accurate results (but slower)"
    )
    
    # Run simulation button
    run_simulation = st.button("🚀 Run Monte Carlo Simulation", type="primary", use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

with col_right:
    if run_simulation or 'simulation_results' in st.session_state:
        # Get baseline data for selected district
        district_data = historical_ads_df[historical_ads_df['Ads_District'] == selected_district]
        
        if len(district_data) == 0:
            st.warning(f"⚠️ No historical data available for {selected_district}")
        else:
            # Calculate baseline metrics
            base_conversions = district_data['Conversions'].mean()
            base_cost = district_data['Cost'].mean()
            base_revenue_per_conversion = sector_config['avg_ticket']
            profit_margin = competitors_df['Profit_Margin_Estimate'].mean()
            
            # Run Monte Carlo simulation
            with st.spinner(f"🎲 Running {num_trials:,} Monte Carlo trials..."):
                simulation_results = run_monte_carlo_simulation(
                    base_conversions=base_conversions,
                    base_cost=base_cost,
                    base_revenue_per_conversion=base_revenue_per_conversion,
                    bid_multiplier=bid_multiplier_value,
                    num_trials=num_trials,
                    profit_margin=profit_margin
                )
            
            # Store in session state
            st.session_state.simulation_results = simulation_results
            
            # Display results
            st.markdown("### 📈 Simulation Results")
            
            # Summary metrics
            metric_col1, metric_col2, metric_col3 = st.columns(3)
            
            with metric_col1:
                st.metric(
                    label="💰 Average Net Profit",
                    value=f"₺{simulation_results['avg_net_profit']:.2f}",
                    delta=f"±₺{simulation_results['std_net_profit']:.2f}",
                    help="Mean daily net profit across all trials"
                )
            
            with metric_col2:
                st.metric(
                    label="📊 Profit Range",
                    value=f"₺{simulation_results['min_net_profit']:.2f} to ₺{simulation_results['max_net_profit']:.2f}",
                    help="Minimum and maximum net profit observed"
                )
            
            with metric_col3:
                st.metric(
                    label="✅ Success Probability",
                    value=f"{simulation_results['probability_positive']:.1f}%",
                    delta="Positive ROI",
                    help="Percentage of trials with positive net profit"
                )
            
            # Create histogram
            fig_histogram = go.Figure()
            
            fig_histogram.add_trace(go.Histogram(
                x=simulation_results['results_df']['net_profit'],
                nbinsx=50,
                name='Net Profit Distribution',
                marker=dict(
                    color=simulation_results['results_df']['net_profit'],
                    colorscale='RdYlGn',
                    line=dict(color='white', width=1)
                ),
                hovertemplate='Net Profit: ₺%{x:.2f}<br>Count: %{y}<extra></extra>'
            ))
            
            # Add vertical lines for key statistics
            fig_histogram.add_vline(
                x=simulation_results['avg_net_profit'],
                line_dash="solid",
                line_color="blue",
                annotation_text=f"Mean: ₺{simulation_results['avg_net_profit']:.2f}",
                annotation_position="top"
            )
            
            fig_histogram.add_vline(
                x=0,
                line_dash="dash",
                line_color="red",
                annotation_text="Break-even",
                annotation_position="bottom"
            )
            
            fig_histogram.update_layout(
                title=f'Daily Net Profit Distribution - {selected_district} ({num_trials:,} trials)<br>Bid Multiplier: {bid_multiplier_value:.2f}x ({bid_multiplier:+d}%)',
                xaxis_title='Daily Net Profit (₺)',
                yaxis_title='Frequency',
                height=500,
                showlegend=False
            )
            
            st.plotly_chart(fig_histogram, use_container_width=True)
            
            # Additional insights
            if simulation_results['avg_net_profit'] > 0:
                st.markdown(f"""
                <div class="success-box">
                <h4>✅ Positive Expected Return</h4>
                <p>The simulation indicates a <strong>positive expected return</strong> with this bid multiplier.</p>
                <ul>
                    <li>Average Daily Net Profit: <strong>₺{simulation_results['avg_net_profit']:.2f}</strong></li>
                    <li>Average ROI: <strong>{simulation_results['avg_roi']:.1f}%</strong></li>
                    <li>25th-75th Percentile Range: <strong>₺{simulation_results['percentile_25']:.2f} to ₺{simulation_results['percentile_75']:.2f}</strong></li>
                </ul>
                <p><strong>Recommendation:</strong> This bid adjustment appears favorable for {selected_district}.</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="warning-box">
                <h4>⚠️ Negative Expected Return</h4>
                <p>The simulation indicates a <strong>negative expected return</strong> with this bid multiplier.</p>
                <ul>
                    <li>Average Daily Net Loss: <strong>₺{abs(simulation_results['avg_net_profit']):.2f}</strong></li>
                    <li>Probability of Profit: <strong>{simulation_results['probability_positive']:.1f}%</strong></li>
                </ul>
                <p><strong>Recommendation:</strong> Consider reducing the bid multiplier or targeting a different district.</p>
                </div>
                """, unsafe_allow_html=True)


# ============================================================================
# SCENARIO B: NEGATIVE KEYWORD IMPACT
# ============================================================================

st.markdown('<div class="sub-header">🚫 Scenario B: Negative Keyword Impact Analysis</div>', unsafe_allow_html=True)

col_neg_left, col_neg_right = st.columns([1, 2])

with col_neg_left:
    st.markdown('<div class="scenario-box">', unsafe_allow_html=True)
    st.markdown("### ⚙️ Negative Keyword Selection")
    
    st.markdown(f"""
    **Available Negative Keywords for {st.session_state.sector}:**
    
    Select keywords that are likely to attract low-quality traffic or non-converting clicks.
    """)
    
    # Multi-select for negative keywords
    selected_negative_keywords = st.multiselect(
        "**Select Negative Keywords to Implement**",
        options=negative_keywords_list,
        default=negative_keywords_list[:3] if len(negative_keywords_list) >= 3 else negative_keywords_list,
        help="Choose keywords that should be excluded from your campaigns"
    )
    
    # Estimated waste rate slider
    estimated_waste_rate = st.slider(
        "**Estimated Waste Rate per Keyword**",
        min_value=5,
        max_value=30,
        value=15,
        step=1,
        format="%d%%",
        help="Estimate what % of clicks might be related to each negative keyword"
    )
    
    # Calculate impact button
    calculate_impact = st.button("🔍 Calculate Impact", type="primary", use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Display selected keywords
    if selected_negative_keywords:
        st.markdown("**Selected Keywords:**")
        for kw in selected_negative_keywords:
            st.markdown(f"- 🚫 `{kw}`")

with col_neg_right:
    if calculate_impact or 'negative_keyword_impact' in st.session_state:
        if not selected_negative_keywords:
            st.warning("⚠️ Please select at least one negative keyword to analyze.")
        else:
            # Calculate impact
            with st.spinner("🔍 Analyzing negative keyword impact..."):
                impact_results = calculate_negative_keyword_impact(
                    historical_df=historical_ads_df,
                    negative_keywords=selected_negative_keywords,
                    estimated_waste_rate=estimated_waste_rate / 100
                )
            
            # Store in session state
            st.session_state.negative_keyword_impact = impact_results
            
            # Display results
            st.markdown("### 📊 Projected Impact Analysis")
            
            # Impact metrics
            impact_col1, impact_col2, impact_col3 = st.columns(3)
            
            with impact_col1:
                st.metric(
                    label="💰 Cost Reduction",
                    value=f"₺{impact_results['cost_reduction']:.2f}",
                    delta=f"-{impact_results['cost_reduction_pct']:.1f}%",
                    delta_color="inverse",
                    help="Expected cost savings from eliminating wasted clicks"
                )
            
            with impact_col2:
                st.metric(
                    label="📈 CVR Improvement",
                    value=f"+{impact_results['cvr_improvement']:.1f}%",
                    delta=f"New CVR: {impact_results['new_cvr']:.2f}%",
                    help="Expected conversion rate improvement from better traffic quality"
                )
            
            with impact_col3:
                st.metric(
                    label="✅ Additional Conversions",
                    value=f"+{impact_results['additional_conversions']:.1f}",
                    delta="More conversions",
                    help="Expected increase in total conversions"
                )
            
            # Create before/after comparison chart
            baseline_total_cost = historical_ads_df['Cost'].sum()
            baseline_conversions = historical_ads_df['Conversions'].sum()
            baseline_cvr = historical_ads_df['CVR'].mean()
            
            comparison_data = pd.DataFrame({
                'Scenario': ['Before (Current)', 'After (With Negative Keywords)'],
                'Total Cost': [baseline_total_cost, baseline_total_cost - impact_results['cost_reduction']],
                'Total Conversions': [baseline_conversions, impact_results['total_conversions_new']],
                'Avg CVR': [baseline_cvr, impact_results['new_cvr']]
            })
            
            # Create subplots
            fig_comparison = make_subplots(
                rows=1, cols=3,
                subplot_titles=('Total Cost', 'Total Conversions', 'Conversion Rate'),
                specs=[[{"type": "bar"}, {"type": "bar"}, {"type": "bar"}]]
            )
            
            # Cost comparison
            fig_comparison.add_trace(
                go.Bar(
                    x=comparison_data['Scenario'],
                    y=comparison_data['Total Cost'],
                    name='Cost',
                    marker=dict(color=['#e74c3c', '#27ae60']),
                    text=[f"₺{x:.2f}" for x in comparison_data['Total Cost']],
                    textposition='outside',
                    hovertemplate='%{x}<br>Cost: ₺%{y:.2f}<extra></extra>'
                ),
                row=1, col=1
            )
            
            # Conversions comparison
            fig_comparison.add_trace(
                go.Bar(
                    x=comparison_data['Scenario'],
                    y=comparison_data['Total Conversions'],
                    name='Conversions',
                    marker=dict(color=['#3498db', '#27ae60']),
                    text=[f"{x:.0f}" for x in comparison_data['Total Conversions']],
                    textposition='outside',
                    hovertemplate='%{x}<br>Conversions: %{y:.0f}<extra></extra>'
                ),
                row=1, col=2
            )
            
            # CVR comparison
            fig_comparison.add_trace(
                go.Bar(
                    x=comparison_data['Scenario'],
                    y=comparison_data['Avg CVR'],
                    name='CVR',
                    marker=dict(color=['#f39c12', '#27ae60']),
                    text=[f"{x:.2f}%" for x in comparison_data['Avg CVR']],
                    textposition='outside',
                    hovertemplate='%{x}<br>CVR: %{y:.2f}%<extra></extra>'
                ),
                row=1, col=3
            )
            
            fig_comparison.update_layout(
                title_text='Before vs After: Negative Keyword Implementation Impact',
                showlegend=False,
                height=450
            )
            
            fig_comparison.update_yaxes(title_text="Cost (₺)", row=1, col=1)
            fig_comparison.update_yaxes(title_text="Conversions", row=1, col=2)
            fig_comparison.update_yaxes(title_text="CVR (%)", row=1, col=3)
            
            st.plotly_chart(fig_comparison, use_container_width=True)
            
            # Detailed breakdown
            st.markdown("### 📋 Detailed Impact Breakdown")
            
            breakdown_data = pd.DataFrame({
                'Metric': [
                    'Estimated Waste Clicks',
                    'Estimated Waste Cost',
                    'Cost Reduction',
                    'CVR Improvement',
                    'Additional Conversions',
                    'Monthly Cost Savings'
                ],
                'Value': [
                    f"{impact_results['waste_clicks']:.0f} clicks",
                    f"₺{impact_results['waste_cost']:.2f}",
                    f"₺{impact_results['cost_reduction']:.2f} ({impact_results['cost_reduction_pct']:.1f}%)",
                    f"+{impact_results['cvr_improvement']:.1f}%",
                    f"+{impact_results['additional_conversions']:.1f} conversions",
                    f"₺{impact_results['cost_reduction'] * 30:.2f}"
                ]
            })
            
            st.dataframe(breakdown_data, use_container_width=True, hide_index=True)
            
            # Recommendation
            potential_monthly_savings = impact_results['cost_reduction'] * 30
            potential_annual_savings = impact_results['cost_reduction'] * 365
            
            st.markdown(f"""
            <div class="success-box">
            <h4>💡 Implementation Recommendation</h4>
            <p>Implementing the selected <strong>{len(selected_negative_keywords)} negative keywords</strong> could result in:</p>
            <ul>
                <li>💰 <strong>Daily Savings:</strong> ₺{impact_results['cost_reduction']:.2f}</li>
                <li>📅 <strong>Monthly Savings:</strong> ₺{potential_monthly_savings:.2f}</li>
                <li>📆 <strong>Annual Savings:</strong> ₺{potential_annual_savings:.2f}</li>
                <li>📈 <strong>Quality Improvement:</strong> {impact_results['cvr_improvement']:.1f}% higher CVR</li>
                <li>✅ <strong>More Conversions:</strong> +{impact_results['additional_conversions']:.1f} conversions</li>
            </ul>
            <p><strong>Next Steps:</strong></p>
            <ol>
                <li>Add these keywords to your Google Ads negative keyword list</li>
                <li>Monitor performance for 2-4 weeks</li>
                <li>Adjust the list based on actual results</li>
            </ol>
            </div>
            """, unsafe_allow_html=True)


# ============================================================================
# NEGATIVE KEYWORDS REFERENCE
# ============================================================================

st.markdown('<div class="sub-header">📚 Negative Keywords Reference Guide</div>', unsafe_allow_html=True)

st.markdown(f"""
<div class="info-box">
<h4>🚫 Complete Negative Keyword List for {st.session_state.sector}</h4>
<p>These keywords are known to attract low-quality traffic that rarely converts. Consider implementing them in your campaigns:</p>
</div>
""", unsafe_allow_html=True)

# Display all negative keywords in columns
num_cols = 3
keyword_cols = st.columns(num_cols)

for idx, keyword in enumerate(negative_keywords_list):
    col_idx = idx % num_cols
    with keyword_cols[col_idx]:
        st.markdown(f"- 🚫 `{keyword}`")


# ============================================================================
# EXPORT SECTION
# ============================================================================

st.markdown('<div class="sub-header">📥 Export Simulation Results</div>', unsafe_allow_html=True)

export_col1, export_col2 = st.columns(2)

with export_col1:
    if 'simulation_results' in st.session_state:
        # Prepare CSV export
        sim_results_df = st.session_state.simulation_results['results_df']
        csv_data = sim_results_df.to_csv(index=False)
        
        st.download_button(
            label="⬇️ Download Monte Carlo Results (CSV)",
            data=csv_data,
            file_name=f"monte_carlo_simulation_{selected_district}_{bid_multiplier}pct.csv",
            mime="text/csv",
            use_container_width=True
        )

with export_col2:
    if 'negative_keyword_impact' in st.session_state:
        # Prepare negative keywords export
        neg_kw_text = "\n".join(selected_negative_keywords)
        
        st.download_button(
            label="⬇️ Download Negative Keywords (TXT)",
            data=neg_kw_text,
            file_name=f"negative_keywords_{st.session_state.sector.lower().replace(' ', '_')}.txt",
            mime="text/plain",
            use_container_width=True
        )


# ============================================================================
# FOOTER
# ============================================================================

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #7f8c8d; padding: 1rem;'>
    <p>🎲 <strong>Optimization Simulator Module</strong> | Advanced scenario testing with statistical modeling</p>
    <p>Monte Carlo simulations provide probabilistic forecasts - always validate with real campaign data</p>
</div>
""", unsafe_allow_html=True)


