import pandas as pd
import numpy as np
import re
import os
import logging
from sqlalchemy import create_engine
from typing import Optional

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DataPipeline:
    def __init__(self, db_connection_string: Optional[str] = None):
        """
        Initializes the data pipeline.
        :param db_connection_string: SQLAlchemy connection string.
        """
        self.db_connection_string = db_connection_string
        if not self.db_connection_string:
            # Default to local postgres if not provided
            self.db_connection_string = os.environ.get(
                'DB_CONNECTION_STRING', 
                'postgresql://postgres:postgres@localhost:5432/retail_db'
            )
        self.engine = create_engine(self.db_connection_string)

    def clean_column_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Convert raw header names into clean snake_case.
        """
        logger.info("Cleaning column names...")
        def to_snake_case(name):
            # Strip whitespace, replace special chars with space, then replace spaces with underscores, lowercased
            name = str(name).strip()
            name = re.sub(r'[^a-zA-Z0-9\s_]', '', name)
            name = re.sub(r'[\s_]+', '_', name)
            return name.lower()
        
        df.columns = [to_snake_case(col) for col in df.columns]
        return df

    def impute_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Impute missing numerical fields (e.g., purchase_amount, review_rating) 
        using the median grouped by categorical features (category and gender).
        """
        logger.info("Imputing missing values...")
        
        # Identify target columns if they exist
        target_cols = [col for col in ['purchase_amount', 'review_rating'] if col in df.columns]
        group_cols = [col for col in ['category', 'gender'] if col in df.columns]

        if not target_cols or not group_cols:
            logger.warning("Target columns or group columns for imputation not found. Skipping imputation.")
            return df

        for target in target_cols:
            if df[target].isnull().any():
                logger.info(f"Imputing missing values for {target} grouped by {group_cols}")
                # Impute based on group median
                df[target] = df[target].fillna(
                    df.groupby(group_cols)[target].transform('median')
                )
                
                # If there are still missing values (e.g., a group had all NaNs), fill with global median
                if df[target].isnull().any():
                    global_median = df[target].median()
                    df[target] = df[target].fillna(global_median)
                    
        return df

    def engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create age_group, purchase_frequency_score, and clv_proxy.
        """
        logger.info("Engineering features...")
        
        # 1. Age Group
        if 'age' in df.columns:
            bins = [0, 25, 35, 50, 65, np.inf]
            labels = ['18-25', '26-35', '36-50', '51-65', '65+']
            df['age_group'] = pd.cut(df['age'], bins=bins, labels=labels, right=True)
            
        # 2. Purchase Frequency Score (Assume we have a 'historical_purchases' or similar, else we mock)
        # If transaction data, we'd group by customer_id. Assuming customer-level data here.
        if 'historical_purchases' in df.columns:
            # Standardized tiers: Low (bottom 33%), Medium (middle 33%), High (top 33%)
            df['purchase_frequency_score'] = pd.qcut(
                df['historical_purchases'].rank(method='first'), 
                q=3, 
                labels=['Low', 'Medium', 'High']
            )
            
        # 3. CLV Proxy: clv_proxy based on frequency and average spend
        if 'historical_purchases' in df.columns and 'purchase_amount' in df.columns:
            # Simple Proxy: historical_purchases * purchase_amount (assuming purchase_amount is AOV or recent spend)
            df['clv_proxy'] = df['historical_purchases'] * df['purchase_amount']
            
        return df

    def validate_data(self, df: pd.DataFrame):
        """
        Sanity assertions for null values.
        """
        logger.info("Validating data...")
        
        # Check specific columns we care about
        critical_cols = ['purchase_amount', 'review_rating']
        for col in critical_cols:
            if col in df.columns:
                null_count = df[col].isnull().sum()
                assert null_count == 0, f"Validation failed: {col} contains {null_count} null values."
                
        logger.info("Data validation passed.")

    def export_data(self, df: pd.DataFrame, output_path: str, table_name: str = 'clean_customer_shopping'):
        """
        Export to CSV and load directly to PostgreSQL via SQLAlchemy.
        """
        logger.info(f"Exporting data to {output_path}...")
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Export to CSV
        df.to_csv(output_path, index=False)
        logger.info("CSV export completed.")
        
        # Load to PostgreSQL
        try:
            logger.info(f"Loading data into PostgreSQL table: {table_name}...")
            df.to_sql(name=table_name, con=self.engine, if_exists='replace', index=False)
            logger.info("PostgreSQL load completed.")
        except Exception as e:
            logger.error(f"Failed to load data into PostgreSQL: {e}")
            logger.warning("Please ensure PostgreSQL is running and credentials are correct.")

    def generate_mock_data(self, n_rows=1000) -> pd.DataFrame:
        """
        Generate mock data for demonstration if no raw data is provided.
        """
        logger.info(f"Generating {n_rows} rows of mock data...")
        np.random.seed(42)
        
        categories = ['Electronics', 'Clothing', 'Home & Garden', 'Sports', 'Toys']
        genders = ['Male', 'Female', 'Other']
        
        df = pd.DataFrame({
            'Customer ID': range(1, n_rows + 1),
            'Age': np.random.randint(18, 70, n_rows),
            'Gender': np.random.choice(genders, n_rows, p=[0.48, 0.48, 0.04]),
            'Category': np.random.choice(categories, n_rows),
            'Purchase Amount ($)': np.random.normal(150, 50, n_rows),
            'Review Rating / 5': np.random.normal(3.8, 0.8, n_rows),
            'Historical_Purchases': np.random.randint(1, 50, n_rows)
        })
        
        # Introduce some missing values
        df.loc[np.random.choice(df.index, size=int(n_rows*0.05)), 'Purchase Amount ($)'] = np.nan
        df.loc[np.random.choice(df.index, size=int(n_rows*0.1)), 'Review Rating / 5'] = np.nan
        
        # Ensure values stay in bounds
        df['Purchase Amount ($)'] = df['Purchase Amount ($)'].clip(lower=5.0)
        df['Review Rating / 5'] = df['Review Rating / 5'].clip(lower=1.0, upper=5.0)
        
        return df

    def run(self, raw_data_path: Optional[str] = None):
        """
        Execute the full pipeline.
        """
        logger.info("Starting Data Pipeline...")
        
        if raw_data_path and os.path.exists(raw_data_path):
            logger.info(f"Reading raw data from {raw_data_path}")
            df = pd.read_csv(raw_data_path)
        else:
            logger.warning("No raw data path provided or file not found. Generating mock data.")
            df = self.generate_mock_data()
            
        df = self.clean_column_names(df)
        df = self.impute_missing_values(df)
        df = self.engineer_features(df)
        self.validate_data(df)
        
        output_csv = 'data/processed/clean_customer_shopping.csv'
        self.export_data(df, output_csv)
        
        logger.info("Data Pipeline completed successfully.")

if __name__ == "__main__":
    pipeline = DataPipeline()
    # To run with real data, uncomment and provide path:
    # pipeline.run(raw_data_path='data/raw/raw_customer_shopping.csv')
    
    # Run with mock data
    pipeline.run()
