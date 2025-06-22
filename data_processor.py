import pandas as pd
import streamlit as st
from typing import Optional, Union
import io

class DataProcessor:
    """
    Class for processing and validating uploaded inventory data
    """
    
    def __init__(self):
        self.required_columns = [
            'Item no', 'Description', 'Inventory', 
            'Sales (Qty.)', 'Average Cost'
        ]
        self.optional_columns = ['LDC', 'Sales (LCY)', 'Purch. (LCY)', 'Value']
        
    def load_data(self, uploaded_file) -> Optional[pd.DataFrame]:
        """
        Load data from uploaded file
        
        Args:
            uploaded_file: Streamlit uploaded file object
            
        Returns:
            DataFrame with processed data or None if error
        """
        try:
            # Determine file type and read accordingly
            if uploaded_file.name.endswith('.csv'):
                data = pd.read_csv(uploaded_file)
            elif uploaded_file.name.endswith(('.xlsx', '.xls')):
                data = pd.read_excel(uploaded_file)
            else:
                st.error("Unsupported file format. Please upload CSV or Excel files.")
                return None
            
            # Validate and clean data
            processed_data = self.validate_and_clean_data(data)
            
            return processed_data
            
        except Exception as e:
            st.error(f"Error loading file: {str(e)}")
            return None
    
    def validate_and_clean_data(self, data: pd.DataFrame) -> Optional[pd.DataFrame]:
        """
        Validate data structure and clean data
        
        Args:
            data: Raw DataFrame from file
            
        Returns:
            Cleaned DataFrame or None if validation fails
        """
        if data.empty:
            st.error("The uploaded file is empty.")
            return None
        
        # Check for required columns
        missing_columns = [col for col in self.required_columns if col not in data.columns]
        
        if missing_columns:
            # Try to find similar column names
            available_columns = list(data.columns)
            suggestions = self.suggest_column_mapping(missing_columns, available_columns)
            
            error_msg = f"Missing required columns: {missing_columns}"
            if suggestions:
                error_msg += f"\n\nSuggested column mappings:\n{suggestions}"
            
            st.error(error_msg)
            return None
        
        # Map columns to standard format for analysis
        mapped_data = self.map_columns_to_standard(data)
        
        if mapped_data is None:
            return None
        
        # Clean and validate data
        cleaned_data = self.clean_data(mapped_data)
        
        return cleaned_data
    
    def suggest_column_mapping(self, missing_columns: list, available_columns: list) -> str:
        """
        Suggest possible column mappings for missing columns
        """
        suggestions = []
        
        column_mappings = {
            'Product_ID': ['item no', 'product_id', 'sku', 'item_id', 'product_code'],
            'Product_Name': ['description', 'product_name', 'item_name', 'product'],
            'Current_Stock': ['inventory', 'stock', 'quantity', 'qty', 'on_hand', 'current_qty'],
            'Sales_Last_30_Days': ['sales (qty.)', 'sales', 'sold', 'units_sold', 'monthly_sales', 'last_30_days'],
            'Unit_Cost': ['average cost', 'cost', 'price', 'unit_price', 'unit_cost', 'cost_per_unit']
        }
        
        for missing_col in missing_columns:
            if missing_col in column_mappings:
                possible_matches = []
                for available_col in available_columns:
                    for suggestion in column_mappings[missing_col]:
                        if suggestion.lower() in available_col.lower():
                            possible_matches.append(available_col)
                            break
                
                if possible_matches:
                    suggestions.append(f"'{missing_col}' → {possible_matches}")
        
        return '\n'.join(suggestions) if suggestions else "No similar columns found"
    
    def map_columns_to_standard(self, data: pd.DataFrame) -> Optional[pd.DataFrame]:
        """
        Map your specific columns to standard format for analysis
        """
        mapped_data = data.copy()
        
        # Column mapping from your format to standard format
        column_mapping = {
            'Item no': 'Product_ID',
            'Description': 'Product_Name',
            'Inventory': 'Current_Stock',
            'Sales (Qty.)': 'Sales_Last_30_Days',
            'Average Cost': 'Unit_Cost',
            'LDC': 'Lead_Time_Days',
            'Sales (LCY)': 'Sales_LCY',
            'Purch. (LCY)': 'Purchase_LCY',
            'Value': 'Total_Value'
        }
        
        # Rename columns
        mapped_data = mapped_data.rename(columns=column_mapping)
        
        # Add any missing standard columns with default values
        if 'Lead_Time_Days' not in mapped_data.columns:
            mapped_data['Lead_Time_Days'] = 14  # Default 14 days
        
        return mapped_data
    
    def clean_data(self, data: pd.DataFrame) -> Optional[pd.DataFrame]:
        """
        Clean and standardize the data
        """
        cleaned_data = data.copy()
        
        # Remove duplicates based on Product_ID
        initial_count = len(cleaned_data)
        cleaned_data = cleaned_data.drop_duplicates(subset=['Product_ID'])
        
        if len(cleaned_data) < initial_count:
            st.warning(f"Removed {initial_count - len(cleaned_data)} duplicate products")
        
        # Clean numerical columns
        numerical_columns = ['Current_Stock', 'Sales_Last_30_Days', 'Unit_Cost']
        
        for col in numerical_columns:
            # Convert to numeric, handling errors
            cleaned_data[col] = pd.to_numeric(cleaned_data[col], errors='coerce')
            
            # Fill NaN values with 0 for stock and sales, but not for cost
            if col in ['Current_Stock', 'Sales_Last_30_Days']:
                cleaned_data[col] = cleaned_data[col].fillna(0)
            
            # Ensure non-negative values
            cleaned_data[col] = cleaned_data[col].clip(lower=0)
        
        # Clean Lead_Time_Days if present
        if 'Lead_Time_Days' in cleaned_data.columns:
            cleaned_data['Lead_Time_Days'] = pd.to_numeric(
                cleaned_data['Lead_Time_Days'], errors='coerce'
            )
            cleaned_data['Lead_Time_Days'] = cleaned_data['Lead_Time_Days'].clip(lower=1)
        
        # Clean text columns
        text_columns = ['Product_Name']
        for col in text_columns:
            if col in cleaned_data.columns:
                cleaned_data[col] = cleaned_data[col].astype(str).str.strip()
        
        # Remove rows with missing critical data
        critical_columns = ['Product_Name', 'Unit_Cost']
        for col in critical_columns:
            if col == 'Product_Name':
                mask = cleaned_data[col].isna() | (cleaned_data[col].astype(str).str.strip() == '')
            else:
                mask = cleaned_data[col].isna() | (cleaned_data[col] == 0)
            
            removed_count = mask.sum()
            if removed_count > 0:
                st.warning(f"Removed {removed_count} products with missing {col}")
                cleaned_data = cleaned_data[~mask]
        
        # Ensure Product_ID is string
        cleaned_data['Product_ID'] = cleaned_data['Product_ID'].astype(str)
        
        # Final validation
        if cleaned_data.empty:
            st.error("No valid data remaining after cleaning.")
            return None
        
        st.info(f"Data cleaned successfully. {len(cleaned_data)} products ready for analysis.")
        
        return cleaned_data
    
    def get_data_summary(self, data: pd.DataFrame) -> dict:
        """
        Get summary information about the loaded data
        """
        if data is None or data.empty:
            return {}
        
        summary = {
            'total_products': len(data),
            'columns': list(data.columns),
            'total_stock_value': (data['Current_Stock'] * data['Unit_Cost']).sum(),
            'total_sales_last_30_days': data['Sales_Last_30_Days'].sum(),
            'date_range': {
                'min_stock': data['Current_Stock'].min(),
                'max_stock': data['Current_Stock'].max(),
                'avg_stock': data['Current_Stock'].mean(),
            }
        }
        
        return summary
