import requests
import csv
import time
import json
import unicodedata
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup as bs
from selenium.webdriver.common.by import By

URL_TEMPLATES = []
COMPANY_NAME = []
TICKERS = []

with open('companies.json', 'r', encoding="utf8") as file:
    companies = json.load(file)

for company in companies:
    COMPANY_NAME.append(company)
    URL_TEMPLATES.append(companies[company])

CHROMEDRIVER_PATH = "C:/Program Files (x86)/chromedriver-win64/chromedriver.exe"

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920,1080")
service = Service(executable_path=CHROMEDRIVER_PATH)
driver = webdriver.Chrome(service=service, options=chrome_options)


def fetch_full_page_content(url):
    """Use Selenium to fetch the full content of the given URL by scrolling."""
    try:
        driver.get(url)
        TICKERS.append(driver.find_elements(By.CLASS_NAME, "chart__info__name-short")[0].text)
        time.sleep(5)
        for page_num in range(50):
            last_height = driver.execute_script("return document.body.scrollHeight")
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            new_height = driver.execute_script("return document.body.scrollHeight")
            print(f'Page: {page_num + 1}')
            if new_height == last_height:
                break

        page_content = driver.page_source
        return page_content
    finally:
        print("End of the site")


def extract_links(soup):
    vacancies_names = soup.find_all('a', class_='q-item__link')
    links = set()
    for name in vacancies_names:
        if 'href' in name.attrs:
            links.add(name['href'])
    return links


def extract_article_details(soup):
    title_tag = soup.find('h1')
    paragraphs = soup.find_all('p')

    if title_tag:
        title = title_tag.get_text(strip=True)
    else:
        title = "Untitled"
    article_text = " ".join(p.get_text(" ", strip=True) for p in paragraphs)
    article_text = unicodedata.normalize('NFKC', article_text)
    return title, article_text


def save_to_csv(articles_info, ticker, filename="articles_raw.tsv"):
    """Save the articles information to a CSV file."""
    with open(filename, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter='\t')
        for link, title, article_text in articles_info:
            writer.writerow([ticker[0], ticker[1], title, article_text, link])


def main():
    with open('articles_raw.tsv', mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter='\t')
        writer.writerow(['Name', 'Ticker', 'Title', 'Text', 'Link'])

    for i, URL_TEMPLATE in enumerate(URL_TEMPLATES):
        main_page_content = fetch_full_page_content(URL_TEMPLATE)
        main_soup = bs(main_page_content, "html.parser")
        links = extract_links(main_soup)

        articles_info = []
        company = [COMPANY_NAME[i], TICKERS[i]]

        for link in links:
            try:
                response = requests.get(link)
                response.raise_for_status()
                linked_page_content = response.text
                linked_soup = bs(linked_page_content, "html.parser")
                title, article_text = extract_article_details(linked_soup)
                articles_info.append((link, title, article_text))
            except Exception as e:
                print(f"Error fetching {link}: {e}")

        save_to_csv(articles_info, company)


if __name__ == "__main__":
    main()
