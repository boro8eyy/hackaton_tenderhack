# TenderHack - Product Aggregation System

Система агрегации товаров с ML-кластеризацией.

## Технологии

- **Backend**: FastAPI, SQLAlchemy, PostgreSQL
- **Frontend**: SvelteKit 5, TypeScript
- **ML**: Sentence Transformers, HDBSCAN
- **Infrastructure**: Docker, Docker Compose

## Быстрый старт (Development)

```bash
# Клонировать репозиторий
git clone <repo-url>
cd tenderhack-201

# Запустить в режиме разработки
docker-compose up --build
```

Приложение будет доступно:

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

**Логин по умолчанию**: `admin` / `admin1`

## Production Деплой

### 1. Подготовка

```bash
# Создать .env файл из примера
cp .env.example .env

# Отредактировать .env - ОБЯЗАТЕЛЬНО изменить:
# - POSTGRES_PASSWORD
# - SECRET_KEY
# - VITE_API_URL (ваш домен)
# - ALLOWED_ORIGINS (ваш домен)
```

### 2. Запуск

```bash
# Сборка и запуск production
docker-compose -f docker-compose.prod.yml up --build -d

# Просмотр логов
docker-compose -f docker-compose.prod.yml logs -f
```

### 3. Остановка

```bash
docker-compose -f docker-compose.prod.yml down
```

## Переменные окружения

| Переменная          | Описание                     | По умолчанию                          |
| ------------------- | ---------------------------- | ------------------------------------- |
| `POSTGRES_USER`     | Пользователь БД              | postgres                              |
| `POSTGRES_PASSWORD` | Пароль БД                    | postgres                              |
| `POSTGRES_DB`       | Имя БД                       | tenderhack                            |
| `SECRET_KEY`        | JWT секрет                   | -                                     |
| `EMBEDDING_MODEL`   | ML модель                    | paraphrase-multilingual-MiniLM-L12-v2 |
| `VITE_API_URL`      | URL бэкенда для фронтенда    | http://localhost:8000                 |
| `ALLOWED_ORIGINS`   | CORS origins (через запятую) | -                                     |

## API Endpoints

### Авторизация

- `POST /api/auth/login` - Вход
- `POST /api/auth/register` - Регистрация

### STE (Товары)

- `GET /api/admin/ste` - Список товаров
- `POST /api/admin/ste` - Создать товар
- `PUT /api/admin/ste/{id}` - Обновить товар
- `DELETE /api/admin/ste/{id}` - Удалить товар

### Карточки (Агрегированные товары)

- `GET /api/admin/card/` - Список карточек
- `GET /api/admin/card/{id}` - Карточка с товарами

### ML Агрегация

- `POST /api/admin/reaggregate` - Реагрегация выбранных STE
- `POST /api/admin/reaggregate/all` - Реагрегация всех STE

### Поиск

- `GET /api/search` - Поиск товаров

## Структура проекта

```
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI приложение
│   │   ├── models.py        # SQLAlchemy модели
│   │   ├── schemas.py       # Pydantic схемы
│   │   ├── ml_insert.py     # ML кластеризация
│   │   └── fuzzy_search.py  # Fuzzy поиск
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── lib/             # Компоненты и утилиты
│   │   └── routes/          # Страницы
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml       # Development
└── docker-compose.prod.yml  # Production
```

## Troubleshooting

### Модель не загружается (timeout)

ML модель скачивается при первой сборке образа. Если сборка прерывается:

```bash
# Пересобрать с чистого листа
docker-compose build --no-cache backend
```

### Ошибка подключения к БД

```bash
# Проверить статус БД
docker-compose ps db

# Посмотреть логи БД
docker-compose logs db
```

## License

MIT
