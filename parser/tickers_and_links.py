import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup as bs
import time

CHROMEDRIVER_PATH = "C:/Program Files (x86)/chromedriver-win64/chromedriver.exe"
URL = "https://www.rbc.ru/quote/catalog/?type=share&sort=leaders"

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
        for _ in range(50):  # Adjust the range as needed to ensure full page load
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

        page_content = driver.page_source
        return page_content
    finally:
        driver.quit()

def extract_tickers_and_links(page_content):
    soup = bs(page_content, 'html.parser')
    catalog_container = soup.find('div', class_='catalog__container js-catalog-container')
    ticker_dict = {}

    if catalog_container:
        items = catalog_container.find_all('span', class_='catalog__line')
        for item in items:
            link_tag = item.find('a', class_='catalog__name')
            ticker_tag = item.find('span', class_='catalog__inner')
            if link_tag and ticker_tag:
                link = link_tag['href']
                ticker = ticker_tag.text.strip()
                ticker_dict[ticker] = link

    return ticker_dict

def save_to_json(data, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)  # Pretty-print JSON [[1]]

def main():
    page_content = fetch_full_page_content(URL)
    ticker_dict = extract_tickers_and_links(page_content)
    save_to_json(ticker_dict, 'companies.json')

if __name__ == "__main__":
    main()
