import scrapy
import re
from bs4 import BeautifulSoup
from workua_spider.config import technologies


class WorkuaSpider(scrapy.Spider):
    name = 'workua'
    allowed_domains = ['work.ua']
    start_urls = ['https://www.work.ua/jobs-c%23/']

    def start_requests(self):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        for url in self.start_urls:
            yield scrapy.Request(url, headers=headers, callback=self.parse)

    def parse(self, response):
        for item in response.css('div.card.card-hover.card-visited'):
            vacancy_uri = item.css('h2 a::attr(href)').get()
            yield response.follow(vacancy_uri, callback=self.parse_vacancy)

        next_page = response.css('a.ga-pagination-default.pointer-none-in-all::attr(href)').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)

    def parse_vacancy(self, response):
        title = response.css('h1::text').get()
        company_elem = response.css('a.inline-block.mb-xs.hidden-print span.strong-500')
        company = company_elem.css('::text').get().strip() if company_elem else ""

        soup = BeautifulSoup(response.text, 'html.parser')
        description_block = soup.find(class_='card rounded-0-top rounded-20-top-xs pb-lg')
        if description_block:
            description_text = ' '.join(description_block.get_text(separator='\n').split())
        else:
            description_text = ""

        price_pattern = r'\b(\d{1,3}\s*\d{3})\s*–\s*(\d{1,3}\s*\d{3})\b'
        match = re.search(price_pattern, description_text)
        if match:
            min_price, max_price = match.groups()
            price = f"от {min_price} до {max_price}"
        else:
            price = ""

        description_lower = description_text.lower()
        techs = set([tech for tech in technologies if tech.lower() in description_lower])
        locations_list = [
            "Київ", "Дніпро", "Харків", "Одеса", "Дніпро", "Донецьк",
            "Львів", "Запоріжжя", "Кривий Ріг", "Миколаїв", "Севастополь"
                                                            "Маріуполь", "Луганськ", "Вінниця", "Сімферополь",
            "Херсон", "Чернігів", "Полтава", "Хмельницький",
            "Черкаси", "Чернівці", "Житомир", "Суми", "Рівне",
            "Івано-Франківськ", "Тернопіль", "Луцьк", "Дистанційна робота"
        ]
        location = next((loc for loc in locations_list if loc.lower() in description_lower), "")
        eng_prices = ['Beginner', 'Intermediate', 'Advanced', 'вище середнього',
                      'середній', "B2", "B1", "A2", "A1", "C1", "C2"]
        eng_lvl = next((eng_lvl for eng_lvl in eng_prices if eng_lvl.lower() in description_lower), "")

        yield {
            'title': title,
            'company': company,
            'location': location,
            'technologies': ', '.join(techs),
            'price': price,
            'eng_lvl': eng_lvl,
            'original_link': response.url
        }