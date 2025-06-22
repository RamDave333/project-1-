import pandas as pd
import streamlit as st
import io
from typing import Union

def validate_file_format(uploaded_file) -> bool:
    """
    Validate if the uploaded file is in the correct format
    
    Args:
        uploaded_file: Streamlit uploaded file object
        
    Returns:
        bool: True if file format is valid, False otherwise
    """
    if uploaded_file is None:
        return False
    
    allowed_extensions = ['.csv', '.xlsx', '.xls']
    file_extension = '.' + uploaded_file.name.split('.')[-1].lower()
    
    return file_extension in allowed_extensions

def export_to_csv(data: pd.DataFrame) -> str:
    """
    Convert DataFrame to CSV string for download
    
    Args:
        data: DataFrame to export
        
    Returns:
        str: CSV string
    """
    return data.to_csv(index=False)

def format_currency(value: float) -> str:
    """
    Format numerical value as currency in BHD
    
    Args:
        value: Numerical value
        
    Returns:
        str: Formatted currency string in BHD
    """
    return f"BHD {value:,.2f}"

def format_percentage(value: float) -> str:
    """
    Format numerical value as percentage
    
    Args:
        value: Numerical value (0-1)
        
    Returns:
        str: Formatted percentage string
    """
    return f"{value:.1%}"

def calculate_safety_stock(sales_velocity: float, lead_time: int, service_level: float = 0.95) -> float:
    """
    Calculate safety stock based on sales velocity and lead time
    
    Args:
        sales_velocity: Average daily sales
        lead_time: Lead time in days
        service_level: Desired service level (default 95%)
        
    Returns:
        float: Recommended safety stock quantity
    """
    # Simplified safety stock calculation
    # In reality, this would consider demand variability and lead time variability
    z_score = 1.65  # For 95% service level
    demand_std = sales_velocity * 0.3  # Assume 30% coefficient of variation
    
    safety_stock = z_score * demand_std * (lead_time ** 0.5)
    
    return max(0, safety_stock)

def generate_reorder_summary(data: pd.DataFrame) -> dict:
    """
    Generate summary statistics for reorder recommendations
    
    Args:
        data: DataFrame with analysis results
        
    Returns:
        dict: Summary statistics
    """
    reorder_now = data[data['Reorder_Status'] == 'Reorder Now']
    reorder_soon = data[data['Reorder_Status'] == 'Reorder Soon']
    
    summary = {
        'total_products': len(data),
        'reorder_now_count': len(reorder_now),
        'reorder_soon_count': len(reorder_soon),
        'reorder_now_value': (reorder_now['Reorder_Quantity'] * reorder_now['Unit_Cost']).sum(),
        'reorder_soon_value': (reorder_soon['Reorder_Quantity'] * reorder_soon['Unit_Cost']).sum(),
        'total_reorder_value': (
            (reorder_now['Reorder_Quantity'] * reorder_now['Unit_Cost']).sum() +
            (reorder_soon['Reorder_Quantity'] * reorder_soon['Unit_Cost']).sum()
        ),
        'critical_stock_count': len(data[data['Stock_Status'] == 'Critical']),
        'low_stock_count': len(data[data['Stock_Status'] == 'Low'])
    }
    
    return summary

def create_sample_data_template() -> pd.DataFrame:
    """
    Create a sample data template for users to understand the required format
    
    Returns:
        pd.DataFrame: Sample data template
    """
    sample_data = {
        'Product_ID': ['SKU001', 'SKU002', 'SKU003', 'SKU004', 'SKU005'],
        'Product_Name': [
            'Widget A', 'Gadget B', 'Tool C', 'Device D', 'Component E'
        ],
        'Current_Stock': [150, 75, 200, 25, 300],
        'Sales_Last_30_Days': [120, 45, 180, 60, 90],
        'Unit_Cost': [12.50, 25.00, 8.75, 45.00, 15.25],
        'Lead_Time_Days': [14, 21, 10, 30, 7]
    }
    
    return pd.DataFrame(sample_data)

def validate_data_quality(data: pd.DataFrame) -> dict:
    """
    Validate data quality and return quality metrics
    
    Args:
        data: DataFrame to validate
        
    Returns:
        dict: Quality metrics and issues
    """
    issues = []
    warnings = []
    
    # Check for missing values
    missing_data = data.isnull().sum()
    if missing_data.any():
        for col, count in missing_data.items():
            if count > 0:
                issues.append(f"{col}: {count} missing values")
    
    # Check for negative values in stock/sales
    numeric_columns = ['Current_Stock', 'Sales_Last_30_Days', 'Unit_Cost']
    for col in numeric_columns:
        if col in data.columns:
            negative_count = (data[col] < 0).sum()
            if negative_count > 0:
                issues.append(f"{col}: {negative_count} negative values")
    
    # Check for zero unit costs
    if 'Unit_Cost' in data.columns:
        zero_cost_count = (data['Unit_Cost'] == 0).sum()
        if zero_cost_count > 0:
            warnings.append(f"Unit_Cost: {zero_cost_count} products with zero cost")
    
    # Check for products with no sales but high stock
    if all(col in data.columns for col in ['Sales_Last_30_Days', 'Current_Stock']):
        no_sales_high_stock = data[
            (data['Sales_Last_30_Days'] == 0) & (data['Current_Stock'] > 100)
        ]
        if len(no_sales_high_stock) > 0:
            warnings.append(
                f"{len(no_sales_high_stock)} products with no sales but high stock levels"
            )
    
    quality_score = max(0, 100 - len(issues) * 10 - len(warnings) * 5)
    
    return {
        'quality_score': quality_score,
        'issues': issues,
        'warnings': warnings,
        'total_records': len(data),
        'complete_records': len(data.dropna()),
        'completeness_percentage': (len(data.dropna()) / len(data)) * 100 if len(data) > 0 else 0
    }

def get_color_scheme() -> dict:
    """
    Get consistent color scheme for the application
    
    Returns:
        dict: Color mappings for different categories
    """
    return {
        'categories': {
            'Slow Moving': '#FF6B6B',
            'Fast Moving': '#4ECDC4',
            'Best Selling': '#45B7D1'
        },
        'stock_status': {
            'Critical': '#FF4444',
            'Low': '#FF8C00',
            'Normal': '#32CD32',
            'High': '#4169E1'
        },
        'reorder_status': {
            'Reorder Now': '#FF4444',
            'Reorder Soon': '#FF8C00',
            'No Action Needed': '#32CD32'
        }
    }
