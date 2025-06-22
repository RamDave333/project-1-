import pandas as pd
import numpy as np
from typing import Dict, Tuple

class InventoryAnalyzer:
    """
    Main class for analyzing inventory data and generating insights
    """
    
    def __init__(self, data: pd.DataFrame, slow_threshold: float = 1.0, fast_threshold: float = 5.0):
        """
        Initialize the analyzer with inventory data
        
        Args:
            data: DataFrame containing inventory data
            slow_threshold: Units per day threshold for slow-moving items
            fast_threshold: Units per day threshold for fast-moving items
        """
        self.data = data.copy()
        self.slow_threshold = slow_threshold
        self.fast_threshold = fast_threshold
        
    def calculate_sales_velocity(self) -> pd.DataFrame:
        """
        Calculate sales velocity (units per day) for each product
        """
        # Calculate daily sales velocity
        self.data['Sales_Velocity'] = self.data['Sales_Last_30_Days'] / 30
        
        # Handle zero or negative sales
        self.data['Sales_Velocity'] = self.data['Sales_Velocity'].clip(lower=0)
        
        return self.data
    
    def categorize_products(self) -> pd.DataFrame:
        """
        Categorize products based on sales velocity
        """
        self.calculate_sales_velocity()
        
        def categorize_product(velocity):
            if velocity >= self.fast_threshold:
                return 'Best Selling'
            elif velocity >= self.slow_threshold:
                return 'Fast Moving'
            else:
                return 'Slow Moving'
        
        self.data['Category'] = self.data['Sales_Velocity'].apply(categorize_product)
        
        return self.data
    
    def calculate_stock_metrics(self) -> pd.DataFrame:
        """
        Calculate various stock-related metrics
        """
        # Days of stock remaining
        self.data['Days_Stock_Remaining'] = np.where(
            self.data['Sales_Velocity'] > 0,
            self.data['Current_Stock'] / self.data['Sales_Velocity'],
            999  # Set high value for products with no sales
        )
        
        # Stock status
        def get_stock_status(days_remaining):
            if days_remaining <= 7:
                return 'Critical'
            elif days_remaining <= 14:
                return 'Low'
            elif days_remaining <= 30:
                return 'Normal'
            else:
                return 'High'
        
        self.data['Stock_Status'] = self.data['Days_Stock_Remaining'].apply(get_stock_status)
        
        return self.data
    
    def calculate_reorder_recommendations(self) -> pd.DataFrame:
        """
        Calculate reorder quantities and timing recommendations
        """
        # Set default lead time if not provided
        if 'Lead_Time_Days' not in self.data.columns:
            self.data['Lead_Time_Days'] = 14  # Default 2 weeks
        
        # Fill missing lead times
        self.data['Lead_Time_Days'] = self.data['Lead_Time_Days'].fillna(14)
        
        # Calculate reorder point (lead time demand + safety stock)
        safety_stock_days = 7  # 1 week safety stock
        self.data['Reorder_Point'] = self.data['Sales_Velocity'] * (
            self.data['Lead_Time_Days'] + safety_stock_days
        )
        
        # Calculate economic order quantity (simplified)
        # Using a simple formula: 30 days of demand
        self.data['Reorder_Quantity'] = np.where(
            self.data['Sales_Velocity'] > 0,
            np.ceil(self.data['Sales_Velocity'] * 30),  # 30 days supply
            0
        )
        
        # Adjust for current stock levels
        self.data['Reorder_Quantity'] = np.maximum(
            0,
            self.data['Reorder_Point'] - self.data['Current_Stock'] + self.data['Reorder_Quantity']
        )
        
        # Determine reorder status
        def get_reorder_status(current_stock, reorder_point, days_remaining):
            if current_stock <= reorder_point:
                return 'Reorder Now'
            elif days_remaining <= 14:
                return 'Reorder Soon'
            else:
                return 'No Action Needed'
        
        self.data['Reorder_Status'] = self.data.apply(
            lambda row: get_reorder_status(
                row['Current_Stock'], 
                row['Reorder_Point'], 
                row['Days_Stock_Remaining']
            ), 
            axis=1
        )
        
        return self.data
    
    def calculate_financial_metrics(self) -> pd.DataFrame:
        """
        Calculate financial metrics for inventory
        """
        # Current inventory value
        self.data['Inventory_Value'] = self.data['Current_Stock'] * self.data['Unit_Cost']
        
        # Reorder value
        self.data['Reorder_Value'] = self.data['Reorder_Quantity'] * self.data['Unit_Cost']
        
        # Monthly sales value (estimated)
        self.data['Monthly_Sales_Value'] = (
            self.data['Sales_Last_30_Days'] * self.data['Unit_Cost']
        )
        
        # Inventory turnover ratio (annual estimate)
        self.data['Turnover_Ratio'] = np.where(
            self.data['Inventory_Value'] > 0,
            (self.data['Monthly_Sales_Value'] * 12) / self.data['Inventory_Value'],
            0
        )
        
        return self.data
    
    def analyze_inventory(self) -> pd.DataFrame:
        """
        Perform complete inventory analysis
        """
        # Run all analysis steps
        self.categorize_products()
        self.calculate_stock_metrics()
        self.calculate_reorder_recommendations()
        self.calculate_financial_metrics()
        
        # Round numerical columns for better display
        numerical_columns = [
            'Sales_Velocity', 'Days_Stock_Remaining', 'Reorder_Point',
            'Reorder_Quantity', 'Inventory_Value', 'Reorder_Value',
            'Monthly_Sales_Value', 'Turnover_Ratio'
        ]
        
        for col in numerical_columns:
            if col in self.data.columns:
                self.data[col] = self.data[col].round(2)
        
        return self.data
    
    def get_summary_stats(self) -> Dict:
        """
        Get summary statistics for the inventory
        """
        if self.data.empty:
            return {}
        
        stats = {
            'total_products': len(self.data),
            'total_inventory_value': self.data['Inventory_Value'].sum(),
            'total_reorder_value': self.data['Reorder_Value'].sum(),
            'category_breakdown': self.data['Category'].value_counts().to_dict(),
            'reorder_status_breakdown': self.data['Reorder_Status'].value_counts().to_dict(),
            'average_turnover_ratio': self.data['Turnover_Ratio'].mean(),
            'products_needing_reorder': len(
                self.data[self.data['Reorder_Status'].isin(['Reorder Now', 'Reorder Soon'])]
            )
        }
        
        return stats
