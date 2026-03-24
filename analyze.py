import pandas as pd

df = pd.read_csv('data/raw/creditcard.csv')
print(f"Rows: {len(df)}, Columns: {len(df.columns)}")
print(f"Columns: {list(df.columns)}")
print(f"Missing: {df.isnull().sum().sum()}")
print(f"Class dist: {df['Class'].value_counts().to_dict()}")
print(f"Fraud rate: {df['Class'].mean()*100:.2f}%")
