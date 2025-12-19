from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, JSON, Float, Text, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship, object_session
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import select
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    # Связь к фидбекам, чтобы можно было получить все оценки от пользователя
    feedbacks = relationship("Feedback", back_populates="user")

class STE(Base):
    __tablename__ = "stes"
    id = Column(Integer, primary_key=True, index=True)
    
    # Поля, которые уже были
    name = Column(String, index=True) # 'название сте'
    category_id = Column(Integer, index=True) # 'id категории'
    characteristics = Column(JSON, default={}) # 'характеристики' (парсим строку или сохраняем как есть)
    
    # НОВЫЕ ПОЛЯ ИЗ EXCEL
    external_id = Column(Integer, unique=True, nullable=True) # 'id сте' (уникальный на портале)
    image_url = Column(String, nullable=True) # 'ссылка на картинку сте'
    model_name = Column(String, nullable=True) # 'модель'
    country_of_origin = Column(String, nullable=True) # 'страна происхождения'
    manufacturer = Column(String, nullable=True) # 'производитель'
    category_name = Column(String, nullable=True) # 'название категории'
    
    card_id = Column(Integer, ForeignKey("cards.id"), nullable=True)
    card = relationship("Card", back_populates="stes")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Card(Base):
    __tablename__ = "cards"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=True)
    stes = relationship("STE", back_populates="card")

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    @hybrid_property
    def score(self):
        """Average feedback score for this card (0.0 - 1.0). Returns 0.0 if no feedbacks."""
        sess = object_session(self)
        if sess is None:
            return 0.0
        avg = sess.query(func.avg(Feedback.score)).filter(Feedback.card_id == self.id).scalar()
        return float(avg) if avg is not None else 0.0

    @score.expression
    def score(cls):
        return select(func.avg(Feedback.score)).where(Feedback.card_id == cls.id).scalar_subquery()

from sqlalchemy import CheckConstraint

class Feedback(Base):
    __tablename__ = "feedbacks"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Какую группу оцениваем
    card_id = Column(Integer, ForeignKey("cards.id"))
    
    # Какой товар внутри этой группы оцениваем
    ste_id = Column(Integer, ForeignKey("stes.id"))
    
    # 1 = Хорошо (правильно сгруппировано), 0 = Плохо (ошибка агрегации)
    score = Column(Integer, CheckConstraint('score IN (0, 1)'), nullable=False)
    
    # Кто оценил (полезно для ML, чтобы фильтровать надежных разметчиков)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Связи (опционально, для удобства ORM)
    card = relationship("Card")
    ste = relationship("STE")
    user = relationship("User", back_populates="feedbacks")