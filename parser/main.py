import requests
import csv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup as bs
import time

URL_TEMPLATES = ["https://www.rbc.ru/quote/ticker/69684",
                 "https://www.rbc.ru/quote/ticker/59256",
                 "https://www.rbc.ru/quote/ticker/59762",
                 "https://www.rbc.ru/quote/ticker/59825"]

TICKERS = ["YDEX", "GAZP", "SBER", "TATN"]

CHROMEDRIVER_PATH = "C:/Program Files (x86)/chromedriver-win64/chromedriver.exe"
def fetch_full_page_content(url):
    """Use Selenium to fetch the full content of the given URL by scrolling."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    service = Service(executable_path=CHROMEDRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        driver.get(url)
        time.sleep(5)
        for _ in range(25):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

        page_content = driver.page_source
        return page_content
    finally:
        driver.quit()


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
        title = "Без названия"
    article_text = " ".join(p.get_text(strip=True) for p in paragraphs)
    return title, article_text


def save_to_csv(articles_info, ticker, filename="articles.tsv"):
    """Save the articles information to a CSV file."""
    with open(filename, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter='\t')
        for link, title, article_text in articles_info:
            writer.writerow([link, ticker, title, article_text])


def main():
    with open('articles.tsv', mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter='\t')
        writer.writerow(['Ссылка', 'Тикер', 'Заголовок статьи', 'Статья'])

    for i, URL_TEMPLATE in enumerate(URL_TEMPLATES):
        main_page_content = fetch_full_page_content(URL_TEMPLATE)
        main_soup = bs(main_page_content, "html.parser")
        links = extract_links(main_soup)

        articles_info = []

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

        save_to_csv(articles_info, TICKERS[i])

if __name__ == "__main__":
    main()
