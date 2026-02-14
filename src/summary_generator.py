"""
Executive Summary Generator - Create business insights from data analysis using Gemini
Updated for new google-genai SDK with rate limiting
"""
from google import genai
from config import Config
import pandas as pd
import json
import time

class SummaryGenerator:
    """Generate executive summaries using Gemini AI"""
    
    def __init__(self):
        # Initialize the new Gemini client
        self.client = genai.Client(api_key=Config.GEMINI_API_KEY)
        
        # Use gemini-2.0-flash (newest) or gemini-1.5-flash if quota issues
        self.model_id = 'gemini-2.0-flash-exp'
        
        # Rate limiting: minimum seconds between requests
        self.min_delay = 5  # 5 seconds between requests
        self.last_request_time = 0
    
    def _wait_for_rate_limit(self):
        """Enforce rate limiting between API calls"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_delay:
            wait_time = self.min_delay - time_since_last
            print(f"⏳ Rate limiting: waiting {wait_time:.1f}s...")
            time.sleep(wait_time)
        
        self.last_request_time = time.time()
    
    def generate_executive_summary(self, query_context, df, analysis_results):
        """
        Generate executive summary from query results and analysis
        
        Args:
            query_context: The original question/context
            df: pandas DataFrame with query results
            analysis_results: Dictionary with EDA results
            
        Returns:
            str: Executive summary text
        """
        # Prepare data summary
        data_preview = df.head(10).to_string() if len(df) > 0 else "No data"
        
        # Extract key statistics
        stats_summary = self._format_statistics(analysis_results)
        insights_summary = "\n".join(analysis_results.get('insights', []))
        
        prompt = f"""You are a business analyst creating an executive summary for leadership.

Context: {query_context}

Data Overview:
- Total Records: {analysis_results.get('row_count', 0):,}
- Columns: {', '.join(analysis_results.get('columns', []))}

Key Statistics:
{stats_summary}

Automated Insights:
{insights_summary}

Sample Data:
{data_preview}

Create a professional executive summary with:
1. **Overview** - What was analyzed and why it matters
2. **Key Findings** - Top 3-5 most important discoveries (use bullet points)
3. **Business Implications** - What this means for the business
4. **Recommendations** - 2-3 actionable next steps

Use clear, non-technical language. Focus on business value and actionable insights.
Format with markdown headers and bullet points for readability.
"""
        
        try:
            # Enforce rate limiting
            self._wait_for_rate_limit()
            
            # Make API call with new SDK
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=prompt
            )
            
            summary = response.text
            return summary
            
        except Exception as e:
            error_msg = str(e)
            
            if '429' in error_msg or 'RESOURCE_EXHAUSTED' in error_msg:
                return f"""Error generating summary: Rate limit exceeded.

Please wait a few minutes and try again.

💡 To avoid this in production:
- Enable billing at https://ai.google.dev/pricing for higher quota
- Add longer delays between requests
- Use batch processing for multiple analyses
"""
            
            return f"Error generating summary: {str(e)}"
    
    def _format_statistics(self, analysis_results):
        """Format statistics in a readable way"""
        output = []
        
        stats = analysis_results.get('summary_statistics', {})
        for col, col_stats in stats.items():
            if isinstance(col_stats, dict):
                mean = col_stats.get('mean', 0)
                median = col_stats.get('50%', 0)
                max_val = col_stats.get('max', 0)
                min_val = col_stats.get('min', 0)
                
                output.append(f"{col}:")
                output.append(f"  Mean: {mean:.2f}")
                output.append(f"  Median: {median:.2f}")
                output.append(f"  Range: {min_val:.2f} - {max_val:.2f}")
        
        return "\n".join(output) if output else "No statistics available"
    
    def generate_detailed_report(self, query_context, sql_query, df, analysis_results, summary):
        """
        Generate a comprehensive report document
        
        Args:
            query_context: Original question
            sql_query: The SQL query used
            df: Query results DataFrame
            analysis_results: EDA results
            summary: Executive summary text
            
        Returns:
            str: Complete markdown report
        """
        report = f"""# Sales Analytics Report

**Generated:** {analysis_results.get('timestamp', 'N/A')}

---

## 1. Analysis Request

**Question:** {query_context}

---

## 2. Executive Summary

{summary}

---

## 3. Data Query

**SQL Query Used:**
```sql
{sql_query}
```

**Results:** {len(df):,} records returned

---

## 4. Detailed Findings

### Dataset Overview
- **Total Records:** {analysis_results.get('row_count', 0):,}
- **Columns Analyzed:** {analysis_results.get('column_count', 0)}
- **Data Columns:** {', '.join(analysis_results.get('columns', []))}

### Statistical Summary

{self._format_statistics(analysis_results)}

### Key Insights

"""
        
        for idx, insight in enumerate(analysis_results.get('insights', []), 1):
            report += f"{idx}. {insight}\n"
        
        report += """

---

## 5. Sample Data

Top 10 Records:

"""
        
        report += df.head(10).to_markdown(index=False) if len(df) > 0 else "No data available"
        
        report += """

---

## 6. Visualizations

"""
        
        viz_files = analysis_results.get('visualization_files', [])
        if viz_files:
            for viz_file in viz_files:
                filename = viz_file.split('/')[-1]
                report += f"- {filename}\n"
        else:
            report += "No visualizations generated\n"
        
        report += """

---

## 7. Tableau Integration

Export files created for Tableau visualization:

"""
        
        tableau_files = analysis_results.get('tableau_files', [])
        if tableau_files:
            for tableau_file in tableau_files:
                filename = tableau_file.split('/')[-1]
                report += f"- {filename}\n"
        else:
            report += "No Tableau exports generated\n"
        
        report += """

---

*Report generated by AI-Powered Sales Analytics System (Gemini Edition)*
"""
        
        return report
    
    def save_report(self, report, filename, output_dir="../outputs"):
        """Save report to file"""
        import os
        
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"📄 Report saved: {filepath}")
        return filepath

def test_summary_generator():
    """Test the summary generator"""
    generator = SummaryGenerator()
    
    # Mock data for testing
    mock_df = pd.DataFrame({
        'product': ['Product A', 'Product B', 'Product C'],
        'revenue': [10000, 8500, 7200],
        'profit': [3000, 2550, 2160]
    })
    
    mock_analysis = {
        'timestamp': '2024-02-08 10:30:00',
        'query_context': 'Top products by revenue',
        'row_count': 3,
        'column_count': 3,
        'columns': ['product', 'revenue', 'profit'],
        'summary_statistics': {
            'revenue': {'mean': 8566.67, '50%': 8500, 'max': 10000, 'min': 7200},
            'profit': {'mean': 2570.00, '50%': 2550, 'max': 3000, 'min': 2160}
        },
        'insights': [
            'Dataset contains 3 records',
            'revenue: Range from 7200.00 to 10000.00',
            'profit: Range from 2160.00 to 3000.00'
        ]
    }
    
    print("🧪 Testing Executive Summary Generator (with rate limiting)\n")
    
    summary = generator.generate_executive_summary(
        "What are the top products by revenue?",
        mock_df,
        mock_analysis
    )
    
    print("=" * 80)
    print(summary)
    print("=" * 80)

if __name__ == "__main__":
    test_summary_generator()
