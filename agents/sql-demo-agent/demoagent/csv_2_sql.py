import pandas as pd
import numpy as np

# Create a dataframe

file_path = 'E:\work@savyai\sayvai-demo-agents\sql-demo-agent\data\AAPL.csv'
df = pd.read_csv(file_path)
sql_db = df.to_sql('AAPL', con="sqlite:///sayvai.db", if_exists='replace', index=False)