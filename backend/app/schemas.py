from typing import Any, Dict, List, Optional

from pydantic import BaseModel


# --- Auth ---
class UserCreate(BaseModel):
    login: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

# --- STE ---
class STEBase(BaseModel):
    name: str
    category_id: Optional[int] = None
    characteristics: Dict[str, Any] = {}

class STECreate(STEBase):
    pass

class STEUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    characteristics: Optional[Dict[str, Any]] = None
    card_id: Optional[int] = None

class STEResponse(STEBase):
    id: int
    card_id: Optional[int] = None
    # Extended fields from import
    external_id: Optional[int] = None
    image_url: Optional[str] = None
    model_name: Optional[str] = None
    country_of_origin: Optional[str] = None
    manufacturer: Optional[str] = None
    category_name: Optional[str] = None
    class Config:
        from_attributes = True

# --- Card ---
class CardBase(BaseModel):
    name: Optional[str] = None

class CardCreate(CardBase):
    ste_ids: Optional[List[int]] = []

class CardUpdate(BaseModel):
    name: Optional[str] = None

class CardResponse(CardBase):
    id: int
    stes: List[STEResponse] = []
    class Config:
        from_attributes = True

# --- Aggregation Request ---
class CategoryResponse(BaseModel):
    id: int
    name: Optional[str] = None
    class Config:
        from_attributes = True


# --- Paginated Response ---
class PaginatedSTEResponse(BaseModel):
    items: List[STEResponse]
    total: int
    page: int
    per_page: int
    total_pages: int
    class Config:
        from_attributes = True


class FeedbackCreate(BaseModel):
    card_id: int
    ste_id: int
    score: int # Ожидаем 0 или 1

class FeedbackResponse(FeedbackCreate):
    id: int
    user_id: Optional[int] = None
    class Config:
        from_attributes = True


# --- Reaggregate ---
class ReaggregateRequest(BaseModel):
    ste_ids: List[int]  # Список ID STE для реагрегации

class ReaggregateResponse(BaseModel):
    status: str
    total: int = 0
    updated: int = 0
    error: Optional[str] = None