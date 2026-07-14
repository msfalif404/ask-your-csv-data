import streamlit as st
import plotly.express as px

def render_kpi_cards(dataframe):
    total_gmv = dataframe['gmv'].sum()
    total_profit = dataframe['profit'].sum()
    total_qty = dataframe['quantity'].sum()
    profit_margin = (total_profit / total_gmv) * 100 if total_gmv > 0 else 0
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        _render_metric_card("Total GMV", f"${total_gmv:,.0f}")
        
    with col2:
        _render_metric_card("Total Profit", f"${total_profit:,.0f}")
        
    with col3:
        _render_metric_card("Profit Margin", f"{profit_margin:.2f}%")
        
    with col4:
        _render_metric_card("Total Quantity Sold", f"{total_qty:,.0f}")

def _render_metric_card(label, value):
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
    </div>
    """, unsafe_allow_html=True)

def render_charts(dataframe):
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.subheader("Top Categories by GMV")
        _render_top_categories_chart(dataframe)
        
    with col_chart2:
        st.subheader("Top 5 Sub-Categories by Profit")
        _render_top_subcategories_chart(dataframe)
        
    col_chart3, col_chart4 = st.columns(2)
    
    with col_chart3:
        st.subheader("GMV Distribution by Segment")
        _render_segment_distribution_chart(dataframe)
        
    with col_chart4:
        st.subheader("Sales Trend (Quantity by Region)")
        _render_region_sales_chart(dataframe)

def _render_top_categories_chart(dataframe):
    category_gmv_dataframe = dataframe.groupby('category', as_index=False)['gmv'].sum().sort_values('gmv', ascending=False)
    category_figure = px.bar(
        category_gmv_dataframe, 
        x='category', 
        y='gmv', 
        text_auto='.2s', 
        color='category',
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    category_figure.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)
    st.plotly_chart(category_figure, width='stretch')

def _render_top_subcategories_chart(dataframe):
    subcategory_profit_dataframe = dataframe.groupby('sub_category', as_index=False)['profit'].sum().sort_values('profit', ascending=False).head(5)
    subcategory_figure = px.bar(
        subcategory_profit_dataframe, 
        x='profit', 
        y='sub_category', 
        orientation='h', 
        text_auto='.2s', 
        color='profit', 
        color_continuous_scale='Greens'
    )
    subcategory_figure.update_layout(yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(subcategory_figure, width='stretch')

def _render_segment_distribution_chart(dataframe):
    segment_gmv_dataframe = dataframe.groupby('segment', as_index=False)['gmv'].sum()
    segment_figure = px.pie(
        segment_gmv_dataframe, 
        values='gmv', 
        names='segment', 
        hole=0.4, 
        color_discrete_sequence=px.colors.sequential.Teal
    )
    st.plotly_chart(segment_figure, width='stretch')

def _render_region_sales_chart(dataframe):
    region_quantity_dataframe = dataframe.groupby('region', as_index=False)['quantity'].sum().sort_values('quantity', ascending=False)
    region_figure = px.bar(
        region_quantity_dataframe, 
        x='region', 
        y='quantity', 
        text_auto='.2s', 
        color='region',
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    st.plotly_chart(region_figure, width='stretch')
