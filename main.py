from fastapi import FastAPI, Depends, Request, Query
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
import schemas
import models
import database

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

templates = Jinja2Templates(directory="templates")

@app.get("/vacancies/", response_model=list[schemas.Vacancy])
def read_vacancies(
    sort_by: str = Query(None, title="Sort by", description="Field to sort by"),
    sort_order: str = Query("asc", title="Sort order", description="Sort order (asc or desc)"),
    country: str = None,
    skip: int = 0,
    limit: int = None,  # Изменили значение на None, чтобы не ограничивать лимит
    db: Session = Depends(database.get_db)
):
    query = db.query(models.Vacancy)

    # Применяем фильтр и сортировку по стране, если указан параметр country
    if country:
        query = query.filter(models.Vacancy.location == country)

    # Применяем сортировку, если указаны параметры sort_by и sort_order
    if sort_by:
        column = getattr(models.Vacancy, sort_by, None)
        if column is not None:
            if sort_order.lower() == "desc":
                query = query.order_by(column.desc())
            else:
                query = query.order_by(column)

    # Применяем смещение и лимит для пагинации, если указан limit
    if limit is not None:
        query = query.limit(limit)

    # Применяем смещение для пагинации
    vacancies = query.offset(skip).all()  # Убрали limit здесь

    return vacancies


@app.post("/vacancies/", response_model=schemas.Vacancy)
def create_vacancy(vacancy: schemas.VacancyCreate, db: Session = Depends(database.get_db)):
    db_vacancy = models.Vacancy(**vacancy.dict())
    db.add(db_vacancy)
    db.commit()
    db.refresh(db_vacancy)
    return db_vacancy

@app.get("/", response_class=HTMLResponse)
def read_vacancies_html(
    request: Request,
    sort_by: str = Query(None, title="Sort by", description="Field to sort by"),
    sort_order: str = Query("asc", title="Sort order", description="Sort order (asc or desc)"),
    country: str = None,
    skip: int = 0,
    limit: int = None,  # Изменили значение на None, чтобы не ограничивать лимит
    db: Session = Depends(database.get_db)
):
    query = db.query(models.Vacancy)

    # Применяем фильтр и сортировку по стране, если указан параметр country
    if country:
        query = query.filter(models.Vacancy.location == country)

    # Применяем сортировку, если указаны параметры sort_by и sort_order
    if sort_by:
        column = getattr(models.Vacancy, sort_by, None)
        if column is not None:
            if sort_order.lower() == "desc":
                query = query.order_by(column.desc())
            else:
                query = query.order_by(column)

    # Применяем смещение и лимит для пагинации, если указан limit
    if limit is not None:
        query = query.limit(limit)

    # Применяем смещение для пагинации
    vacancies = query.offset(skip).all()  # Убрали limit здесь

    # Передаем параметры в шаблон HTML
    return templates.TemplateResponse(
        "vacancies.html",
        {"request": request, "vacancies": vacancies, "sort_by": sort_by, "sort_order": sort_order},
    )
