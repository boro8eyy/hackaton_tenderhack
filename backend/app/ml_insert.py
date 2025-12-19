import logging
import os
from typing import List, Optional

import hdbscan
import pandas as pd
from sentence_transformers import SentenceTransformer
from sqlalchemy import update
from sqlalchemy.orm import Session

from . import models

logger = logging.getLogger(__name__)

# Название модели (можно менять через env)
MODEL_NAME = os.getenv('EMBEDDING_MODEL', 'paraphrase-multilingual-MiniLM-L12-v2')

# Кешируем модель, чтобы не загружать при каждом запросе
_model_cache = None
_model_load_error = None


def get_embedding_model() -> SentenceTransformer:
    """Ленивая загрузка и кеширование модели."""
    global _model_cache, _model_load_error
    
    # Сбрасываем ошибку, чтобы можно было повторить попытку
    if _model_cache is not None:
        return _model_cache
    
    try:
        logger.info(f"Loading embedding model: {MODEL_NAME}")
        logger.info(f"HF_HOME: {os.getenv('HF_HOME', 'not set')}")
        
        # Пробуем загрузить модель (из кэша или скачать)
        _model_cache = SentenceTransformer(MODEL_NAME)
        logger.info("Embedding model loaded successfully")
        return _model_cache
        
    except Exception as e:
        error_msg = f"Failed to load embedding model '{MODEL_NAME}': {e}"
        logger.error(error_msg)
        raise RuntimeError(error_msg)


def preload_model():
    """Предзагрузка модели при старте (вызывается из main.py)."""
    try:
        get_embedding_model()
        return True
    except Exception as e:
        logger.warning(f"Model preload failed (will retry on first use): {e}")
        return False


def get_all_stes_from_db(db: Session, ste_ids: List[int] = None) -> pd.DataFrame:
    """Оптимизированное получение данных из БД."""
    # Базовый запрос
    query = db.query(
        models.STE.id,
        models.STE.card_id,
        models.STE.name,
        models.STE.characteristics
    )
    
    # Фильтруем по ID, если указаны
    if ste_ids:
        query = query.filter(models.STE.id.in_(ste_ids))
    
    result = query.all()
    
    if not result:
        return pd.DataFrame(columns=['id', 'card_id', 'title', 'features'])
    
    # Создаем DataFrame напрямую из результата
    df = pd.DataFrame(result, columns=['id', 'card_id', 'title', 'features'])
    df['card_id'] = df['card_id'].fillna(0).astype(int)
    df['features'] = df['features'].apply(lambda x: x or {})
    
    return df


def run_ml_clustering(left_df: pd.DataFrame) -> pd.DataFrame:
    """Кластеризация с использованием кешированной модели."""
    if left_df.empty:
        return pd.DataFrame(columns=['id', 'title', 'features', 'cluster_id'])
    
    titles = left_df['title'].fillna('').tolist()
    
    # Используем кешированную модель
    model = get_embedding_model()
    embeddings = model.encode(titles, show_progress_bar=False, batch_size=64)
    
    clusterer = hdbscan.HDBSCAN(min_cluster_size=2, min_samples=1)
    labels = clusterer.fit_predict(embeddings)
    
    df = left_df[['id', 'title', 'features']].copy()
    df['cluster_id'] = labels
    
    return df


def merge_cluster_to_card(left_df: pd.DataFrame, right_df: pd.DataFrame) -> pd.DataFrame:
    """Объединение результатов кластеризации."""
    if right_df.empty:
        return left_df
    
    # Делаем left join по id
    merged_df = left_df.merge(
        right_df[['id', 'cluster_id']], 
        on='id', 
        how='left'
    )
    
    # Где cluster_id = -1 (шум), ставим 0
    merged_df['cluster_id'] = merged_df['cluster_id'].replace(-1, 0)
    
    # Обновляем card_id значениями из cluster_id
    merged_df['card_id'] = merged_df['cluster_id'].fillna(merged_df['card_id']).astype(int)
    
    merged_df = merged_df.drop(columns=['cluster_id'])
    
    return merged_df


def update_stes_in_db(db: Session, merged_df: pd.DataFrame, ste_ids: List[int] = None) -> int:
    """Оптимизированное batch-обновление БД."""
    if merged_df.empty:
        return 0
    
    # Получаем текущие card_id из БД одним запросом
    query = db.query(models.STE.id, models.STE.card_id)
    if ste_ids:
        query = query.filter(models.STE.id.in_(ste_ids))
    
    current_data = query.all()
    current_map = {row.id: row.card_id for row in current_data}
    
    # Находим только измененные записи
    updates = []
    for _, row in merged_df.iterrows():
        ste_id = int(row['id'])
        new_card_id = int(row['card_id']) if row['card_id'] != 0 else None
        
        if current_map.get(ste_id) != new_card_id:
            updates.append({'id': ste_id, 'card_id': new_card_id})
    
    if not updates:
        return 0
    
    # Batch update через executemany (значительно быстрее)
    for batch_start in range(0, len(updates), 500):
        batch = updates[batch_start:batch_start + 500]
        for item in batch:
            db.query(models.STE).filter(models.STE.id == item['id']).update(
                {'card_id': item['card_id']}, 
                synchronize_session=False
            )
    
    db.commit()
    return len(updates)


def run_ml_pipeline(db: Session, ste_ids: List[int] = None) -> dict:
    """
    Запуск ML пайплайна.
    
    Args:
        db: Сессия базы данных
        ste_ids: Список ID STE для обработки. Если None, обрабатываются все.
    
    Returns:
        Словарь с результатами
    """
    left_df = get_all_stes_from_db(db, ste_ids)
    
    if left_df.empty:
        return {"status": "no_data", "total": 0, "updated": 0}
    
    try:
        right_df = run_ml_clustering(left_df)
    except RuntimeError as e:
        logger.error(f"ML clustering failed: {e}")
        return {"status": "error", "total": len(left_df), "updated": 0, "error": str(e)}
    
    merged_df = merge_cluster_to_card(left_df, right_df)
    
    updated_count = update_stes_in_db(db, merged_df, ste_ids)
    
    return {"status": "success", "total": len(left_df), "updated": updated_count}