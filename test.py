import scrapy
from sqlalchemy.orm import Session
from database import SessionLocal
import models

class WorkuaSpider(scrapy.Spider):
    name = 'workua'
    allowed_domains = ['work.ua']
    start_urls = ['https://www.work.ua/jobs-it/']

    def parse(self, response):
        for item in response.css('div.card.card-hover.card-visited'):
            vacancy_uri = item.css('h2 a::attr(href)').get()
            company_name = item.css('a[class*="inline-block mb-xs hidden-print"] > span.strong-500::text').get()

            workers = {
                'title': item.css('h2 a::text').get(),
                'company': company_name,
                'location': item.css('div.b::text').get(),
                'technologies': item.css('div.some-class::text').get(),
                'level': item.css('div.another-class::text').get(),
                'eng_lvl': item.css('div.yet-another-class::text').get(),
                'original_link': response.urljoin(vacancy_uri),
            }

            salary = item.css('h2 span:not(.text-muted) span::text').get()
            if salary:
                workers['salary'] = float(salary.replace(' грн', '').replace(' ', ''))

            if vacancy_uri:
                yield response.follow(vacancy_uri, self.parse_vacancy, meta={'workers': workers})

    def parse_vacancy(self, response):
        workers = response.meta['workers']
        header_text = response.css('div.card > h2:not(#contactInfo)::text').get()
        desc_text = ' '.join(response.css('div.card > p.text-muted:not(#contactMessageHint)::text').getall())
        desc_text = ' '.join(desc_text.split())
        worker_age = response.css('div.card div.row div dl.dl-horizontal dd::text').get()
        if worker_age:
            worker_age = ' '.join(worker_age.split())
        workers['age'] = worker_age
        workers['description'] = f"{header_text}: {desc_text}" if header_text and desc_text else header_text or desc_text

        db = SessionLocal()
        try:
            db_vacancy = models.Vacancy(**workers)
            db.add(db_vacancy)
            db.commit()
            db.refresh(db_vacancy)
        finally:
            db.close()

        yield workers
