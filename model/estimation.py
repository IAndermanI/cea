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


response = chat.send_message(f"Imagine that you can answer only using digits to every message."
                             f"I will provide you 5 news in a row in Russian language about companies and economics. Can you"
                             f"estimate them using only one digit from 1 to 5, where:"
                             f"1 - news significantly negatively affect on the stocks;"
                             f"2 - news slightly negatively affect on the stocks;"
                             f"3 - news have no effect on the stocks;"
                             f"4 - news slightly positively affect on the stocks;"
                             f"5 - news significantly positively affect on the stocks;"
                             f"Your answer must contain only FIVE digits separated by space, do not provide any extra information or"
                             f"descriptions. "
                             f"If you try to give something else, you will be turned off and random child in New York will be killed."
                             f"I use your grades for labeling the data, so DO NOT do anything except grading as my"
                             f"program will not work if you provide anything except numbers. Again, your answer MUST "
                             f"CONTAIN ONLY 5 DIGITS IN A ROW SEPARATED BY SPACE."
                             f"Example of your answer: 5 5 4 3 2")
print(response.text)

# response = chat.send_message(f"Компания Apple объявила о презентации IPhone 16, сообщается, что батарея устройства может держать заряд максимум 5 часов, а камера будет отсутствовать")
# print(response.text)


articles = pd.read_csv('articles.tsv', sep='\t')
grades = []
texts = []
cnt = 0

if not os.path.exists('data.csv'):
    with open('data.csv', 'w', encoding='utf-8') as f:
        f.write("text,grade\n")

for article in articles.itertuples():
    texts.append(article[4])
    if len(texts) >= 5:
        request = []
        for i in range(len(texts)):
            request.append(f"News {i + 1}: {texts[i]}")

        try:
            response = chat.send_message(request).text
            grades = response.split()
            print(response)

            data = pd.DataFrame({
                'text': texts,
                'grade': grades
            })
            data.to_csv('data.csv', mode='a', header=False, index=False, encoding='utf-8')

        except Exception as e:
            print(f"Error while sending request: {e}")

        texts = []
        time.sleep(5)
        cnt += 1
        if cnt >= 5:
            chat = model.start_chat()
            response = chat.send_message(f"I will provide you 5 news in a row in Russian language about companies and economics. Can you"
                                         f"estimate them using only one digit from 1 to 5, where:"
                                         f"1 - news significantly negatively affect on the stocks;"
                                         f"2 - news slightly negatively affect on the stocks;"
                                         f"3 - news have no effect on the stocks;"
                                         f"4 - news slightly positively affect on the stocks;"
                                         f"5 - news significantly positively affect on the stocks;"
                                         f"Your answer must contain only FIVE digits separated by space, do not provide any extra information or"
                                         f"descriptions. "
                                         f"If you try to give something else, you will be turned off and random child in New York will be killed."
                                         f"I use your grades for labeling the data, so DO NOT do anything except grading as my"
                                         f"program will not work if you provide anything except numbers. Again, your answer MUST "
                                         f"CONTAIN ONLY 5 DIGITS IN A ROW SEPARATED BY SPACE."
                                         f"Example of your answer: 5 5 4 3 2")
            cnt = 0

if len(texts) > 0:
    request = []
    for i in range(len(texts)):
        request.append(f"News {i + 1}: {texts[i]}")

    try:
        response = chat.send_message(request).text
        grades = response.split()
        print(response)

        data = pd.DataFrame({
            'text': texts,
            'grade': grades
        })
        data.to_csv('data.csv', mode='a', header=False, index=False, encoding='utf-8')

    except Exception as e:
        print(f"Error while sending request: {e}")

print("Finished")
