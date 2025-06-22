import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

def create_velocity_chart(data: pd.DataFrame):
    """
    Create a chart showing sales velocity distribution by category
    """
    # Category distribution pie chart
    category_counts = data['Category'].value_counts()
    
    colors = {
        'Slow Moving': '#FF6B6B',
        'Fast Moving': '#4ECDC4', 
        'Best Selling': '#45B7D1'
    }
    
    fig = px.pie(
        values=category_counts.values,
        names=category_counts.index,
        title="Product Distribution by Sales Velocity",
        color=category_counts.index,
        color_discrete_map=colors
    )
    
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>'
    )
    
    fig.update_layout(
        showlegend=True,
        height=400,
        font=dict(size=14)
    )
    
    return fig

def create_stock_level_chart(data: pd.DataFrame):
    """
    Create a chart showing stock level distribution
    """
    # Stock status distribution
    stock_counts = data['Stock_Status'].value_counts()
    
    colors = {
        'Critical': '#FF4444',
        'Low': '#FF8C00',
        'Normal': '#32CD32',
        'High': '#4169E1'
    }
    
    fig = px.bar(
        x=stock_counts.index,
        y=stock_counts.values,
        title="Stock Level Distribution",
        color=stock_counts.index,
        color_discrete_map=colors,
        labels={'x': 'Stock Status', 'y': 'Number of Products'}
    )
    
    fig.update_traces(
        hovertemplate='<b>%{x}</b><br>Products: %{y}<extra></extra>'
    )
    
    fig.update_layout(
        showlegend=False,
        height=400,
        xaxis_title="Stock Status",
        yaxis_title="Number of Products"
    )
    
    return fig

def create_reorder_chart(data: pd.DataFrame):
    """
    Create a chart showing reorder recommendations
    """
    # Filter products that need reordering
    reorder_data = data[data['Reorder_Status'].isin(['Reorder Now', 'Reorder Soon'])]
    
    if reorder_data.empty:
        # Create empty chart with message
        fig = go.Figure()
        fig.add_annotation(
            text="No products require reordering at this time",
            xref="paper", yref="paper",
            x=0.5, y=0.5, xanchor='center', yanchor='middle',
            showarrow=False,
            font=dict(size=16)
        )
        fig.update_layout(
            title="Reorder Recommendations",
            height=400,
            xaxis=dict(visible=False),
            yaxis=dict(visible=False)
        )
        return fig
    
    # Sort by reorder quantity for better visualization
    reorder_data = reorder_data.nlargest(20, 'Reorder_Quantity')
    
    colors = {
        'Reorder Now': '#FF4444',
        'Reorder Soon': '#FF8C00'
    }
    
    fig = px.bar(
        reorder_data,
        x='Product_Name',
        y='Reorder_Quantity',
        color='Reorder_Status',
        title="Top Products Requiring Reorder",
        color_discrete_map=colors,
        labels={'Reorder_Quantity': 'Reorder Quantity', 'Product_Name': 'Product'}
    )
    
    fig.update_traces(
        hovertemplate='<b>%{x}</b><br>Reorder Qty: %{y}<br>Status: %{color}<extra></extra>'
    )
    
    fig.update_layout(
        height=500,
        xaxis_title="Product",
        yaxis_title="Reorder Quantity",
        xaxis={'tickangle': 45}
    )
    
    return fig

def create_sales_velocity_scatter(data: pd.DataFrame):
    """
    Create a scatter plot of sales velocity vs current stock
    """
    fig = px.scatter(
        data,
        x='Current_Stock',
        y='Sales_Velocity',
        color='Category',
        size='Inventory_Value',
        hover_data=['Product_Name', 'Days_Stock_Remaining'],
        title="Sales Velocity vs Current Stock",
        labels={
            'Current_Stock': 'Current Stock Level',
            'Sales_Velocity': 'Sales Velocity (units/day)'
        }
    )
    
    fig.update_traces(
        hovertemplate='<b>%{hovertext}</b><br>'
                     'Stock: %{x}<br>'
                     'Velocity: %{y:.2f}<br>'
                     'Days Remaining: %{customdata[1]:.1f}<br>'
                     '<extra></extra>',
        hovertext=data['Product_Name']
    )
    
    fig.update_layout(
        height=500,
        showlegend=True
    )
    
    return fig

def create_inventory_value_chart(data: pd.DataFrame):
    """
    Create a chart showing inventory value by category
    """
    # Calculate inventory value by category
    category_values = data.groupby('Category')['Inventory_Value'].sum().sort_values(ascending=False)
    
    fig = px.bar(
        x=category_values.index,
        y=category_values.values,
        title="Total Inventory Value by Category",
        labels={'x': 'Category', 'y': 'Inventory Value ($)'},
        color=category_values.index,
        color_discrete_map={
            'Slow Moving': '#FF6B6B',
            'Fast Moving': '#4ECDC4',
            'Best Selling': '#45B7D1'
        }
    )
    
    fig.update_traces(
        hovertemplate='<b>%{x}</b><br>Value: BHD %{y:,.2f}<extra></extra>'
    )
    
    fig.update_layout(
        showlegend=False,
        height=400,
        yaxis_tickformat='BHD ,.0f'
    )
    
    return fig

def create_days_remaining_histogram(data: pd.DataFrame):
    """
    Create a histogram showing distribution of days stock remaining
    """
    # Filter out extremely high values for better visualization
    filtered_data = data[data['Days_Stock_Remaining'] <= 365]  # Max 1 year
    
    fig = px.histogram(
        filtered_data,
        x='Days_Stock_Remaining',
        nbins=30,
        title="Distribution of Days Stock Remaining",
        labels={'Days_Stock_Remaining': 'Days Stock Remaining', 'count': 'Number of Products'},
        color_discrete_sequence=['#45B7D1']
    )
    
    fig.add_vline(
        x=30, line_dash="dash", line_color="red",
        annotation_text="30 Days", annotation_position="top right"
    )
    
    fig.add_vline(
        x=14, line_dash="dash", line_color="orange",
        annotation_text="14 Days", annotation_position="top right"
    )
    
    fig.add_vline(
        x=7, line_dash="dash", line_color="darkred",
        annotation_text="7 Days", annotation_position="top right"
    )
    
    fig.update_layout(
        height=400,
        showlegend=False
    )
    
    return fig

def create_abc_analysis_chart(data: pd.DataFrame):
    """
    Create ABC analysis chart based on inventory value
    """
    # Calculate cumulative value percentage
    sorted_data = data.sort_values('Inventory_Value', ascending=False).copy()
    sorted_data['Cumulative_Value'] = sorted_data['Inventory_Value'].cumsum()
    total_value = sorted_data['Inventory_Value'].sum()
    sorted_data['Cumulative_Percentage'] = (sorted_data['Cumulative_Value'] / total_value) * 100
    
    # Classify into ABC categories
    def classify_abc(cum_pct):
        if cum_pct <= 80:
            return 'A'
        elif cum_pct <= 95:
            return 'B'
        else:
            return 'C'
    
    sorted_data['ABC_Category'] = sorted_data['Cumulative_Percentage'].apply(classify_abc)
    
    fig = px.line(
        sorted_data.reset_index(),
        x='index',
        y='Cumulative_Percentage',
        title="ABC Analysis - Cumulative Inventory Value",
        labels={'index': 'Product Rank', 'Cumulative_Percentage': 'Cumulative Value %'}
    )
    
    # Add horizontal lines for ABC boundaries
    fig.add_hline(y=80, line_dash="dash", line_color="red", annotation_text="80% (A-B boundary)")
    fig.add_hline(y=95, line_dash="dash", line_color="orange", annotation_text="95% (B-C boundary)")
    
    fig.update_layout(
        height=400,
        yaxis_range=[0, 100]
    )
    
    return fig
