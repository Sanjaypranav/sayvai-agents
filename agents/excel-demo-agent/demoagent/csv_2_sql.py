import numpy as np
import pandas as pd

# Create a dataframe

file_path = 'data\AAPL.csv'
df = pd.read_csv(file_path)
sql_db = df.to_sql('AAPL', con="sqlite:///sayvai.db",
                   if_exists='replace', index=False)
