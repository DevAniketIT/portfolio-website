#!/usr/bin/env python3
"""
Data Analysis & Visualization Toolkit
Comprehensive data analysis solutions for businesses.
Services priced between ₹2500-7000 per project.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

from datetime import datetime, timedelta
import os
from typing import List, Dict, Any, Optional, Tuple
import logging
import json

class DataAnalyzer:
    def __init__(self):
        """Initialize the Data Analyzer"""
        self.setup_logging()
        self.setup_plotting_style()
        
    def setup_logging(self):
        """Setup logging for analysis operations"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
    def setup_plotting_style(self):
        """Setup consistent plotting style"""
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
        
    def load_data(self, file_path: str) -> pd.DataFrame:
        """
        Load data from various file formats
        """
        try:
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            elif file_path.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(file_path)
            elif file_path.endswith('.json'):
                df = pd.read_json(file_path)
            elif file_path.endswith('.parquet'):
                df = pd.read_parquet(file_path)
            else:
                raise ValueError(f"Unsupported file format: {file_path}")
                
            self.logger.info(f"Data loaded successfully: {df.shape[0]} rows, {df.shape[1]} columns")
            return df
            
        except Exception as e:
            self.logger.error(f"Error loading data: {e}")
            raise
    
    def data_profiling(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Generate comprehensive data profiling report
        """
        profile = {
            'basic_info': {
                'rows': len(df),
                'columns': len(df.columns),
                'memory_usage': df.memory_usage(deep=True).sum(),
                'duplicate_rows': df.duplicated().sum()
            },
            'column_info': {},
            'data_types': df.dtypes.value_counts().to_dict(),
            'missing_values': df.isnull().sum().to_dict(),
            'summary_stats': df.describe(include='all').to_dict()
        }
        
        # Detailed column analysis
        for column in df.columns:
            col_data = df[column]
            col_profile = {
                'data_type': str(col_data.dtype),
                'null_count': col_data.isnull().sum(),
                'null_percentage': (col_data.isnull().sum() / len(df)) * 100,
                'unique_values': col_data.nunique(),
                'unique_percentage': (col_data.nunique() / len(df)) * 100
            }
            
            if col_data.dtype in ['int64', 'float64']:
                col_profile.update({
                    'min': col_data.min(),
                    'max': col_data.max(),
                    'mean': col_data.mean(),
                    'median': col_data.median(),
                    'std': col_data.std(),
                    'outliers_iqr': self._detect_outliers_iqr(col_data)
                })
            elif col_data.dtype == 'object':
                col_profile.update({
                    'most_common': col_data.value_counts().head().to_dict(),
                    'avg_length': col_data.astype(str).str.len().mean() if not col_data.empty else 0
                })
                
            profile['column_info'][column] = col_profile
        
        return profile
    
    def _detect_outliers_iqr(self, series: pd.Series) -> int:
        """Detect outliers using IQR method"""
        if series.dtype not in ['int64', 'float64'] or series.empty:
            return 0
            
        Q1 = series.quantile(0.25)
        Q3 = series.quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        outliers = ((series < lower_bound) | (series > upper_bound)).sum()
        return int(outliers)
    
    def clean_data(self, df: pd.DataFrame, config: Dict[str, Any] = None) -> pd.DataFrame:
        """
        Clean data based on configuration
        """
        df_clean = df.copy()
        
        if config is None:
            config = {
                'remove_duplicates': True,
                'handle_missing': 'auto',  # 'drop', 'fill_mean', 'fill_median', 'fill_mode', 'auto'
                'outlier_treatment': 'cap',  # 'remove', 'cap', 'none'
                'standardize_text': True
            }
        
        initial_shape = df_clean.shape
        
        # Remove duplicates
        if config.get('remove_duplicates', True):
            df_clean = df_clean.drop_duplicates()
            self.logger.info(f"Removed {initial_shape[0] - df_clean.shape[0]} duplicate rows")
        
        # Handle missing values
        missing_strategy = config.get('handle_missing', 'auto')
        for column in df_clean.columns:
            if df_clean[column].isnull().sum() > 0:
                if missing_strategy == 'auto':
                    if df_clean[column].dtype in ['int64', 'float64']:
                        df_clean[column] = df_clean[column].fillna(df_clean[column].median())
                    else:
                        df_clean[column] = df_clean[column].fillna(df_clean[column].mode()[0] if not df_clean[column].mode().empty else 'Unknown')
                elif missing_strategy == 'drop':
                    df_clean = df_clean.dropna(subset=[column])
                elif missing_strategy == 'fill_mean':
                    if df_clean[column].dtype in ['int64', 'float64']:
                        df_clean[column] = df_clean[column].fillna(df_clean[column].mean())
                elif missing_strategy == 'fill_median':
                    if df_clean[column].dtype in ['int64', 'float64']:
                        df_clean[column] = df_clean[column].fillna(df_clean[column].median())
                elif missing_strategy == 'fill_mode':
                    mode_value = df_clean[column].mode()[0] if not df_clean[column].mode().empty else 'Unknown'
                    df_clean[column] = df_clean[column].fillna(mode_value)
        
        # Handle outliers for numeric columns
        outlier_treatment = config.get('outlier_treatment', 'cap')
        if outlier_treatment != 'none':
            for column in df_clean.select_dtypes(include=[np.number]).columns:
                Q1 = df_clean[column].quantile(0.25)
                Q3 = df_clean[column].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                if outlier_treatment == 'remove':
                    df_clean = df_clean[(df_clean[column] >= lower_bound) & (df_clean[column] <= upper_bound)]
                elif outlier_treatment == 'cap':
                    df_clean[column] = df_clean[column].clip(lower=lower_bound, upper=upper_bound)
        
        # Standardize text columns
        if config.get('standardize_text', True):
            for column in df_clean.select_dtypes(include=['object']).columns:
                df_clean[column] = df_clean[column].astype(str).str.strip().str.title()
        
        self.logger.info(f"Data cleaned: {initial_shape} -> {df_clean.shape}")
        return df_clean
    
    def sales_analysis(self, df: pd.DataFrame, date_col: str, amount_col: str, 
                      category_col: str = None) -> Dict[str, Any]:
        """
        Comprehensive sales analysis
        """
        # Convert date column
        df[date_col] = pd.to_datetime(df[date_col])
        df = df.sort_values(date_col)
        
        # Basic metrics
        total_sales = df[amount_col].sum()
        avg_sale = df[amount_col].mean()
        total_transactions = len(df)
        
        # Time-based analysis
        df['year'] = df[date_col].dt.year
        df['month'] = df[date_col].dt.month
        df['day_of_week'] = df[date_col].dt.day_name()
        df['quarter'] = df[date_col].dt.quarter
        
        monthly_sales = df.groupby(df[date_col].dt.to_period('M'))[amount_col].agg(['sum', 'count', 'mean'])
        quarterly_sales = df.groupby('quarter')[amount_col].agg(['sum', 'count', 'mean'])
        daily_sales = df.groupby('day_of_week')[amount_col].agg(['sum', 'count', 'mean'])
        
        # Growth analysis
        monthly_growth = monthly_sales['sum'].pct_change() * 100
        
        analysis = {
            'summary': {
                'total_sales': total_sales,
                'avg_sale_amount': avg_sale,
                'total_transactions': total_transactions,
                'date_range': f"{df[date_col].min().date()} to {df[date_col].max().date()}"
            },
            'time_analysis': {
                'monthly_sales': monthly_sales.to_dict(),
                'quarterly_sales': quarterly_sales.to_dict(),
                'daily_sales': daily_sales.to_dict(),
                'monthly_growth': monthly_growth.dropna().to_dict()
            },
            'top_performers': {
                'best_month': monthly_sales['sum'].idxmax(),
                'best_quarter': quarterly_sales['sum'].idxmax(),
                'best_day': daily_sales['sum'].idxmax()
            }
        }
        
        # Category analysis if category column provided
        if category_col and category_col in df.columns:
            category_analysis = df.groupby(category_col)[amount_col].agg(['sum', 'count', 'mean'])
            analysis['category_analysis'] = category_analysis.to_dict()
            analysis['top_categories'] = category_analysis['sum'].nlargest(5).to_dict()
        
        return analysis
    
    def customer_analysis(self, df: pd.DataFrame, customer_col: str, 
                         amount_col: str, date_col: str = None) -> Dict[str, Any]:
        """
        Customer behavior analysis
        """
        # Customer metrics
        customer_metrics = df.groupby(customer_col).agg({
            amount_col: ['sum', 'count', 'mean'],
            customer_col: 'count'
        }).round(2)
        
        customer_metrics.columns = ['total_spent', 'transaction_count', 'avg_transaction', 'frequency']
        
        # Customer segments
        customer_metrics['segment'] = pd.cut(customer_metrics['total_spent'], 
                                           bins=3, labels=['Low Value', 'Medium Value', 'High Value'])
        
        # RFM Analysis if date column is provided
        rfm_analysis = None
        if date_col:
            df[date_col] = pd.to_datetime(df[date_col])
            current_date = df[date_col].max()
            
            rfm = df.groupby(customer_col).agg({
                date_col: lambda x: (current_date - x.max()).days,  # Recency
                customer_col: 'count',  # Frequency
                amount_col: 'sum'  # Monetary
            })
            
            rfm.columns = ['recency', 'frequency', 'monetary']
            
            # RFM scoring
            rfm['r_score'] = pd.cut(rfm['recency'], bins=5, labels=[5,4,3,2,1])
            rfm['f_score'] = pd.cut(rfm['frequency'].rank(method='first'), bins=5, labels=[1,2,3,4,5])
            rfm['m_score'] = pd.cut(rfm['monetary'], bins=5, labels=[1,2,3,4,5])
            
            rfm['rfm_score'] = (rfm['r_score'].astype(str) + 
                               rfm['f_score'].astype(str) + 
                               rfm['m_score'].astype(str))
            
            rfm_analysis = rfm.to_dict()
        
        analysis = {
            'customer_metrics': customer_metrics.to_dict(),
            'segment_distribution': customer_metrics['segment'].value_counts().to_dict(),
            'top_customers': customer_metrics.nlargest(10, 'total_spent')[['total_spent', 'transaction_count']].to_dict(),
            'customer_stats': {
                'total_customers': len(customer_metrics),
                'avg_customer_value': customer_metrics['total_spent'].mean(),
                'avg_transactions_per_customer': customer_metrics['transaction_count'].mean()
            }
        }
        
        if rfm_analysis:
            analysis['rfm_analysis'] = rfm_analysis
            
        return analysis
    
    def create_dashboard(self, df: pd.DataFrame, analysis_type: str = 'general', 
                        output_file: str = 'dashboard.html') -> str:
        """
        Create interactive dashboard using Plotly
        """
        if analysis_type == 'sales' and len(df.select_dtypes(include=[np.number]).columns) >= 2:
            return self._create_sales_dashboard(df, output_file)
        else:
            return self._create_general_dashboard(df, output_file)
    
    def _create_sales_dashboard(self, df: pd.DataFrame, output_file: str) -> str:
        """Create sales-specific dashboard"""
        # Create subplots
        fig = make_subplots(
            rows=3, cols=2,
            subplot_titles=['Sales Trend', 'Top Products/Categories', 
                           'Daily Sales Pattern', 'Monthly Comparison',
                           'Sales Distribution', 'Key Metrics'],
            specs=[[{"secondary_y": True}, {"type": "bar"}],
                   [{"type": "bar"}, {"type": "bar"}],
                   [{"type": "histogram"}, {"type": "table"}]]
        )
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        date_cols = df.select_dtypes(include=['datetime']).columns
        
        # Sales trend (if date column exists)
        if len(date_cols) > 0 and len(numeric_cols) > 0:
            date_col = date_cols[0]
            amount_col = numeric_cols[0]
            
            daily_sales = df.groupby(df[date_col].dt.date)[amount_col].sum().reset_index()
            fig.add_trace(
                go.Scatter(x=daily_sales[date_col], y=daily_sales[amount_col], 
                          mode='lines', name='Daily Sales'),
                row=1, col=1
            )
        
        # Top categories (if categorical columns exist)
        categorical_cols = df.select_dtypes(include=['object']).columns
        if len(categorical_cols) > 0 and len(numeric_cols) > 0:
            cat_col = categorical_cols[0]
            top_categories = df.groupby(cat_col)[numeric_cols[0]].sum().nlargest(10)
            
            fig.add_trace(
                go.Bar(x=top_categories.index, y=top_categories.values, 
                       name='Top Categories'),
                row=1, col=2
            )
        
        # Key metrics table
        metrics_data = [
            ['Total Records', len(df)],
            ['Numeric Columns', len(numeric_cols)],
            ['Date Columns', len(date_cols)],
            ['Categorical Columns', len(categorical_cols)]
        ]
        
        if len(numeric_cols) > 0:
            metrics_data.extend([
                ['Total Sum', df[numeric_cols[0]].sum()],
                ['Average', df[numeric_cols[0]].mean()],
                ['Max Value', df[numeric_cols[0]].max()]
            ])
        
        fig.add_trace(
            go.Table(
                header=dict(values=['Metric', 'Value']),
                cells=dict(values=[[item[0] for item in metrics_data],
                                  [item[1] for item in metrics_data]])
            ),
            row=3, col=2
        )
        
        fig.update_layout(height=800, showlegend=True, 
                         title_text="Sales Dashboard")
        
        # Save dashboard
        fig.write_html(output_file)
        self.logger.info(f"Sales dashboard created: {output_file}")
        return output_file
    
    def _create_general_dashboard(self, df: pd.DataFrame, output_file: str) -> str:
        """Create general data dashboard"""
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=['Data Overview', 'Numeric Distributions', 
                           'Missing Values', 'Data Types'],
            specs=[[{"type": "table"}, {"type": "histogram"}],
                   [{"type": "bar"}, {"type": "pie"}]]
        )
        
        # Data overview table
        overview_data = [
            ['Total Rows', len(df)],
            ['Total Columns', len(df.columns)],
            ['Memory Usage (MB)', round(df.memory_usage(deep=True).sum() / 1024**2, 2)],
            ['Duplicate Rows', df.duplicated().sum()]
        ]
        
        fig.add_trace(
            go.Table(
                header=dict(values=['Metric', 'Value']),
                cells=dict(values=[[item[0] for item in overview_data],
                                  [item[1] for item in overview_data]])
            ),
            row=1, col=1
        )
        
        # Numeric distributions
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            fig.add_trace(
                go.Histogram(x=df[numeric_cols[0]], name=numeric_cols[0]),
                row=1, col=2
            )
        
        # Missing values
        missing_data = df.isnull().sum()
        missing_data = missing_data[missing_data > 0]
        if len(missing_data) > 0:
            fig.add_trace(
                go.Bar(x=missing_data.index, y=missing_data.values, 
                       name='Missing Values'),
                row=2, col=1
            )
        
        # Data types
        dtype_counts = df.dtypes.value_counts()
        fig.add_trace(
            go.Pie(labels=dtype_counts.index.astype(str), 
                   values=dtype_counts.values, name='Data Types'),
            row=2, col=2
        )
        
        fig.update_layout(height=600, showlegend=True, 
                         title_text="Data Analysis Dashboard")
        
        # Save dashboard
        fig.write_html(output_file)
        self.logger.info(f"General dashboard created: {output_file}")
        return output_file
    
    def generate_report(self, df: pd.DataFrame, analysis_config: Dict[str, Any] = None) -> str:
        """
        Generate comprehensive analysis report
        """
        if analysis_config is None:
            analysis_config = {
                'include_profiling': True,
                'include_visualizations': True,
                'analysis_type': 'general',
                'output_format': 'html'
            }
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"analysis_report_{timestamp}.html"
        
        # Generate profile
        profile = self.data_profiling(df)
        
        # Create dashboard
        dashboard_file = f"dashboard_{timestamp}.html"
        self.create_dashboard(df, analysis_config.get('analysis_type', 'general'), dashboard_file)
        
        # Generate HTML report
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Data Analysis Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f0f0f0; padding: 20px; margin-bottom: 20px; }}
                .section {{ margin-bottom: 30px; }}
                .metric {{ display: inline-block; margin: 10px; padding: 15px; background-color: #e9f4f8; border-radius: 5px; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Data Analysis Report</h1>
                <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            
            <div class="section">
                <h2>Dataset Overview</h2>
                <div class="metric">
                    <h3>{profile['basic_info']['rows']:,}</h3>
                    <p>Total Rows</p>
                </div>
                <div class="metric">
                    <h3>{profile['basic_info']['columns']}</h3>
                    <p>Total Columns</p>
                </div>
                <div class="metric">
                    <h3>{profile['basic_info']['duplicate_rows']:,}</h3>
                    <p>Duplicate Rows</p>
                </div>
                <div class="metric">
                    <h3>{round(profile['basic_info']['memory_usage'] / 1024**2, 2)} MB</h3>
                    <p>Memory Usage</p>
                </div>
            </div>
            
            <div class="section">
                <h2>Data Quality Issues</h2>
                <table>
                    <tr><th>Column</th><th>Missing Values</th><th>Missing %</th><th>Data Type</th></tr>
        """
        
        # Add column details
        for col, info in profile['column_info'].items():
            html_content += f"""
                    <tr>
                        <td>{col}</td>
                        <td>{info['null_count']}</td>
                        <td>{info['null_percentage']:.2f}%</td>
                        <td>{info['data_type']}</td>
                    </tr>
            """
        
        html_content += f"""
                </table>
            </div>
            
            <div class="section">
                <h2>Interactive Dashboard</h2>
                <p><a href="{dashboard_file}" target="_blank">Open Interactive Dashboard</a></p>
                <p>The dashboard contains detailed visualizations and interactive charts for deeper analysis.</p>
            </div>
            
            <div class="section">
                <h2>Recommendations</h2>
                <ul>
        """
        
        # Generate recommendations
        recommendations = self._generate_recommendations(profile)
        for rec in recommendations:
            html_content += f"<li>{rec}</li>"
        
        html_content += """
                </ul>
            </div>
        </body>
        </html>
        """
        
        # Save report
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        self.logger.info(f"Analysis report generated: {report_file}")
        return report_file
    
    def _generate_recommendations(self, profile: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations based on data profile"""
        recommendations = []
        
        # Check for missing values
        missing_cols = [col for col, info in profile['column_info'].items() 
                       if info['null_percentage'] > 5]
        if missing_cols:
            recommendations.append(f"Address missing values in columns: {', '.join(missing_cols[:3])}...")
        
        # Check for duplicates
        if profile['basic_info']['duplicate_rows'] > 0:
            recommendations.append(f"Remove {profile['basic_info']['duplicate_rows']} duplicate rows to improve data quality")
        
        # Check for high cardinality
        high_cardinality_cols = [col for col, info in profile['column_info'].items() 
                               if info['unique_percentage'] > 95]
        if high_cardinality_cols:
            recommendations.append(f"Consider if high-cardinality columns like {high_cardinality_cols[0]} should be identifiers")
        
        # Check for potential categorical variables
        potential_categorical = [col for col, info in profile['column_info'].items() 
                               if info['data_type'] == 'object' and info['unique_values'] < 20]
        if potential_categorical:
            recommendations.append(f"Consider converting {', '.join(potential_categorical[:2])} to categorical data type for better performance")
        
        return recommendations

def main():
    analyzer = DataAnalyzer()
    
    print("Data Analysis & Visualization Toolkit")
    print("=====================================")
    print("\nServices Available:")
    print("1. Data Profiling & Quality Assessment")
    print("2. Sales Performance Analysis")
    print("3. Customer Behavior Analysis")
    print("4. Interactive Dashboard Creation")
    print("5. Comprehensive Report Generation")
    print("6. Data Cleaning & Preprocessing")
    
    print("\nExample Usage:")
    print("analyzer = DataAnalyzer()")
    print("df = analyzer.load_data('your_data.csv')")
    print("profile = analyzer.data_profiling(df)")
    print("report = analyzer.generate_report(df)")
    print("dashboard = analyzer.create_dashboard(df)")

if __name__ == "__main__":
    main()
