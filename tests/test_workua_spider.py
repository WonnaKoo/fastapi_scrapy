import unittest
import os
from scrapy.http import HtmlResponse
from workua_spider.spiders.workua import WorkuaSpider
from scrapy.utils.test import get_crawler



class TestWorkuaSpider(unittest.TestCase):

    def setUp(self):
        self.spider = WorkuaSpider()
        self.test_pages_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'test_pages'))

    def test_parse(self):
        list_page_path = os.path.join(self.test_pages_dir, 'list_page.html')
        with open(list_page_path, 'r', encoding='utf-8') as f:
            file_content = f.read()
        response = HtmlResponse(url='http://example.com', body=file_content, encoding='utf-8')
        results = list(self.spider.parse(response))
        self.assertGreater(len(results), 0)

    def test_parse_vacancy(self):
        vacancy_page_path = os.path.join(self.test_pages_dir, 'vacancy_page.html')
        with open(vacancy_page_path, 'r', encoding='utf-8') as f:
            file_content = f.read()
        response = HtmlResponse(url='http://example.com', body=file_content, encoding='utf-8')
        result = self.spider.parse_vacancy(response)
        result_data = next(result)
        self.assertIn('title', result_data)
        self.assertIn('company', result_data)


class TestWorkuaSpider(unittest.TestCase):

    def setUp(self):
        self.spider = WorkuaSpider()

    def test_parse(self):
        html_content = """
        <html>
        <body>
            <div class="card card-hover card-visited">
                <h2><a href="https://www.example.com/job/1">Job 1</a></h2>
            </div>
            <div class="card card-hover card-visited">
                <h2><a href="https://www.example.com/job/2">Job 2</a></h2>
            </div>
        </body>
        </html>
        """

        response = HtmlResponse(url='https://www.example.com/jobs', body=html_content, encoding='utf-8')
        request = next(self.spider.parse(response))

        self.assertEqual(request.url, 'https://www.example.com/job/1')
        self.assertEqual(request.callback, self.spider.parse_vacancy)


class Vacancy:
    def __init__(self, title, company, location, technologies):
        self.title = title
        self.company = company
        self.location = location
        self.technologies = technologies

    def __repr__(self):
        return f"<Vacancy(title='{self.title}', company='{self.company}', location='{self.location}', technologies='{self.technologies}')>"


class TestVacancy(unittest.TestCase):

    def setUp(self):
        self.vacancy = Vacancy("Software Engineer", "Tech Company", "New York", ["Python", "Django"])

    def test_vacancy_representation(self):
        self.assertEqual(repr(self.vacancy), "<Vacancy(title='Software Engineer', company='Tech Company', location='New York', technologies='['Python', 'Django']')>")

    def test_vacancy_attributes(self):
        self.assertEqual(self.vacancy.title, "Software Engineer")
        self.assertEqual(self.vacancy.company, "Tech Company")
        self.assertEqual(self.vacancy.location, "New York")
        self.assertEqual(self.vacancy.technologies, ["Python", "Django"])


class TestVacancy(unittest.TestCase):

    def setUp(self):
        self.vacancy = Vacancy("Software Engineer", "Tech Company", "New York", ["Python", "Django"])

    def test_vacancy_representation(self):
        self.assertEqual(repr(self.vacancy), "<Vacancy(title='Software Engineer', company='Tech Company', location='New York', technologies='['Python', 'Django']')>")

    def test_vacancy_attributes(self):
        self.assertEqual(self.vacancy.title, "Software Engineer")
        self.assertEqual(self.vacancy.company, "Tech Company")
        self.assertEqual(self.vacancy.location, "New York")
        self.assertEqual(self.vacancy.technologies, ["Python", "Django"])


if __name__ == '__main__':
    unittest.main()
