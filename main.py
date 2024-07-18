from fastapi import FastAPI, Depends, Request, Query, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from sqlalchemy import or_
from starlette.staticfiles import StaticFiles
import schemas

import models
import database

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

# Монтируем статические файлы
app.mount("/static", StaticFiles(directory="static"), name="static")

# Инициализируем шаблоны Jinja2
templates = Jinja2Templates(directory="templates")

# Получение соединения с базой данных
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Маршрут для отображения страницы с вакансиями
@app.get("/", response_class=HTMLResponse)
def read_vacancies_html(
    request: Request,
    sort_by: str = Query(None, title="Sort by", description="Field to sort by"),
    sort_order: str = Query("asc", title="Sort order", description="Sort order (asc or desc)"),
    search_query: str = Query(None, title="Search query", description="Search query for filtering vacancies"),
    db: Session = Depends(get_db)
):
    query = db.query(models.Vacancy)

    # Применяем фильтр по полю title, если передан параметр search_query
    if search_query:
        search = f"%{search_query}%"
        query = query.filter(models.Vacancy.title.ilike(search))

    # Применяем сортировку, если переданы параметры sort_by и sort_order
    if sort_by:
        column = getattr(models.Vacancy, sort_by, None)
        if column is not None:
            if sort_order.lower() == "desc":
                query = query.order_by(column.desc())
            else:
                query = query.order_by(column)

    vacancies = query.all()

    return templates.TemplateResponse(
        "vacancies.html",
        {"request": request, "vacancies": vacancies, "sort_by": sort_by, "sort_order": sort_order, "search_query": search_query},
    )

# Маршрут для обработки POST запроса поиска
@app.post("/search", response_class=HTMLResponse)
def search_vacancies(
    request: Request,
    search_query: str = Form(...),
    db: Session = Depends(get_db)
):
    query = db.query(models.Vacancy)

    # Применяем фильтр по полю title, если передан параметр search_query
    if search_query:
        search = f"%{search_query}%"
        query = query.filter(models.Vacancy.title.ilike(search))

    vacancies = query.all()

    return templates.TemplateResponse(
        "vacancies.html",
        {"request": request, "vacancies": vacancies, "search_query": search_query},
    )

# Маршрут для создания вакансии
@app.post("/vacancies/", response_model=schemas.Vacancy)
def create_vacancy(vacancy: schemas.VacancyBase, db: Session = Depends(database.get_db)):
    db_vacancy = models.Vacancy(**vacancy.dict())
    db.add(db_vacancy)
    db.commit()
    db.refresh(db_vacancy)
    return db_vacancy
