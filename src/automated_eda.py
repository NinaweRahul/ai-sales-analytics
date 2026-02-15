"""
Automated Exploratory Data Analysis Module
"""
import pandas as pd
import numpy as np
from sqlalchemy import text
from config import Config
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend (must be before pyplot import!)
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os

class AutomatedEDA:
    """Perform automated exploratory data analysis on query results"""
    
    def __init__(self):
        self.engine = Config.get_engine()
        
        # Create outputs directory if it doesn't exist
        self.output_dir = "../outputs"
        os.makedirs(self.output_dir, exist_ok=True)
    
    def execute_query(self, sql_query):
        """
        Execute SQL query and return results as DataFrame
        
        Args:
            sql_query: SQL query string
            
        Returns:
            pandas DataFrame with query results
        """
        try:
            with self.engine.connect() as conn:
                df = pd.read_sql(sql_query, conn)
            return df, None
        except Exception as e:
            return None, str(e)
    
    def analyze_results(self, df, query_context=""):
        """
        Perform comprehensive analysis on query results
        
        Args:
            df: pandas DataFrame with query results
            query_context: Description of what the query was asking
            
        Returns:
            dict: Analysis results
        """
        analysis = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'query_context': query_context,
            'row_count': len(df),
            'column_count': len(df.columns),
            'columns': list(df.columns),
            'data_types': df.dtypes.to_dict(),
            'summary_statistics': {},
            'missing_values': {},
            'unique_counts': {},
            'insights': []
        }
        
        # Summary statistics for numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if numeric_cols:
            summary = df[numeric_cols].describe()
            analysis['summary_statistics'] = summary.to_dict()
        
        # Missing values
        missing = df.isnull().sum()
        analysis['missing_values'] = missing[missing > 0].to_dict()
        
        # Unique value counts
        for col in df.columns:
            unique_count = df[col].nunique()
            analysis['unique_counts'][col] = unique_count
        
        # Generate insights
        analysis['insights'] = self._generate_insights(df, numeric_cols)
        
        return analysis
    
    def _generate_insights(self, df, numeric_cols):
        """Generate automated insights from the data"""
        insights = []
        
        # Insight 1: Row count
        insights.append(f"Dataset contains {len(df):,} records")
        
        # Insight 2: Numeric column insights
        for col in numeric_cols:
            col_data = df[col].dropna()
            if len(col_data) > 0:
                mean_val = col_data.mean()
                median_val = col_data.median()
                max_val = col_data.max()
                min_val = col_data.min()
                
                # Check for skewness
                if mean_val > median_val * 1.2:
                    insights.append(f"{col}: Right-skewed distribution (Mean: {mean_val:.2f}, Median: {median_val:.2f})")
                elif mean_val < median_val * 0.8:
                    insights.append(f"{col}: Left-skewed distribution (Mean: {mean_val:.2f}, Median: {median_val:.2f})")
                
                # Range insight
                insights.append(f"{col}: Range from {min_val:.2f} to {max_val:.2f}")
        
        # Insight 3: Categorical columns
        categorical_cols = df.select_dtypes(include=['object', 'string']).columns.tolist()
        for col in categorical_cols[:3]:  # Limit to first 3
            unique_count = df[col].nunique()
            if unique_count <= 10:
                top_value = df[col].mode()[0] if len(df[col].mode()) > 0 else "N/A"
                insights.append(f"{col}: {unique_count} unique values, most common: {top_value}")
        
        # Insight 4: Top records
        if len(numeric_cols) > 0:
            first_numeric = numeric_cols[0]
            if len(df) > 0:
                top_row = df.nlargest(1, first_numeric)
                insights.append(f"Highest {first_numeric}: {top_row[first_numeric].values[0]:.2f}")
        
        return insights
    
    def create_visualizations(self, df, analysis_name="analysis"):
        """
        Create automated visualizations for the data
        
        Args:
            df: pandas DataFrame
            analysis_name: Name for output files
        """
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        if not numeric_cols:
            print("No numeric columns to visualize")
            return []
        
        created_files = []
        
        # Set style
        sns.set_style("whitegrid")
        plt.rcParams['figure.figsize'] = (12, 6)
        
        # Visualization 1: Distribution plots for numeric columns
        if len(numeric_cols) > 0:
            fig, axes = plt.subplots(1, min(len(numeric_cols), 3), figsize=(15, 5))
            if not isinstance(axes, np.ndarray):
                axes = [axes]
            
            for idx, col in enumerate(numeric_cols[:3]):
                df[col].hist(bins=30, ax=axes[idx], edgecolor='black')
                axes[idx].set_title(f'Distribution of {col}')
                axes[idx].set_xlabel(col)
                axes[idx].set_ylabel('Frequency')
            
            plt.tight_layout()
            filepath = os.path.join(self.output_dir, f"{analysis_name}_distributions.png")
            plt.savefig(filepath, dpi=300, bbox_inches='tight')
            plt.close()
            created_files.append(filepath)
            print(f"Created: {filepath}")
        
        # Visualization 2: Bar chart if there are categorical columns with aggregated data
        categorical_cols = df.select_dtypes(include=['object', 'string']).columns.tolist()
        if categorical_cols and numeric_cols:
            cat_col = categorical_cols[0]
            num_col = numeric_cols[0]
            
            if df[cat_col].nunique() <= 15:  # Only if not too many categories
                plt.figure(figsize=(12, 6))
                top_categories = df.groupby(cat_col)[num_col].sum().nlargest(10)
                top_categories.plot(kind='bar', color='steelblue', edgecolor='black')
                plt.title(f'Top 10 {cat_col} by {num_col}')
                plt.xlabel(cat_col)
                plt.ylabel(num_col)
                plt.xticks(rotation=45, ha='right')
                plt.tight_layout()
                
                filepath = os.path.join(self.output_dir, f"{analysis_name}_top_categories.png")
                plt.savefig(filepath, dpi=300, bbox_inches='tight')
                plt.close()
                created_files.append(filepath)
                print(f"Created: {filepath}")
        
        return created_files
    
    def export_for_tableau(self, df, filename="tableau_export"):
        """
        Export data in Tableau-friendly format
        
        Args:
            df: pandas DataFrame
            filename: Output filename (without extension)
        """
        try:
            # Export as CSV
            csv_path = os.path.join(self.output_dir, f"{filename}.csv")
            df.to_csv(csv_path, index=False)
            print(f"Tableau CSV export: {csv_path}")
            
            # Export as Excel
            excel_path = os.path.join(self.output_dir, f"{filename}.xlsx")
            df.to_excel(excel_path, index=False, engine='openpyxl')
            print(f"Tableau Excel export: {excel_path}")
            
            return [csv_path, excel_path]
        
        except Exception as e:
            print(f"Error exporting for Tableau: {e}")
            return []
    
    def generate_eda_report(self, df, query_context, analysis_name="analysis"):
        """
        Generate complete EDA report
        
        Args:
            df: pandas DataFrame
            query_context: Description of the analysis
            analysis_name: Name for output files
            
        Returns:
            dict: Complete analysis results with file paths
        """
        print(f"\nPerforming Automated EDA...")
        
        # Perform analysis
        analysis = self.analyze_results(df, query_context)
        
        # Create visualizations
        viz_files = self.create_visualizations(df, analysis_name)
        analysis['visualization_files'] = viz_files
        
        # Export for Tableau
        tableau_files = self.export_for_tableau(df, analysis_name)
        analysis['tableau_files'] = tableau_files
        
        # Save analysis report
        report_path = os.path.join(self.output_dir, f"{analysis_name}_report.txt")
        with open(report_path, 'w') as f:
            f.write(f"=== Automated EDA Report ===\n\n")
            f.write(f"Generated: {analysis['timestamp']}\n")
            f.write(f"Query Context: {analysis['query_context']}\n\n")
            f.write(f"Dataset Overview:\n")
            f.write(f"  - Rows: {analysis['row_count']:,}\n")
            f.write(f"  - Columns: {analysis['column_count']}\n\n")
            f.write(f"Columns: {', '.join(analysis['columns'])}\n\n")
            f.write(f"Key Insights:\n")
            for insight in analysis['insights']:
                f.write(f"  • {insight}\n")
        
        analysis['report_file'] = report_path
        print(f"EDA Report: {report_path}")
        
        return analysis

def test_eda():
    """Test the EDA module"""
    eda = AutomatedEDA()
    
    # Test query
    query = "SELECT * FROM sales_data LIMIT 100"
    print(f"Testing EDA with query: {query}")
    
    df, error = eda.execute_query(query)
    
    if error:
        print(f"Query error: {error}")
        return
    
    print(f"Query executed successfully: {len(df)} rows")
    
    # Generate EDA report
    results = eda.generate_eda_report(df, "Test analysis of sales data", "test_analysis")
    
    print("\nAnalysis Complete!")
    print(f"Files created: {len(results.get('visualization_files', [])) + len(results.get('tableau_files', [])) + 1}")

if __name__ == "__main__":
    test_eda()
