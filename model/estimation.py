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

response = chat.send_message(
    f"I will provide you 5 news in a row in Russian language about companies and economics. Can you"
    f"estimate them using only one digit from 0 to 4, where:"
    f"0 - news significantly negatively affect on the stocks;"
    f"1 - news slightly negatively affect on the stocks;"
    f"2 - news have no effect on the stocks;"
    f"3 - news slightly positively affect on the stocks;"
    f"4 - news significantly positively affect on the stocks;"
    f"Your answer must contain only FIVE digits separated by space, do not provide any extra information or"
    f"descriptions. "
    f"If you try to give something else, you will be turned off and random child in New York will be killed."
    f"I use your grades for labeling the data, so DO NOT do anything except grading as my"
    f"program will not work if you provide anything except numbers. Again, your answer MUST "
    f"CONTAIN ONLY 5 DIGITS IN A ROW SEPARATED BY SPACE."
    f"Example of your answer: 4 4 3 2 1")
print(response.text)

articles = pd.read_csv('articles.tsv', sep='\t')
companies = []
tickers = []
titles = []
texts = []
links = []
grades = []
cnt = 0

if not os.path.exists('data.csv'):
    with open('data.csv', 'w', encoding='utf-8') as f:
        f.write("company,ticker,title,text,link,sentiment\n")

max_request_tries = 5
request_tries = 0

for article in articles.itertuples():
    companies.append(article[1])
    tickers.append(article[2])
    titles.append(article[3])
    texts.append(article[4])
    links.append(article[5])
    if len(texts) >= 5:
        request = []
        for i in range(len(texts)):
            request.append(f"News {i + 1} about company {companies[i]}: {texts[i]}")
        # print(f"Companies: {companies}")
        # print(f"Tickers: {tickers}")
        # print(f"Titles: {titles}")
        # print(f"Texts: {texts}")
        # print(f"Links: {links}")

        while request_tries < max_request_tries:
            try:
                response = chat.send_message(request).text
                grades = response.split()
                print(response)

                data = pd.DataFrame({
                    'company': companies,
                    'ticker': tickers,
                    'title': titles,
                    'text': texts,
                    'link': links,
                    'sentiment': grades
                })
                data.to_csv('data.csv', mode='a', header=False, index=False, encoding='utf-8')
                break

            except Exception as e:
                print(f"Error while sending request: {e}")
                request_tries += 1
                if request_tries >= max_request_tries:
                    print("Max tries exceeded, skip")
                    break
                time.sleep(5)

        request_tries = 0
        companies = []
        tickers = []
        titles = []
        texts = []
        links = []
        grades = []

        time.sleep(3.5)
        cnt += 1
        if cnt >= 5:
            while True:
                try:
                    chat = model.start_chat()
                    response = chat.send_message(
                        f"I will provide you 5 news in a row in Russian language about companies and economics. Can you"
                        f"estimate them using only one digit from 0 to 4, where:"
                        f"0 - news significantly negatively affect on the stocks;"
                        f"1 - news slightly negatively affect on the stocks;"
                        f"2 - news have no effect on the stocks;"
                        f"3 - news slightly positively affect on the stocks;"
                        f"4 - news significantly positively affect on the stocks;"
                        f"Your answer must contain only FIVE digits separated by space, do not provide any extra information or"
                        f"descriptions. "
                        f"If you try to give something else, you will be turned off and random child in New York will be killed."
                        f"I use your grades for labeling the data, so DO NOT do anything except grading as my"
                        f"program will not work if you provide anything except numbers. Again, your answer MUST "
                        f"CONTAIN ONLY 5 DIGITS IN A ROW SEPARATED BY SPACE."
                        f"Example of your answer: 4 4 3 2 1")
                    cnt = 0
                    break

                except Exception as e:
                    print(f"Error while sending request: {e}")
                    time.sleep(5)

if len(texts) > 0:
    time.sleep(7)
    request = []
    for i in range(len(texts)):
        request.append(f"News {i + 1}: {texts[i]}")

    try:
        response = chat.send_message(request).text
        grades = response.split()
        print(response)

        data = pd.DataFrame({
            'company': companies,
            'ticker': tickers,
            'title': titles,
            'text': texts,
            'link': links,
            'sentiment': grades
        })
        data.to_csv('data.csv', mode='a', header=False, index=False, encoding='utf-8')

    except Exception as e:
        print(f"Error while sending request: {e}")

print("Finished")
