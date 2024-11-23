import pandas as pd

df = pd.read_table('articles_raw.tsv')

df = df.replace(to_replace='\u00A0', value=' ', regex=True)
df = df.dropna()

missing_in_A = df[df['Text'].isna()]
print("All missing values in Text:")
print(missing_in_A)

missing_anywhere = df[df.isna().any(axis=1)]
print("Rows with missing values:")
print(missing_anywhere)

missing_positions = df.isna()
print("Columns with missing values:")
print(missing_positions)

missing = df.isna().any()
print("Missing:", missing)

all_filled = df.notna().all()
print("All values filled:", all_filled)

are_all_columns_filled = all(all_filled)
print("All columns filled:", are_all_columns_filled)

df.to_csv('articles.tsv', sep='\t', index=False)
