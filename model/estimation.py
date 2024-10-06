import time

import pandas as pd
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv('API_KEY')

genai.configure(api_key=API_KEY)

model = genai.GenerativeModel("gemini-1.5-flash")
chat = model.start_chat()


response = chat.send_message(f"I will provide you news in Russian language about companies and economics. Can you"
                             f"estimate them using only one digit from 1 to 5, where:"
                             f"1 - news significantly negatively affect on the stocks;"
                             f"2 - news slightly negatively affect on the stocks;"
                             f"3 - news have no effect on the stocks;"
                             f"4 - news slightly positively affect on the stocks;"
                             f"5 - news significantly positively affect on the stocks;"
                             f"Your answer must contain only ONE digit, do not provide any extra information or"
                             f"descriptions")
print(response.text)

# response = chat.send_message(f"Компания Apple объявила о презентации IPhone 16, сообщается, что батарея устройства может держать заряд максимум 5 часов, а камера будет отсутствовать")
# print(response.text)


articles = pd.read_csv('articles.tsv', sep='\t')
grades = []

cnt = 0
for article in articles.itertuples():
    # if cnt == 10:
    #     cnt = 0
    #     chat = model.start_chat()
    #     response = chat.send_message(
    #         f"I will provide you news in Russian language about companies and economics. Can you"
    #         f"estimate them using only one digit from 1 to 5, where:"
    #         f"1 - news significantly negatively affect on the stocks;"
    #         f"2 - news slightly negatively affect on the stocks;"
    #         f"3 - news have no effect on the stocks;"
    #         f"4 - news slightly positively affect on the stocks;"
    #         f"5 - news significantly positively affect on the stocks;"
    #         f"Your answer must contain only ONE digit, do not provide any extra information or"
    #         f"descriptions")

    text = article[4]
    response = chat.send_message(text)
    grade = response.text[0]
    print(grade)
    grades.append(grade)
    time.sleep(5)
    # cnt += 1

data = pd.DataFrame({
    'Text': articles['Статья'],
    'Grade': grades
})

data.to_csv('data.csv', index=False, encoding='utf-8')

print("Finished")
