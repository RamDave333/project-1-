# Inventory Management Dashboard

## Overview

This is a Streamlit-based inventory management dashboard application that allows users to upload inventory data and analyze sales velocity, stock levels, and receive reorder recommendations. The application is built with Python 3.11 and designed to run on Replit's autoscale deployment platform.

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit web application framework
- **Layout**: Wide layout with expandable sidebar for controls
- **Visualization**: Plotly for interactive charts and graphs
- **File Upload**: Support for CSV and Excel files (.csv, .xlsx, .xls)

### Backend Architecture
- **Language**: Python 3.11
- **Architecture Pattern**: Modular design with separation of concerns
- **Core Components**:
  - Data processing layer (`DataProcessor`)
  - Analysis engine (`InventoryAnalyzer`) 
  - Visualization module (`visualizations.py`)
  - Utility functions (`utils.py`)

### Data Processing Pipeline
1. File upload and validation
2. Data cleaning and normalization
3. Sales velocity calculations
4. Product categorization
5. Reorder point analysis
6. Visualization generation

## Key Components

### Core Modules

1. **app.py** - Main Streamlit application entry point
   - Handles UI layout and user interactions
   - Manages session state for data persistence
   - Coordinates between different modules

2. **data_processor.py** - Data ingestion and validation
   - Supports multiple file formats (CSV, Excel)
   - Validates required columns: Product_ID, Product_Name, Current_Stock, Sales_Last_30_Days, Unit_Cost
   - Optional columns: Lead_Time_Days
   - Data cleaning and normalization

3. **inventory_analyzer.py** - Core business logic
   - Sales velocity calculations (units per day)
   - Product categorization: Slow Moving, Fast Moving, Best Selling
   - Configurable thresholds for categorization
   - Reorder point recommendations

4. **visualizations.py** - Chart generation
   - Sales velocity distribution charts
   - Stock level visualization
   - Reorder recommendations charts
   - Uses Plotly for interactive visualizations

5. **utils.py** - Utility functions
   - File format validation
   - Data export capabilities (CSV)
   - Formatting functions for currency and percentages

### Data Schema

**Required Columns:**
- `Item no`: Unique product identifier
- `Description`: Product name/description
- `Inventory`: Current inventory levels
- `Sales (Qty.)`: Sales volume quantity
- `Average Cost`: Cost per unit

**Optional Columns:**
- `LDC`: Lead time in days

**Calculated Fields:**
- `Sales_Velocity`: Daily sales rate (Sales_Last_30_Days / 30)
- `Category`: Product classification based on velocity
- `Stock_Status`: Current stock level status

## Data Flow

1. **Upload**: User uploads inventory data file via Streamlit interface
2. **Validation**: File format and data structure validation
3. **Processing**: Data cleaning and standardization
4. **Analysis**: Sales velocity calculation and product categorization
5. **Visualization**: Interactive charts and dashboards
6. **Export**: Processed data can be exported as CSV

## External Dependencies

### Core Dependencies
- **streamlit**: Web application framework (v1.46.0+)
- **pandas**: Data manipulation and analysis (v2.3.0+)
- **numpy**: Numerical computing (v2.3.1+)
- **plotly**: Interactive visualizations (v6.1.2+)
- **openpyxl**: Excel file processing (v3.1.5+)

### System Dependencies
- Python 3.11
- Nix package manager (stable-24_05 channel)
- glibc locales for internationalization

## Deployment Strategy

### Platform
- **Target**: Replit autoscale deployment
- **Runtime**: Python 3.11 with Nix modules
- **Port**: 5000 (configured for Streamlit)

### Configuration
- **Entry Point**: `streamlit run app.py --server.port 5000`
- **Deployment Mode**: Autoscale for dynamic resource allocation
- **Server Config**: Headless mode with external access on 0.0.0.0:5000

### Workflow
- Parallel execution workflow with Streamlit app task
- Automatic port detection and waiting
- Shell execution for Streamlit server startup

## Changelog

```
Changelog:
- June 22, 2025. Initial setup
- June 22, 2025. Updated column mapping to support user's specific data format with columns: Item no, Description, Inventory, Sales (Qty.), Average Cost, LDC
- June 22, 2025. Added BHD currency formatting and financial dashboard metrics: Total Value, Total Sales, Sale Qty, Sale LCY, Purchase LCY
```

## User Preferences

```
Preferred communication style: Simple, everyday language.
```

## Architecture Decisions

### Technology Choices

1. **Streamlit over Flask/Django**
   - **Rationale**: Rapid prototyping for data applications
   - **Pros**: Built-in UI components, easy deployment, perfect for dashboards
   - **Cons**: Limited customization compared to full web frameworks

2. **Plotly for Visualizations**
   - **Rationale**: Interactive charts with minimal code
   - **Pros**: Professional-looking charts, interactivity, web-ready
   - **Cons**: Larger bundle size than matplotlib

3. **Pandas for Data Processing**
   - **Rationale**: Standard for data manipulation in Python
   - **Pros**: Excellent CSV/Excel support, powerful data operations
   - **Cons**: Memory usage for large datasets

4. **Modular Architecture**
   - **Rationale**: Separation of concerns for maintainability
   - **Pros**: Testable components, clear responsibilities
   - **Cons**: More files to manage

### Design Patterns

1. **Session State Management**: Uses Streamlit's session state to persist data across interactions
2. **Error Handling**: Graceful error handling with user-friendly messages
3. **Validation Pipeline**: Multi-stage validation for data integrity
4. **Configurable Thresholds**: Parameterized analysis for different business needs