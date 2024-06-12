import scrapy


class WorkuaSpider(scrapy.Spider):
    name = 'workua'
    allowed_domains = ['work.ua']
    start_urls = ['https://www.work.ua/jobs-it/']
    pagination_page_count = 5  # Количество страниц для обхода

    def parse(self, response):
        for item in response.css('div.card.card-hover.card-visited'):
            vacancy_uri = item.css('h2 a::attr(href)').get()
            company_name = item.css('a[class*="inline-block mb-xs hidden-print"] > span.strong-500::text').get()

            workers = {
                'position': item.css('h2 a::text').get(),
                'name': item.css('div b::text').get(),
                'link': response.urljoin(vacancy_uri),
                'company': company_name  # Добавляем имя компании в workers
            }

            salary = item.css('h2 span:not(.text-muted) span::text').get()
            if salary:
                workers['salary'] = float(salary.replace(' грн', '').replace(' ', ''))

            if vacancy_uri:
                yield response.follow(vacancy_uri, self.parse_vacancy, meta={'workers': workers})

        next_page = response.css(
            'a.ga-pagination-default.pointer-none-in-all.link-icon[href*="page="]::attr(href)').get()
        if next_page and self.pagination_page_count > 0:
            self.pagination_page_count -= 1
            yield response.follow(next_page, self.parse)

    def parse_vacancy(self, response):
        workers = response.meta['workers']
        header_text = response.css('div.card > h2:not(#contactInfo)::text').get()
        desc_text = ' '.join(response.css('div.card > p.text-muted:not(#contactMessageHint)::text').getall())
        desc_text = ' '.join(desc_text.split())
        worker_age = response.css('div.card div.row div dl.dl-horizontal dd::text').get()
        if worker_age:
            worker_age = ' '.join(worker_age.split())
        workers['age'] = worker_age
        workers[
            'description'] = f"{header_text}: {desc_text}" if header_text and desc_text else header_text or desc_text
        yield workers
