"""
Data Loader Module - Load CSV data into PostgreSQL
"""
import pandas as pd
from sqlalchemy import text
from config import Config
import os

class DataLoader:
    """Load and manage data in PostgreSQL"""
    
    def __init__(self):
        self.engine = Config.get_engine()
    
    def load_csv_to_postgres(self, csv_path, table_name='sales_data'):
        """
        Load CSV file into PostgreSQL database
        
        Args:
            csv_path: Path to CSV file
            table_name: Name of the target table
        """
        try:
            print(f"Reading CSV file: {csv_path}")
            df = pd.read_csv(csv_path)
            
            # Convert date column to datetime
            df['Date'] = pd.to_datetime(df['Date'])
            
            # Rename columns to lowercase for easier SQL querying
            df.columns = df.columns.str.lower()
            
            print(f"Data shape: {df.shape}")
            print(f"Columns: {list(df.columns)}")
            
            # Check if table exists and get row count
            with self.engine.connect() as conn:
                result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                existing_rows = result.scalar()
                
                if existing_rows > 0:
                    print(f"Table '{table_name}' already has {existing_rows} rows.")
                    response = input("Do you want to replace the data? (yes/no): ")
                    if response.lower() != 'yes':
                        print("Data load cancelled.")
                        return False
                    
                    # Truncate table
                    conn.execute(text(f"TRUNCATE TABLE {table_name} RESTART IDENTITY"))
                    conn.commit()
                    print(f"Table truncated.")
            
            # Load data to PostgreSQL
            print(f"Loading data to PostgreSQL...")
            df.to_sql(table_name, self.engine, if_exists='append', index=False)
            
            # Verify load
            with self.engine.connect() as conn:
                result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                row_count = result.scalar()
            
            print(f"Successfully loaded {row_count} rows into '{table_name}'")
            
            # Show sample data
            print("\n Sample data:")
            with self.engine.connect() as conn:
                sample = pd.read_sql(f"SELECT * FROM {table_name} LIMIT 5", conn)
                print(sample)
            
            return True
            
        except Exception as e:
            print(f"Error loading data: {e}")
            return False
    
    def get_table_info(self, table_name='sales_data'):
        """Get information about the table"""
        try:
            with self.engine.connect() as conn:
                # Get row count
                result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                row_count = result.scalar()
                
                # Get column info
                query = f"""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = '{table_name}'
                ORDER BY ordinal_position
                """
                columns_df = pd.read_sql(query, conn)
                
                print(f"\n Table: {table_name}")
                print(f"Total Rows: {row_count:,}")
                print("\n Columns:")
                print(columns_df.to_string(index=False))
                
                return True
        except Exception as e:
            print(f"Error getting table info: {e}")
            return False

def main():
    """Main function to load data"""
    loader = DataLoader()
    
    # Path to your CSV file
    csv_path = "../data/sales_data.csv"  # Update this path
    
    if not os.path.exists(csv_path):
        print(f"CSV file not found: {csv_path}")
        print("Please update the csv_path variable with the correct path.")
        return
    
    # Load data
    success = loader.load_csv_to_postgres(csv_path)
    
    if success:
        # Show table info
        loader.get_table_info()

if __name__ == "__main__":
    main()
