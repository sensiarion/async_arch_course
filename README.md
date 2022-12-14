## Backend API для курса по асинхронной архитектуре

- language: python 3.10
- api: fastapi
- database: sqlalchemy ORM with postgres db (asyncpg)
- validation: pydantic
- queues: aiokafka, aio-pika

# Конфигурирование

Перед запуском, необходимо указать переменные среды из файла `.env.example` в файл `.env`. Сам файл как и
пример должен находится в корне проекта.

# Запуск

Самый простой вариант запуска – `docker-compose` (`docker compose` для docker 20+). Перед этим, само собой,
необходимо установить docker на сервер/рабочую станцию. Официальный мануал очень даже подробно рассказывает
шаги для установки https://docs.docker.com/engine/install/

1. Выставляем все переменные из пункта конфигурирования
2. запускаем весь backend вместе с БД через команду `docker-compose up -d```
3. ?????
4. PROFIT

# Начало работы

Для ознакомления с функционалом API можно перейти по uri `/docs` на котором располагается интерактивная
документация swagger. Также есть альтернативный вариант документации на `/redoc`

### TODO list

- [ ] сделать restricted реализацию круда для разграничения доступа
- [x] поддержка файлов
- [ ] индексы на основные нагруженные таблицы бд
- [ ] сортировки и фильтрация
- [ ] привязка (доступ к конкретному аккаунту при выставлении позиции/сделки)
- [ ] реализация плеча в расчётах

