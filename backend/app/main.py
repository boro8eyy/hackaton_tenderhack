import io  # <--- И ЭТУ ТОЖЕ (если нет)
import json
import os
from typing import List, Optional

import pandas as pd  # <--- ДОБАВЬ ЭТУ СТРОКУ
from fastapi import Depends, FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import or_
from sqlalchemy.orm import Session

# Импортируем наши модули
from . import database, dependencies, models, schemas
from .auth import router as auth_router

# Создаем таблицы (в проде лучше миграции Alembic)
models.Base.metadata.create_all(bind=database.engine)

# Создаем админа через SQLAlchemy ORM
def create_default_admin():
    from passlib.context import CryptContext
    
    pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
    hashed_password = pwd_context.hash("admin1")
    
    db = database.SessionLocal()
    try:
        # Проверяем, есть ли уже админ
        admin = db.query(models.User).filter(models.User.username == "admin").first()
        if admin is None:
            admin = models.User(
                username="admin",
                hashed_password=hashed_password,
                is_admin=True
            )
            db.add(admin)
            db.commit()
            print("Default admin user created: admin / admin1")
    except Exception as e:
        print(f"Could not create admin: {e}")
        db.rollback()
    finally:
        db.close()

create_default_admin()

app = FastAPI(title="TenderHack API")

# CORS для фронтенда
# В продакшене добавьте реальный домен в ALLOWED_ORIGINS
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "").split(",") if os.getenv("ALLOWED_ORIGINS") else []
ALLOWED_ORIGINS.extend([
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://frontend:3000",
])

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 1. Подключаем роуты авторизации (/api/auth/login, /api/auth/register)
app.include_router(auth_router.router)


# --- 2. API: STE (Товары) ---

@app.post("/api/admin/ste/upload")
async def import_ste_file(
    file: UploadFile = File(...), 
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(dependencies.get_current_user)
):
    contents = await file.read()
    
    try:
        filename = file.filename.lower()
        if filename.endswith('.csv'):
            # Автоматическое определение разделителя (запятая или точка с запятой)
            df = pd.read_csv(io.BytesIO(contents), sep=None, engine='python', encoding='utf-8')
        elif filename.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(io.BytesIO(contents))
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading file: {str(e)}")

    # 1. Нормализация заголовков (убираем пробелы, lowercase)
    df.columns = df.columns.astype(str).str.strip().str.lower()

    # 2. Заменяем NaN на None
    df = df.where(pd.notnull(df), None)
    
    imported_count = 0
    updated_count = 0

    for index, row in df.iterrows():
        # Парсим характеристики
        chars_raw = row.get('характеристики')
        chars_json = {}
        
        if isinstance(chars_raw, str):
            try:
                # Разбираем "Ключ:Знач; Ключ2:Знач2"
                items = chars_raw.split(';')
                for item in items:
                    if ':' in item:
                        k, v = item.split(':', 1)
                        chars_json[k.strip()] = v.strip()
            except:
                chars_json = {"raw": chars_raw}
        
        # Безопасное получение ID категории (преобразуем в int, если это float 123.0)
        cat_id = row.get('id категории')
        if cat_id is not None:
            try:
                cat_id = int(float(cat_id))
            except:
                cat_id = None # Если там мусор, ставим None

        # Безопасное получение модели (всегда строка)
        model_val = row.get('модель')
        if model_val is not None:
            model_val = str(model_val).strip() # "3296" -> "3296"

        ste_data = {
            "external_id":       row.get('id сте'),
            "name":              row.get('название сте'),
            "image_url":         row.get('ссылка на картинку сте'),
            "model_name":        model_val,              # <--- Важно: строка
            "country_of_origin": row.get('страна происхождения'),
            "manufacturer":      row.get('производитель'),
            "category_id":       cat_id,                 # <--- Важно: int
            "category_name":     row.get('название категории'),
            "characteristics":   chars_json
        }
        
        if not ste_data["external_id"]:
            continue

        # UPSERT (Insert or Update)
        existing_ste = db.query(models.STE).filter(models.STE.external_id == ste_data["external_id"]).first()

        if existing_ste:
            for key, value in ste_data.items():
                setattr(existing_ste, key, value)
            updated_count += 1
        else:
            new_ste = models.STE(**ste_data)
            db.add(new_ste)
            imported_count += 1
            
    db.commit()
    
    return {
        "msg": "Import completed", 
        "created": imported_count, 
        "updated": updated_count
    }


@app.post("/api/admin/ste/upload")
async def import_ste_file(
    file: UploadFile = File(...), 
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(dependencies.get_current_user)
):
    """
    Импорт CSV или Excel файла с данными о STE.
    Колонки: 'id сте', 'название сте', 'ссылка на картинку сте', 
    'модель', 'страна происхождения', 'производитель', 
    'id категории', 'название категории', 'характеристики'
    """
    contents = await file.read()
    
    # 1. Читаем файл в DataFrame
    try:
        if file.filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(contents))
        elif file.filename.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(io.BytesIO(contents))
        else:
            raise HTTPException(status_code=400, detail="Unsupported file format. Use CSV or Excel.")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading file: {str(e)}")

    # 2. Обработка данных (замена NaN на None для SQL)
    df = df.where(pd.notnull(df), None)
    
    imported_count = 0
    updated_count = 0

    # 3. Проходимся по строкам
    for index, row in df.iterrows():
        # Парсим характеристики (если это строка "ключ:знач; ключ:знач")
        # В твоем файле они разделены точкой с запятой
        chars_raw = row.get('характеристики')
        chars_json = {}
        if isinstance(chars_raw, str):
            # Пример: "Ширина:20; Высота:10" -> {"Ширина": "20", "Высота": "10"}
            try:
                items = chars_raw.split(';')
                for item in items:
                    if ':' in item:
                        k, v = item.split(':', 1)
                        chars_json[k.strip()] = v.strip()
            except:
                chars_json = {"raw": chars_raw}

        ste_data = {
            "external_id": row.get('id сте'),
            "name": row.get('название сте'),
            "image_url": row.get('ссылка на картинку сте'),
            "model_name": row.get('модель'),
            "country_of_origin": row.get('страна происхождения'),
            "manufacturer": row.get('производитель'),
            "category_id": row.get('id категории'),
            "category_name": row.get('название категории'),
            "characteristics": chars_json
        }
        
        # Проверяем, есть ли уже такой товар (по external_id)
        existing_ste = None
        if ste_data["external_id"]:
             existing_ste = db.query(models.STE).filter(models.STE.external_id == ste_data["external_id"]).first()

        if existing_ste:
            # Обновляем поля
            for key, value in ste_data.items():
                setattr(existing_ste, key, value)
            updated_count += 1
        else:
            # Создаем новый
            new_ste = models.STE(**ste_data)
            db.add(new_ste)
            imported_count += 1
            
    db.commit()
    
    return {
        "msg": "Import completed", 
        "created": imported_count, 
        "updated": updated_count
    }

@app.get("/api/admin/ste", response_model=List[schemas.STEResponse])
def get_stes(
    q: Optional[str] = None,  # Поиск по query
    category_id: Optional[int] = None,  # Фильтр по категории
    fuzzy: bool = True,  # Использовать fuzzy search
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(dependencies.get_current_user)
):
    """Получить список STE с поиском, фильтрацией по категории и пагинацией."""
    from . import fuzzy_search
    
    query = db.query(models.STE)
    
    # Фильтр по категории (применяется всегда)
    if category_id:
        query = query.filter(models.STE.category_id == category_id)
    
    if q:
        if fuzzy:
            # Fuzzy search: сначала получаем все записи, затем фильтруем
            all_stes = query.all()
            ste_data = [
                {
                    'id': ste.id,
                    'name': ste.name,
                    'model_name': ste.model_name,
                    'manufacturer': ste.manufacturer
                }
                for ste in all_stes
            ]
            matching_ids = fuzzy_search.get_fuzzy_matches_for_ste(q, ste_data, threshold=50)
            
            if not matching_ids:
                return []
            
            # Получаем STE в порядке релевантности
            id_to_ste = {ste.id: ste for ste in all_stes}
            result = [id_to_ste[id] for id in matching_ids if id in id_to_ste]
            return result[skip:skip + limit]
        else:
            # Обычный ILIKE поиск
            query = query.filter(
                or_(
                    models.STE.name.ilike(f"%{q}%"),
                    models.STE.model_name.ilike(f"%{q}%"),
                    models.STE.manufacturer.ilike(f"%{q}%")
                )
            )
    
    return query.offset(skip).limit(limit).all()

@app.post("/api/admin/ste", response_model=schemas.STEResponse)
def create_ste(
    ste: schemas.STECreate, 
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(dependencies.get_current_user)
):
    """Создать новый STE."""
    db_ste = models.STE(**ste.model_dump())
    db.add(db_ste)
    db.commit()
    db.refresh(db_ste)
    return db_ste

@app.get("/api/admin/ste/{id}", response_model=schemas.STEResponse)
def get_ste_detail(
    id: int, 
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(dependencies.get_current_user)
):
    """Получить STE по ID."""
    ste = db.query(models.STE).filter(models.STE.id == id).first()
    if not ste:
        raise HTTPException(status_code=404, detail="STE not found")
    return ste

@app.patch("/api/admin/ste/{id}", response_model=schemas.STEResponse)
def update_ste(
    id: int, 
    ste_update: schemas.STEUpdate, 
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(dependencies.get_current_user)
):
    """Обновить STE (PATCH)."""
    db_ste = db.query(models.STE).filter(models.STE.id == id).first()
    if not db_ste:
        raise HTTPException(status_code=404, detail="STE not found")
    
    update_data = ste_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_ste, key, value)
    
    db.commit()
    db.refresh(db_ste)
    return db_ste

@app.delete("/api/admin/ste/{id}")
def delete_ste(
    id: int, 
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(dependencies.get_current_user)
):
    """Удалить STE."""
    db_ste = db.query(models.STE).filter(models.STE.id == id).first()
    if not db_ste:
        raise HTTPException(status_code=404, detail="STE not found")
    db.delete(db_ste)
    db.commit()
    return {"msg": "Deleted"}

@app.post("/api/admin/ste/upload-json")
async def upload_stes(
    file: UploadFile = File(...), 
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(dependencies.get_current_user)
):
    """Загрузка JSON файла с STE (массовое создание)."""
    content = await file.read()
    try:
        data = json.loads(content)
        if not isinstance(data, list):
            data = [data]
            
        created_count = 0
        for item in data:
            ste = models.STE(
                name=item.get("name", "No Name"),
                description=item.get("description", ""),
                category_id=item.get("category_id", 0),
                characteristics=item.get("characteristics", {})
            )
            db.add(ste)
            created_count += 1
        
        db.commit()
        return {"msg": f"Successfully uploaded {created_count} STEs"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid file format: {str(e)}")


# --- 3. API: Cards (Группы/Агрегации) ---

@app.get("/api/admin/card/", response_model=List[schemas.CardResponse])
def get_cards(
    q: Optional[str] = None,
    category_id: Optional[int] = None,  # Фильтр по категории (через STE)
    fuzzy: bool = True,  # Использовать fuzzy search
    skip: int = 0, 
    limit: int = 50, 
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(dependencies.get_current_user)
):
    """Список карт с поиском и фильтрацией по категории."""
    from . import fuzzy_search
    
    query = db.query(models.Card)
    
    if category_id:
        # Фильтруем карточки, у которых есть STE с указанной категорией
        query = query.join(models.STE).filter(models.STE.category_id == category_id).distinct()
    
    if q:
        if fuzzy:
            # Fuzzy search по названию карты
            all_cards = query.all()
            card_names = [card.name or '' for card in all_cards]
            
            matches = fuzzy_search.fuzzy_match(q, card_names, threshold=50, limit=len(card_names))
            
            if not matches:
                return []
            
            # Сортируем по релевантности
            matching_indices = [index for _, _, index in matches]
            result = [all_cards[i] for i in matching_indices]
            return result[skip:skip + limit]
        else:
            query = query.filter(models.Card.name.ilike(f"%{q}%"))
    
    return query.offset(skip).limit(limit).all()

@app.post("/api/admin/card/", response_model=schemas.CardResponse)
def create_card(
    card: schemas.CardCreate, 
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(dependencies.get_current_user)
):
    """Создать карту вручную."""
    # Extract ste_ids from the payload and create card with remaining fields
    payload = card.model_dump()
    ste_ids = payload.pop("ste_ids", []) or []

    db_card = models.Card(**payload)
    db.add(db_card)
    db.commit()
    db.refresh(db_card)

    # Attach provided STEs to the created card
    if ste_ids:
        stes = db.query(models.STE).filter(models.STE.id.in_(ste_ids)).all()
        for ste in stes:
            ste.card_id = db_card.id
        db.commit()
        db.refresh(db_card)

    return db_card

@app.get("/api/admin/card/{id}", response_model=schemas.CardResponse)
def get_card_detail(
    id: int, 
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(dependencies.get_current_user)
):
    """Детальная инфо о карте."""
    card = db.query(models.Card).filter(models.Card.id == id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Card not found")
    return card

@app.patch("/api/admin/card/{id}", response_model=schemas.CardResponse)
def update_card(
    id: int, 
    card_update: schemas.CardUpdate, 
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(dependencies.get_current_user)
):
    """Обновить карту (PATCH)."""
    db_card = db.query(models.Card).filter(models.Card.id == id).first()
    if not db_card:
        raise HTTPException(status_code=404, detail="Card not found")
    
    update_data = card_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_card, key, value)
    
    db.commit()
    db.refresh(db_card)
    return db_card

@app.delete("/api/admin/card/{id}")
def delete_card(
    id: int, 
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(dependencies.get_current_user)
):
    """Удалить карту."""
    db_card = db.query(models.Card).filter(models.Card.id == id).first()
    if not db_card:
        raise HTTPException(status_code=404, detail="Card not found")
    
    # Отвязываем STE перед удалением
    for ste in db_card.stes:
        ste.card_id = None
    
    db.delete(db_card)
    db.commit()
    return {"msg": "Deleted"}


# --- 4. API: Search & Aggregation (Публичные и ML) ---

@app.get("/api/search", response_model=schemas.PaginatedSTEResponse)
def search_public(
    query: str,
    exact: bool = False,
    fuzzy: bool = True,  # Использовать fuzzy search (игнорируется если exact=True)
    page: int = 1,
    per_page: int = 10,
    category_id: Optional[int] = None,
    db: Session = Depends(database.get_db)
):
    """Публичный поиск STE по query с пагинацией. exact=true для точного поиска, fuzzy=true для нечёткого."""
    from . import fuzzy_search

    # Базовый запрос
    base_query = db.query(models.STE)
    
    # Фильтр по категории
    if category_id is not None:
        base_query = base_query.filter(models.STE.category_id == category_id)
    
    # Фильтр по поисковому запросу
    if exact:
        # Точный поиск - ищем точное совпадение
        base_query = base_query.filter(
            or_(
                models.STE.name == query,
                models.STE.model_name == query,
                models.STE.manufacturer == query
            )
        )
        total = base_query.count()
        offset = (page - 1) * per_page
        items = base_query.offset(offset).limit(per_page).all()
    elif fuzzy:
        # Fuzzy search
        all_stes = base_query.all()
        ste_data = [
            {
                'id': ste.id,
                'name': ste.name,
                'model_name': ste.model_name,
                'manufacturer': ste.manufacturer
            }
            for ste in all_stes
        ]
        matching_ids = fuzzy_search.get_fuzzy_matches_for_ste(query, ste_data, threshold=40)
        
        total = len(matching_ids)
        offset = (page - 1) * per_page
        page_ids = matching_ids[offset:offset + per_page]
        
        # Получаем STE в порядке релевантности
        id_to_ste = {ste.id: ste for ste in all_stes}
        items = [id_to_ste[id] for id in page_ids if id in id_to_ste]
    else:
        # Обычный поиск - частичное совпадение (ILIKE)
        base_query = base_query.filter(
            or_(
                models.STE.name.ilike(f"%{query}%"),
                models.STE.model_name.ilike(f"%{query}%"),
                models.STE.manufacturer.ilike(f"%{query}%")
            )
        )
        total = base_query.count()
        offset = (page - 1) * per_page
        items = base_query.offset(offset).limit(per_page).all()
    
    # Вычисляем общее количество страниц
    total_pages = (total + per_page - 1) // per_page if total > 0 else 1
    
    return {
        "items": items,
        "total": total,
        "page": page,
        "per_page": per_page,
        "total_pages": total_pages
    }

@app.get("/api/card/{card_id}/{ste_id}", response_model=schemas.STEResponse)
def get_card_ste_relation(
    card_id: int, 
    ste_id: int, 
    db: Session = Depends(database.get_db)
):
    """Проверка связи между картой и STE. Возвращает данные STE, если он привязан к карте."""
    ste = db.query(models.STE).filter(models.STE.id == ste_id, models.STE.card_id == card_id).first()
    if not ste:
        raise HTTPException(status_code=404, detail="Relation not found")
    return ste

@app.get("/api/categories", response_model=List[schemas.CategoryResponse])
def get_categories(
    db: Session = Depends(database.get_db)
):
    """
    Получить список всех категорий (id + name).
    Поскольку в проекте нет отдельной таблицы категорий, берём уникальные пары
    `category_id` и `category_name` из таблицы `stes`.
    """
    rows = db.query(models.STE.category_id, models.STE.category_name).distinct().all()
    result = []
    for cid, cname in rows:
        if cid is None:
            continue
        result.append({"id": cid, "name": cname or str(cid)})
    return result


# --- 5. API: Ratings / Feedback (Новый блок) ---

@app.post("/api/rating", response_model=schemas.FeedbackResponse)
def rate_aggregation(
    feedback: schemas.FeedbackCreate,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(dependencies.get_current_user)
):
    """
    Оценить качество агрегации (связь Карты и STE).
    score: 1 (Correct), 0 (Incorrect).
    Эти данные будут использованы для переобучения ML.
    """
    # 1. Валидация: существуют ли такие ID
    card = db.query(models.Card).filter(models.Card.id == feedback.card_id).first()
    ste = db.query(models.STE).filter(models.STE.id == feedback.ste_id).first()
    
    if not card or not ste:
        raise HTTPException(status_code=404, detail="Card or STE not found")
        
    if feedback.score not in [0, 1]:
        raise HTTPException(status_code=400, detail="Score must be 0 or 1")

    # 2. Проверяем, не голосовал ли уже этот юзер за эту пару (чтобы избежать дублей)
    # Если нужно разрешить переголосовывать - можно убрать этот блок или делать update
    existing_vote = db.query(models.Feedback).filter(
        models.Feedback.card_id == feedback.card_id,
        models.Feedback.ste_id == feedback.ste_id,
        models.Feedback.user_id == current_user.id
    ).first()

    if existing_vote:
        # Обновляем существующую оценку
        existing_vote.score = feedback.score
        db.commit()
        db.refresh(existing_vote)
        return existing_vote

    # 3. Создаем новую запись фидбека
    new_feedback = models.Feedback(
        card_id=feedback.card_id,
        ste_id=feedback.ste_id,
        score=feedback.score,
        user_id=current_user.id
    )
    db.add(new_feedback)
    db.commit()
    db.refresh(new_feedback)
    
    return new_feedback

@app.get("/api/rating/history")
def get_rating_history(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(dependencies.get_current_user)
):
    """Получить все оценки (для ML датасета)."""
    return db.query(models.Feedback).all()


# --- 6. API: Reaggregate (ML Pipeline) ---

@app.post("/api/admin/reaggregate", response_model=schemas.ReaggregateResponse)
def reaggregate_stes(
    request: schemas.ReaggregateRequest,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(dependencies.get_current_user)
):
    """
    Запустить ML кластеризацию для указанных STE.
    Переагрегирует товары и обновляет их card_id.
    """
    from . import ml_insert
    
    if not request.ste_ids:
        raise HTTPException(status_code=400, detail="ste_ids cannot be empty")
    
    result = ml_insert.run_ml_pipeline(db, request.ste_ids)
    
    return result


@app.post("/api/admin/reaggregate/all", response_model=schemas.ReaggregateResponse)
def reaggregate_all_stes(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(dependencies.get_current_user)
):
    """
    Запустить ML кластеризацию для всех STE.
    """
    from . import ml_insert
    
    result = ml_insert.run_ml_pipeline(db)
    
    return result