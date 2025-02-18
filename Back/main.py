from fastapi import HTTPException, Query
from sqlalchemy import asc, desc, or_
from fastapi import FastAPI, HTTPException, Depends, Query
from sqlalchemy import Index, create_engine, or_, func, asc, desc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, selectinload, joinedload
from models import App, Category, Developer
from datetime import datetime
import math
import time
from collections import Counter
import os
from typing import Optional
from pydantic import BaseModel

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://myuser:admin@localhost/playStore")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

app = FastAPI()


Index("idx_covering_category_name_rating",
      App.category_id, App.app_name, App.rating)

Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class AppCreate(BaseModel):
    app_name: str
    category_id: int
    price: float
    size: Optional[float] = None
    minimum_android_version: Optional[str] = None
    developer_name: str
    developer_website: Optional[str] = None
    developer_email: Optional[str] = None
    ad_supported: bool = False
    in_app_purchases: bool = False
    editors_choice: bool = False


@app.post("/apps/", response_model=dict)
def create_app(
    app_data: AppCreate,
    db: Session = Depends(get_db)
):
    developer = db.query(Developer).filter(
        Developer.developer_name == app_data.developer_name,
        Developer.developer_website == app_data.developer_website,
        Developer.developer_email == app_data.developer_email
    ).first()

    if not developer:
        developer = Developer(
            developer_name=app_data.developer_name,
            developer_website=app_data.developer_website,
            developer_email=app_data.developer_email
        )
        db.add(developer)
        db.flush()
    app_entry = App(
        app_name=app_data.app_name,
        category_id=app_data.category_id,
        developer_id=developer.developer_id,
        rating=0,
        rating_count=0,
        installs=0,
        minimum_installs=0,
        maximum_installs=0,
        price=app_data.price,
        is_free=app_data.price == 0,
        size=app_data.size,
        currency="USD",
        minimum_android_version=app_data.minimum_android_version,
        released=datetime.now(),
        last_updated=datetime.now(),
        ad_supported=app_data.ad_supported,
        in_app_purchases=app_data.in_app_purchases,
        editors_choice=app_data.editors_choice,
        scraped_time=datetime.now(),
        content_rating=""
    )

    db.add(app_entry)
    try:
        db.commit()
        db.refresh(app_entry)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Database error: {str(e)}")

    return {"app_id": app_entry.app_id, "app_name": app_entry.app_name}


@app.put("/apps/{app_id}", response_model=dict)
def update_app(app_id: int, app_data: dict, db: Session = Depends(get_db)):
    app_entry = db.query(App).options(
        joinedload(App.category),
        joinedload(App.developer)
    ).filter(App.app_id == app_id).first()

    if app_entry is None:
        raise HTTPException(status_code=404, detail="App not found")

    app_entry.app_name = app_data.get('app_name', app_entry.app_name)
    app_entry.rating = app_data.get('rating', app_entry.rating)
    app_entry.rating_count = app_data.get(
        'rating_count', app_entry.rating_count)
    app_entry.content_rating = app_data.get(
        'content_rating', app_entry.content_rating)
    app_entry.installs = app_data.get('installs', app_entry.installs)
    app_entry.price = app_data.get('price', app_entry.price)
    app_entry.size = app_data.get('size', app_entry.size)
    app_entry.released = app_data.get('released', app_entry.released)
    app_entry.last_updated = app_data.get(
        'last_updated', app_entry.last_updated)

    category_name = app_data.get('category_name')
    if category_name is not None:
        category_entry = db.query(Category).filter(
            Category.category_name == category_name).first()
        if category_entry is None:
            category_entry = Category(category_name=category_name)
            db.add(category_entry)
            db.flush()
        app_entry.category = category_entry

    developer_data = {
        'developer_name': app_data.get('developer_name'),
        'developer_email': app_data.get('developer_email'),
        'developer_website': app_data.get('developer_website')
    }
    if any(developer_data.values()):
        developer_name = developer_data['developer_name']
        developer_entry = db.query(Developer).filter(
            Developer.developer_name == developer_name).first()
        if developer_entry is None:
            developer_entry = Developer(
                **{k: v for k, v in developer_data.items() if v is not None})
            db.add(developer_entry)
            db.flush()
        app_entry.developer = developer_entry

    db.commit()
    db.refresh(app_entry)

    return {"app_id": app_entry.app_id, "app_name": app_entry.app_name}


@app.delete("/apps/{app_id}", response_model=dict)
def delete_app(app_id: int, db: Session = Depends(get_db)):
    app_entry = db.query(App).filter(App.app_id == app_id).first()
    if app_entry is None:
        raise HTTPException(status_code=404, detail="App not found")
    db.delete(app_entry)
    db.commit()
    return {"message": "App deleted successfully"}


SORT_COLUMNS = {
    "app_name": App.app_name,
    "category_name": Category.category_name,
    "developer_name": Developer.developer_name,
    "rating": App.rating,
    "installs": App.installs,
    "price": App.price,
    "size": App.size,
    "released": App.released,
    "last_updated": App.last_updated
}


@app.get("/apps/", response_model=dict)
def get_apps(
    db: Session = Depends(get_db),
    min_rating: float = Query(None, ge=0, le=5),
    max_rating: float = Query(None, ge=0, le=5),
    min_price: float = Query(None, ge=0),
    max_price: float = Query(None, ge=0),
    is_free: bool = Query(None),
    category_id: int = Query(None, ge=1),
    ad_supported: bool = Query(None),
    in_app_purchases: bool = Query(None),
    editors_choice: bool = Query(None),
    search_query: str = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    sort_by: str = Query("rating", regex="|".join(SORT_COLUMNS.keys())),
    sort_order: str = Query("desc", regex="asc|desc")
):
    try:
        start_time = time.perf_counter()

        if sort_by not in SORT_COLUMNS:
            raise HTTPException(
                status_code=400, detail="Invalid sort_by value")

        order = desc(SORT_COLUMNS[sort_by]) if sort_order == "desc" else asc(
            SORT_COLUMNS[sort_by])

        query = (
            db.query(App)
            .options(selectinload(App.category), selectinload(App.developer))
        )

        if min_rating is not None:
            query = query.filter(App.rating >= min_rating)
        if max_rating is not None:
            query = query.filter(App.rating <= max_rating)
        if min_price is not None:
            query = query.filter(App.price >= min_price)
        if max_price is not None:
            query = query.filter(App.price <= max_price)
        if is_free is not None:
            query = query.filter(App.is_free == is_free)
        if ad_supported is not None:
            query = query.filter(App.ad_supported == ad_supported)
        if in_app_purchases is not None:
            query = query.filter(App.in_app_purchases == in_app_purchases)
        if editors_choice is not None:
            query = query.filter(App.editors_choice == editors_choice)
        if category_id is not None:
            query = query.filter(App.category_id == category_id)

        if search_query:
            query = query.outerjoin(App.category).outerjoin(App.developer)
            filters = [
                App.app_name.ilike(f"%{search_query}%"),
                Developer.developer_name.ilike(f"%{search_query}%"),
                Developer.developer_email.ilike(f"%{search_query}%"),
                Developer.developer_website.ilike(f"%{search_query}%")
            ]
            if category_id is None:
                filters.append(
                    Category.category_name.ilike(f"%{search_query}%"))
            query = query.filter(or_(*filters))

        if sort_by in ["Category Name", "Developer Name"]:
            query = query.join(Category).join(Developer)

        query = query.order_by(order)
        total_count = query.count()
        total_pages = math.ceil(total_count / page_size)
        offset = (page - 1) * page_size

        apps = query.offset(offset).limit(page_size).all()

        max_buttons = 5
        start_page = max(1, page - 2)
        end_page = min(total_pages, start_page + max_buttons - 1)
        page_numbers = list(range(start_page, end_page + 1))

        end_time = time.perf_counter()
        execution_time = end_time - start_time

        return {
            "total": total_count,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
            "page_numbers": page_numbers,
            "execution_time": execution_time,
            "data": [
                {
                    "Id": app.app_id,
                    "App Name": app.app_name,
                    "Category Name": getattr(app.category, "category_name", None),
                    "Developer Name": getattr(app.developer, "developer_name", None),
                    "Developer Email": getattr(app.developer, "developer_email", None),
                    "Developer Website": getattr(app.developer, "developer_website", None),
                    "Rating": app.rating,
                    "Rating Count": app.rating_count,
                    "Content Rating": app.content_rating,
                    "Installs": app.installs,
                    "Price": app.price,
                    "Size": app.size,
                    "Released": app.released,
                    "Last Updated": app.last_updated,
                }
                for app in apps
            ]
        }

    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@app.get("/max_price/")
def get_max_price(db: Session = Depends(get_db)):
    max_price = db.query(func.max(App.price)).scalar()
    return {"max_price": max_price}


@app.get("/categories/")
def get_categories(db: Session = Depends(get_db)):
    categories = db.query(Category).all()
    return {"categories": {category.category_name: category.category_id for category in categories}}


@app.get("/statistics/")
def get_statistics(category_id: int, year: int, db: Session = Depends(get_db)):
    start_time = time.perf_counter()

    apps = (
        db.query(App.last_updated, App.released)
        .filter(App.category_id == category_id)
        .filter(App.last_updated >= f"{year}-01-01", App.last_updated <= f"{year}-12-31")
        .filter(App.released >= f"{year}-01-01", App.released <= f"{year}-12-31")
        .all()
    )

    last_updated = [app.last_updated.strftime(
        "%Y-%m-%d") for app in apps if app.last_updated]
    released_time = [app.released.strftime(
        "%Y-%m-%d") for app in apps if app.released]

    ratings = db.query(App.rating).filter(App.category_id == category_id).all()
    ratings = [r[0] for r in ratings if r[0] is not None]
    rating_counts = dict(Counter(ratings))

    end_time = time.perf_counter()
    execution_time = end_time - start_time

    return {
        "last_updated": last_updated,
        "released_time": released_time,
        "rating_counts": rating_counts,
        "execution_time": execution_time
    }
