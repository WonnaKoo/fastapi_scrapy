from sqlalchemy.orm import sessionmaker
from models import Vacancy, engine
from scrapy.exceptions import DropItem


class DatabasePipeline:
    def __init__(self):
        Session = sessionmaker(bind=engine)
        self.session = Session()

    def process_item(self, item, spider):
        try:
            vacancy = Vacancy(
                title=item['title'],
                company=item['company'],
                location=item['location'],
                technologies=item['technologies'],
                price=item['price'],
                eng_lvl=item['eng_lvl'],
                original_link=item['original_link']
            )
            self.session.add(vacancy)
            self.session.commit()
            spider.logger.info(f"Saved item in database: {item['title']}")
        except Exception as e:
            self.session.rollback()
            spider.logger.error(f"Error saving item in database: {e}")
            raise DropItem(f"Failed to save item: {item['original_link']}")

        return item

    def close_spider(self, spider):
        self.session.close()
