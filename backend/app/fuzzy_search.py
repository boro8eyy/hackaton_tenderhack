"""
Fuzzy search utilities для нечёткого поиска.
Использует rapidfuzz для быстрого fuzzy matching.
"""
from typing import List, Optional, Tuple

from rapidfuzz import fuzz, process


def fuzzy_match(query: str, candidates: List[str], threshold: int = 60, limit: int = 100) -> List[Tuple[str, int, int]]:
    """
    Выполняет fuzzy matching запроса против списка кандидатов.
    
    Args:
        query: Поисковый запрос
        candidates: Список строк для поиска
        threshold: Минимальный score для включения в результаты (0-100)
        limit: Максимальное количество результатов
    
    Returns:
        Список кортежей (match, score, index)
    """
    if not query or not candidates:
        return []
    
    # Используем token_set_ratio для лучшего matching слов в разном порядке
    results = process.extract(
        query, 
        candidates, 
        scorer=fuzz.token_set_ratio,
        limit=limit,
        score_cutoff=threshold
    )
    
    return results


def get_fuzzy_matches_for_ste(
    query: str, 
    ste_data: List[dict],
    threshold: int = 50
) -> List[int]:
    """
    Находит ID STE, которые fuzzy-match запросу.
    
    Args:
        query: Поисковый запрос
        ste_data: Список словарей с полями id, name, model_name, manufacturer
        threshold: Минимальный score
    
    Returns:
        Список ID STE, отсортированных по релевантности
    """
    if not query or not ste_data:
        return []
    
    # Создаём комбинированные строки для поиска
    search_strings = []
    id_map = {}
    
    for i, ste in enumerate(ste_data):
        # Комбинируем все поля для поиска
        parts = [
            str(ste.get('name') or ''),
            str(ste.get('model_name') or ''),
            str(ste.get('manufacturer') or '')
        ]
        combined = ' '.join(filter(None, parts))
        search_strings.append(combined)
        id_map[i] = ste['id']
    
    # Выполняем fuzzy matching
    matches = fuzzy_match(query, search_strings, threshold=threshold, limit=len(search_strings))
    
    # Возвращаем ID в порядке убывания score
    result_ids = []
    for match, score, index in matches:
        result_ids.append(id_map[index])
    
    return result_ids


def calculate_similarity(s1: str, s2: str) -> int:
    """
    Вычисляет similarity score между двумя строками (0-100).
    """
    if not s1 or not s2:
        return 0
    return fuzz.token_set_ratio(s1.lower(), s2.lower())
