from sqlalchemy.orm import sessionmaker
from models import Vacancy, engine
from scrapy.exceptions import DropItem

class DatabasePipeline:
    def __init__(self):
        # Создаем сессию для взаимодействия с базой данных
        Session = sessionmaker(bind=engine)
        self.session = Session()

    def process_item(self, item, spider):
        # Проверяем, если вакансия уже существует, пропускаем её
        exists = self.session.query(Vacancy).filter_by(original_link=item['link']).first()
        if exists:
            raise DropItem(f"Duplicate item found: {item['link']}")
        else:
            # Создаем новую запись
            vacancy = Vacancy(
                title=item.get('position'),
                company=item.get('name'),
                location=item.get('location', ''),
                technologies=item.get('technologies', ''),
                level=item.get('level', ''),
                eng_lvl=item.get('eng_lvl', ''),
                original_link=item.get('link')
            )
            # Добавляем и сохраняем в базу данных
            self.session.add(vacancy)
            self.session.commit()
            return item

    def close_spider(self, spider):
        # Закрываем сессию при завершении работы паука
        self.session.close()
