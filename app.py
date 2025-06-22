import streamlit as st
import pandas as pd
from inventory_analyzer import InventoryAnalyzer
from visualizations import create_velocity_chart, create_stock_level_chart, create_reorder_chart
from data_processor import DataProcessor
from utils import export_to_csv, validate_file_format
import io

# Configure page
st.set_page_config(
    page_title="Inventory Management Dashboard",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'data' not in st.session_state:
    st.session_state.data = None
if 'analyzer' not in st.session_state:
    st.session_state.analyzer = None
if 'processed_data' not in st.session_state:
    st.session_state.processed_data = None

def main():
    st.title("📦 Inventory Management Dashboard")
    st.markdown("Upload your inventory data to analyze sales velocity and get reorder recommendations")
    
    # Sidebar for file upload and controls
    with st.sidebar:
        st.header("Data Upload")
        uploaded_file = st.file_uploader(
            "Choose a CSV or Excel file",
            type=['csv', 'xlsx', 'xls'],
            help="Upload your inventory data with columns: Item no, Description, Inventory, Sales (Qty.), Average Cost, LDC"
        )
        
        if uploaded_file is not None:
            if validate_file_format(uploaded_file):
                try:
                    # Process uploaded file
                    processor = DataProcessor()
                    data = processor.load_data(uploaded_file)
                    
                    if data is not None and not data.empty:
                        st.session_state.data = data
                        st.session_state.analyzer = InventoryAnalyzer(data)
                        st.session_state.processed_data = st.session_state.analyzer.analyze_inventory()
                        st.success(f"✅ Data loaded successfully! {len(data)} products found.")
                    else:
                        st.error("❌ No data found in the uploaded file.")
                        
                except Exception as e:
                    st.error(f"❌ Error processing file: {str(e)}")
            else:
                st.error("❌ Invalid file format. Please upload a CSV or Excel file.")
        
        # Configuration options
        if st.session_state.data is not None:
            st.header("Analysis Settings")
            
            # Velocity thresholds
            st.subheader("Sales Velocity Thresholds")
            slow_threshold = st.slider(
                "Slow Moving Threshold (units/day)",
                min_value=0.1,
                max_value=10.0,
                value=1.0,
                step=0.1,
                help="Products selling below this rate are considered slow-moving"
            )
            
            fast_threshold = st.slider(
                "Fast Moving Threshold (units/day)",
                min_value=1.0,
                max_value=50.0,
                value=5.0,
                step=0.5,
                help="Products selling above this rate are considered fast-moving"
            )
            
            # Update thresholds if changed
            if (st.session_state.analyzer.slow_threshold != slow_threshold or 
                st.session_state.analyzer.fast_threshold != fast_threshold):
                st.session_state.analyzer.slow_threshold = slow_threshold
                st.session_state.analyzer.fast_threshold = fast_threshold
                st.session_state.processed_data = st.session_state.analyzer.analyze_inventory()
                st.rerun()
    
    # Main content area
    if st.session_state.processed_data is not None:
        data = st.session_state.processed_data
        
        # Key financial metrics - Top row
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            total_value = data['Inventory_Value'].sum()
            st.metric("Total Value", f"BHD {total_value:,.2f}")
        
        with col2:
            total_sales = data['Monthly_Sales_Value'].sum()
            st.metric("Total Sales", f"BHD {total_sales:,.2f}")
        
        with col3:
            sale_qty = data['Sales_Last_30_Days'].sum()
            st.metric("Sale Qty", f"{sale_qty:,.0f}")
        
        with col4:
            # Use actual Sales LCY if available, otherwise fallback to Monthly Sales Value
            if 'Sales_LCY' in data.columns:
                sale_lcy = data['Sales_LCY'].sum()
            else:
                sale_lcy = data['Monthly_Sales_Value'].sum()
            st.metric("Sale LCY", f"BHD {sale_lcy:,.2f}")
        
        with col5:
            # Use actual Purchase LCY if available, otherwise calculate from reorder quantities
            if 'Purchase_LCY' in data.columns:
                purchase_lcy = data['Purchase_LCY'].sum()
            else:
                purchase_lcy = (data['Reorder_Quantity'] * data['Unit_Cost']).sum()
            st.metric("Purchase LCY", f"BHD {purchase_lcy:,.2f}")
        
        # Product category metrics - Second row
        st.markdown("---")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_products = len(data)
            st.metric("Total Products", total_products)
        
        with col2:
            slow_moving = len(data[data['Category'] == 'Slow Moving'])
            st.metric("Slow Moving", slow_moving, delta=f"{slow_moving/total_products*100:.1f}%")
        
        with col3:
            fast_moving = len(data[data['Category'] == 'Fast Moving'])
            st.metric("Fast Moving", fast_moving, delta=f"{fast_moving/total_products*100:.1f}%")
        
        with col4:
            best_selling = len(data[data['Category'] == 'Best Selling'])
            st.metric("Best Selling", best_selling, delta=f"{best_selling/total_products*100:.1f}%")
        
        # Tabs for different views
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "🔍 Product Analysis", "📋 Reorder Recommendations", "📤 Export"])
        
        with tab1:
            st.header("Inventory Overview")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Velocity distribution chart
                velocity_fig = create_velocity_chart(data)
                st.plotly_chart(velocity_fig, use_container_width=True)
            
            with col2:
                # Stock level distribution
                stock_fig = create_stock_level_chart(data)
                st.plotly_chart(stock_fig, use_container_width=True)
            
            # Category breakdown table
            st.subheader("Category Summary")
            category_summary = data.groupby('Category').agg({
                'Current_Stock': ['sum', 'mean'],
                'Sales_Velocity': 'mean',
                'Days_Stock_Remaining': 'mean',
                'Reorder_Quantity': 'sum'
            }).round(2)
            
            category_summary.columns = ['Total Stock', 'Avg Stock', 'Avg Velocity', 'Avg Days Remaining', 'Total Reorder Qty']
            st.dataframe(category_summary, use_container_width=True)
        
        with tab2:
            st.header("Product Analysis")
            
            # Filters
            col1, col2, col3 = st.columns(3)
            
            with col1:
                category_filter = st.selectbox(
                    "Filter by Category",
                    options=['All'] + list(data['Category'].unique())
                )
            
            with col2:
                search_term = st.text_input("Search Products", placeholder="Enter product name...")
            
            with col3:
                sort_by = st.selectbox(
                    "Sort by",
                    options=['Product_Name', 'Sales_Velocity', 'Current_Stock', 'Days_Stock_Remaining', 'Reorder_Quantity']
                )
            
            # Apply filters
            filtered_data = data.copy()
            
            if category_filter != 'All':
                filtered_data = filtered_data[filtered_data['Category'] == category_filter]
            
            if search_term:
                filtered_data = filtered_data[
                    filtered_data['Product_Name'].str.contains(search_term, case=False, na=False)
                ]
            
            # Sort data
            filtered_data = filtered_data.sort_values(sort_by, ascending=False)
            
            # Display filtered results
            st.subheader(f"Products ({len(filtered_data)} found)")
            
            # Display table with key columns
            display_columns = [
                'Product_Name', 'Category', 'Current_Stock', 'Sales_Velocity', 
                'Days_Stock_Remaining', 'Reorder_Quantity', 'Reorder_Status'
            ]
            
            st.dataframe(
                filtered_data[display_columns],
                use_container_width=True,
                column_config={
                    'Sales_Velocity': st.column_config.NumberColumn(
                        'Sales Velocity',
                        help='Units sold per day',
                        format='%.2f'
                    ),
                    'Days_Stock_Remaining': st.column_config.NumberColumn(
                        'Days Stock Remaining',
                        help='Days until stock runs out',
                        format='%.1f'
                    ),
                    'Reorder_Quantity': st.column_config.NumberColumn(
                        'Reorder Quantity',
                        help='Recommended reorder quantity',
                        format='%.0f'
                    )
                }
            )
        
        with tab3:
            st.header("Reorder Recommendations")
            
            # Filter for products that need reordering
            reorder_needed = data[data['Reorder_Status'] == 'Reorder Now']
            reorder_soon = data[data['Reorder_Status'] == 'Reorder Soon']
            
            if not reorder_needed.empty:
                st.subheader("🚨 Immediate Reorder Required")
                st.dataframe(
                    reorder_needed[['Product_Name', 'Current_Stock', 'Sales_Velocity', 
                                   'Days_Stock_Remaining', 'Reorder_Quantity']],
                    use_container_width=True
                )
            
            if not reorder_soon.empty:
                st.subheader("⚠️ Reorder Soon")
                st.dataframe(
                    reorder_soon[['Product_Name', 'Current_Stock', 'Sales_Velocity', 
                                 'Days_Stock_Remaining', 'Reorder_Quantity']],
                    use_container_width=True
                )
            
            # Reorder summary chart
            if not reorder_needed.empty or not reorder_soon.empty:
                reorder_fig = create_reorder_chart(data)
                st.plotly_chart(reorder_fig, use_container_width=True)
            
            # Total reorder value
            total_reorder_value = (data['Reorder_Quantity'] * data['Unit_Cost']).sum()
            st.metric("Total Reorder Value", f"BHD {total_reorder_value:,.2f}")
        
        with tab4:
            st.header("Export Data")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Full Analysis")
                csv_data = export_to_csv(data)
                st.download_button(
                    label="📥 Download Full Analysis (CSV)",
                    data=csv_data,
                    file_name="inventory_analysis.csv",
                    mime="text/csv"
                )
            
            with col2:
                st.subheader("Reorder List")
                reorder_data = data[data['Reorder_Status'].isin(['Reorder Now', 'Reorder Soon'])]
                if not reorder_data.empty:
                    reorder_csv = export_to_csv(reorder_data)
                    st.download_button(
                        label="📥 Download Reorder List (CSV)",
                        data=reorder_csv,
                        file_name="reorder_recommendations.csv",
                        mime="text/csv"
                    )
                else:
                    st.info("No products require reordering at this time.")
            
            # Data sample preview
            st.subheader("Data Preview")
            st.dataframe(data.head(10), use_container_width=True)
    
    else:
        # Welcome screen
        st.markdown("""
        ## Welcome to the Inventory Management Dashboard
        
        To get started, please upload your inventory data file using the sidebar. Your file should contain the following columns:
        
        - **Item no**: Unique identifier for each product
        - **Description**: Name of the product
        - **Inventory**: Current inventory level
        - **Sales (Qty.)**: Units sold quantity
        - **Average Cost**: Cost per unit
        - **LDC**: Lead time in days (optional)
        
        ### Features:
        - 📊 **Automatic Categorization**: Products are classified as slow-moving, fast-moving, or best-selling
        - 📈 **Visual Analytics**: Interactive charts and dashboards
        - 🔄 **Reorder Recommendations**: Smart suggestions based on sales velocity
        - 🔍 **Search & Filter**: Find specific products quickly
        - 📤 **Export Options**: Download analysis results
        
        Upload your data to begin the analysis!
        """)

if __name__ == "__main__":
    main()
