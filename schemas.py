from pydantic import BaseModel


class VacancyBase(BaseModel):
    title: str
    company: str
    location: str = None
    technologies: str
    level: str = None
    eng_lvl: str
    original_link: str


class VacancyCreate(VacancyBase):
    pass


class Vacancy(VacancyBase):
    id: int

    class Config:
        orm_mode = True
