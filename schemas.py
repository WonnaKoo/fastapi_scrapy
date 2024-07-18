from pydantic import BaseModel


class VacancyBase(BaseModel):
    title: str
    company: str
    location: str = None
    technologies: str
    price: str = None
    eng_lvl: str
    original_link: str

class Vacancy(VacancyBase):
    id: int

    class Config:
        orm_mode = True