"""
Main Orchestrator - Complete Automated Data Analysis Workflow
"""
import os
from datetime import datetime
from config import Config, test_connection
from query_generator import QueryGenerator
from automated_eda import AutomatedEDA
from summary_generator import SummaryGenerator

class AnalyticsWorkflow:
    """Main workflow orchestrator for automated data analysis"""
    
    def __init__(self):
        self.query_gen = QueryGenerator()
        self.eda = AutomatedEDA()
        self.summary_gen = SummaryGenerator()
        self.output_dir = "../outputs"
        os.makedirs(self.output_dir, exist_ok=True)
    
    def run_analysis(self, natural_language_query, save_sql=True):
        """
        Complete end-to-end analysis workflow
        
        Args:
            natural_language_query: User's question in plain English
            save_sql: Whether to save the generated SQL query
            
        Returns:
            dict: Complete analysis results
        """
        print("\n" + "=" * 80)
        print("AUTOMATED DATA ANALYSIS WORKFLOW")
        print("=" * 80)
        
        results = {
            'success': False,
            'query': natural_language_query,
            'timestamp': datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        }
        
        # Step 1: Generate SQL Query
        print(f"\nStep 1: Generating SQL Query...")
        print(f"Question: {natural_language_query}")
        
        query_result = self.query_gen.generate_sql(natural_language_query)
        
        if not query_result['success']:
            print(f"Failed to generate SQL: {query_result.get('error')}")
            return results
        
        sql_query = query_result['sql']
        explanation = query_result['explanation']
        
        print(f"SQL Generated:")
        print(f"{sql_query}")
        print(f"\nExplanation: {explanation}")
        
        results['sql_query'] = sql_query
        results['sql_explanation'] = explanation
        
        # Save SQL query if requested
        if save_sql:
            sql_filename = f"query_{results['timestamp']}.sql"
            sql_path = os.path.join("../sql_queries", sql_filename)
            os.makedirs("../sql_queries", exist_ok=True)
            
            with open(sql_path, 'w') as f:
                f.write(f"-- Generated: {results['timestamp']}\n")
                f.write(f"-- Question: {natural_language_query}\n")
                f.write(f"-- Explanation: {explanation}\n\n")
                f.write(sql_query)
            
            print(f"SQL saved: {sql_path}")
            results['sql_file'] = sql_path
        
        # Step 2: Execute Query
        print(f"\nStep 2: Executing Query...")
        
        df, error = self.eda.execute_query(sql_query)
        
        if error:
            print(f"Query execution failed: {error}")
            print(f"\nAttempting to fix query...")
            
            # Try to fix the query
            fix_result = self.query_gen.validate_and_improve_query(sql_query, error)
            
            if fix_result['success']:
                print(f"Query corrected")
                print(f"Changes: {fix_result['changes']}")
                
                sql_query = fix_result['sql']
                results['sql_query'] = sql_query
                
                # Retry execution
                df, error = self.eda.execute_query(sql_query)
                
                if error:
                    print(f"Query still failed: {error}")
                    results['error'] = error
                    return results
            else:
                results['error'] = error
                return results
        
        print(f"Query executed: {len(df)} rows returned")
        results['row_count'] = len(df)
        results['dataframe'] = df
        
        # Step 3: Automated EDA
        print(f"\nStep 3: Performing Automated EDA...")
        
        analysis_name = f"analysis_{results['timestamp']}"
        eda_results = self.eda.generate_eda_report(
            df, 
            natural_language_query, 
            analysis_name
        )
        
        results['eda_results'] = eda_results
        print(f"EDA completed")
        
        # Step 4: Generate Executive Summary
        print(f"\nStep 4: Generating Executive Summary...")
        
        summary = self.summary_gen.generate_executive_summary(
            natural_language_query,
            df,
            eda_results
        )
        
        results['executive_summary'] = summary
        print(f"Summary generated")
        
        # Step 5: Create Complete Report
        print(f"\n📋 Step 5: Creating Complete Report...")
        
        full_report = self.summary_gen.generate_detailed_report(
            natural_language_query,
            sql_query,
            df,
            eda_results,
            summary
        )
        
        report_filename = f"complete_report_{results['timestamp']}.md"
        report_path = self.summary_gen.save_report(full_report, report_filename)
        
        results['report_file'] = report_path
        results['success'] = True
        
        # Print summary
        print("\n" + "=" * 80)
        print("ANALYSIS COMPLETE!")
        print("=" * 80)
        print(f"\nResults Summary:")
        print(f"  - Rows analyzed: {len(df):,}")
        print(f"  - Visualizations: {len(eda_results.get('visualization_files', []))}")
        print(f"  - Tableau exports: {len(eda_results.get('tableau_files', []))}")
        print(f"  - Report file: {report_path}")
        
        print(f"\nExecutive Summary Preview:")
        print("-" * 80)
        print(summary[:500] + "..." if len(summary) > 500 else summary)
        print("-" * 80)
        
        return results
    
    def interactive_mode(self):
        """Run in interactive mode for multiple queries"""
        print("\n" + "=" * 80)
        print("AI-POWERED SALES ANALYTICS SYSTEM - INTERACTIVE MODE")
        print("=" * 80)
        print("\nAsk questions about your sales data in plain English!")
        print("Type 'exit' or 'quit' to end the session.\n")
        
        while True:
            query = input("Your question: ").strip()
            
            if query.lower() in ['exit', 'quit', 'q']:
                print("\nThanks for using the Analytics System!")
                break
            
            if not query:
                continue
            
            self.run_analysis(query)
            print("\n" + "=" * 80 + "\n")

def main():
    """Main entry point"""
    print("🔍 Checking database connection...")
    if not test_connection():
        print("Cannot connect to database. Please check your configuration.")
        return
    
    workflow = AnalyticsWorkflow()
    
    example_queries = [
        "Generate a SQL query for detailed list of sales for the top 10 products including the Order Date, Category, Sub-category, Coountry, Region, Quantity, Number of Orders, Customer demographics (Age group , gender), Profit, and Revenue. Include the order_date as a single date column"
    ]
    
    print("\n" + "=" * 80)
    print("RUNNING EXAMPLE ANALYSES")
    print("=" * 80)
    
    # Run example query
    if example_queries:
        workflow.run_analysis(example_queries[0])
    
    # Uncomment below for interactive mode
    # workflow.interactive_mode()

if __name__ == "__main__":
    main()
