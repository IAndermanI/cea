import pandas as pd

n = 250
grades = []
for i in range(n):
    x = int(input())
    grades.append(x)

articles = pd.read_csv('articles1.tsv', sep='\t')
data = pd.DataFrame({
    "text": articles["Статья"],
    "grade": grades
})

data.to_csv('data1.csv', index=False, encoding='utf-8')
