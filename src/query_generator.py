"""
LLM Query Generator - Convert natural language to SQL using Gemini
"""
from google import genai
from config import Config
import json
import time

class QueryGenerator:
    """Generate SQL queries from natural language using Gemini API"""
    
    def __init__(self):
        self.client = genai.Client(api_key=Config.GEMINI_API_KEY)
        self.model_id = 'gemini-2.0-flash'
        
        # Rate limiting: minimum seconds between requests
        self.min_delay = 5  # 5 seconds between requests to avoid 429 errors
        self.last_request_time = 0
        
        # Database schema context
        self.schema_context = """
        Database: PostgreSQL
        Table: sales_data
        
        Columns:
        - id: SERIAL PRIMARY KEY
        - date: DATE (transaction date)
        - day: INTEGER (day of month)
        - month: VARCHAR(20) (month name)
        - year: INTEGER
        - customer_age: INTEGER
        - age_group: VARCHAR(50) (Youth (<25), Young Adults (25-34), Adults (35-64), Seniors (64+))
        - customer_gender: VARCHAR(10) (M/F)
        - country: VARCHAR(50)
        - state: VARCHAR(100)
        - product_category: VARCHAR(100)
        - sub_category: VARCHAR(100)
        - product: VARCHAR(200)
        - order_quantity: INTEGER
        - unit_cost: DECIMAL(10,2)
        - unit_price: DECIMAL(10,2)
        - profit: DECIMAL(10,2)
        - cost: DECIMAL(10,2)
        - revenue: DECIMAL(10,2)
        
        Notes:
        - All column names are lowercase
        - Date format: YYYY-MM-DD
        - Revenue = Unit_Price * Order_Quantity
        - Profit = Revenue - Cost
        """
        
    def _wait_for_rate_limit(self):
        """Enforce rate limiting between API calls"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_delay:
            wait_time = self.min_delay - time_since_last
            print(f" Rate limiting: waiting {wait_time:.1f}s...")
            time.sleep(wait_time)
        
        self.last_request_time = time.time()
        
    def generate_sql(self, natural_language_query):
        """
        Convert natural language question to SQL query
        
        Args:
            natural_language_query: User's question in plain English
            
        Returns:
            dict: {'sql': SQL query string, 'explanation': explanation of what query does}
        """
        prompt = f"""You are a SQL expert. Convert the following natural language question into a PostgreSQL query.

{self.schema_context}

User Question: {natural_language_query}

Requirements:
1. Generate ONLY valid PostgreSQL syntax
2. Use appropriate aggregations, joins, and filters
3. Include ORDER BY and LIMIT where appropriate
4. Use meaningful column aliases
5. Format the query for readability

Respond in JSON format:
{{
    "sql": "SELECT ...",
    "explanation": "This query retrieves..."
}}
"""
        
        try:
            response = self.client.models.generate_content(model=self.model_id,contents=prompt)
            response_text = response.text
            
            # Parse JSON response
            # Remove markdown code blocks if present
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            result = json.loads(response_text)
            
            return {
                'sql': result.get('sql', '').strip(),
                'explanation': result.get('explanation', '').strip(),
                'success': True
            }
            
        except Exception as e:
            error_msg = str(e)
            
            # Handle quota/rate limit errors specifically
            if '429' in error_msg or 'RESOURCE_EXHAUSTED' in error_msg:
                return {
                    'sql': None,
                    'explanation': None,
                    'success': False,
                    'error': 'Rate limit exceeded. Try again in a few minutes or enable billing for higher quota.',
                    'error_type': 'rate_limit'
                }
                
            return {
                'sql': None,
                'explanation': None,
                'success': False,
                'error': str(e)
            }
    
    def validate_and_improve_query(self, sql_query, error_message=None):
        """
        Validate and fix SQL query if it has errors
        
        Args:
            sql_query: The SQL query to validate
            error_message: Error message from database (if any)
            
        Returns:
            dict: Improved query or validation result
        """
        prompt = f"""You are a SQL expert. Review and improve this PostgreSQL query.

{self.schema_context}

Query to review:
{sql_query}

{'Error encountered: ' + error_message if error_message else 'Please validate and optimize this query.'}

Provide:
1. Corrected/improved query (if needed)
2. Explanation of changes
3. Potential issues to watch for

Respond in JSON format:
{{
    "sql": "corrected query",
    "changes": "what was changed and why",
    "warnings": "any potential issues"
}}
"""
        
        try:
            # Enforce rate limiting
            self._wait_for_rate_limit()
            
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=prompt
            )
            
            response_text = response.text
            
            # Parse JSON response
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            result = json.loads(response_text)
            
            return {
                'sql': result.get('sql', '').strip(),
                'changes': result.get('changes', '').strip(),
                'warnings': result.get('warnings', '').strip(),
                'success': True
            }
            
        except Exception as e:
            error_msg = str(e)
            # Handle quota/rate limit errors specifically
            if '429' in error_msg or 'RESOURCE_EXHAUSTED' in error_msg:
                return {
                    'success': False,
                    'error': 'Rate limit exceeded. Try again in a few minutes.',
                    'error_type': 'rate_limit'
                }
            
            return {
                'success': False,
                'error': str(e)
            }

def test_query_generator():
    """Test the query generator with sample questions"""
    generator = QueryGenerator()
    
    test_questions = [
        "What are the top 5 products by revenue?",
      #  "Show me monthly revenue trends for 2016",
      #  "Which age group has the highest average order quantity?",
      #  "Compare profit margins across different product categories"
    ]
    
    print("Testing Query Generator\n")
    
    for idx, question in enumerate(test_questions, 1):
        print(f"Question {idx}/{len(test_questions)}: {question}")
        result = generator.generate_sql(question)
        
        if result['success']:
            print(f"SQL Generated:")
            print(result['sql'])
            print(f"\nExplanation: {result['explanation']}\n")
        else:
            if result.get('error_type') == 'rate_limit':
                print(f"Rate limit hit: {result['error']}")
                print(f"Tip: Wait a few minutes or enable billing at https://ai.google.dev/pricing\n")
            else:
                print(f"Error: {result['error']}\n")
        
        print("-" * 80 + "\n")
        
        # Extra delay between test questions
        if idx < len(test_questions):
            print(f"Waiting before next question...\n")

if __name__ == "__main__":
    test_query_generator()
