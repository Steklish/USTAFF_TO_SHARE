# USTAFF THE AI

### `Dockerfile ( ˇ෴ˇ )`
```
FROM python:3.12
WORKDIR /app
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "main.py"]
```

Для теста локально `docker run -p 5000:5000 ustaff-img`


Сервер на `Flask` на `5000` порте

Бот на `ChromaDB` (вшита в контейнер пока) + `Gemini 2.0 flash`

Есть `RAG` на документах про банки

Хост [`Railway.com`](https://railway.com/)

- В проекте есть файл для добавления документов, но он не используется вебкой. 
- БД на гитхаб не загрузить, оказывается.
- Работает на бесплатныз API т к триал на 300 bucks не дает норм доступа anyway.
- `main.py` - сервер
- `/src` - тут классы с логикой
---
## Процесс обучения
- поддерживаемые форматы:
    - любые текстовые файлы (`.py`, `.txt`, `.csv`, `.md`)
    - `.pdf` документы
- принцип кодирования данных:
    - файл переводится в текст и разбивается на чанки
    - чанки состоят из 120 слов, где первые и последние 10 слов являются последними или первыми в соседних чанках соответственно
    - каждый чанк векторизуется с помощью `text-multilingual-embedding-002`
    - чанк + метаданные + вектор отправляется в БД
- принцип получения данных:
    - запрос переводится в вектор
    - вектор отправляктся в БД
    - Получаем объекты с данными
- для дообучения необходимо:
    - поместить интересующие файлы в `/data` 
    - выполнить код из файла `src/put_data.py` (для запуска использовать `python -m src.put_data`)
    - дождаться завершения процесса


### Алгоритм работы агента:
- Получение запроса
- Обработка оного и извлечение **смысла** _(с учетом истории переписки)_
- Все, что после этого осталось, используется как запрос в векторную БД `ChromaDB`.
- Из БД возвращаются `n = 5` чанков документов с наименьшей **дистанцией** с указанием источников
- Полученные результаты проверяются на предмет релевантности (с помощью LLM)
- Отправка финального запроса в LLM, который состоит из:
    - истории сообщений
    - данных из БД
    - оценки **намерения** пользователя из второго шага
    - Изначального запроса пользовалеля 
- Предоставления вывода пользователю с возможностью просмотреть даныне, полученные из БД в процессе обработки

# [`Ссылочка на Юстафа`](https://ustaff-img-production.up.railway.app/)

### Инструкция для Деда
- `docker build -t ustaff-img .` -> _[Successfully tagged ustaff-img:latest]_
- `docker tag ustaff-img steklish/ustaff-img:latest`
- `docker login`
- `docker push steklish/ustaff-img:latest`
- готово

### Инструкция нормальная
- Сборка контейнера (команда) `docker build -t ustaff-img .`
- Запуск контейнера локально `docker run -p 5000:5000 ustaff-img`
__Важный момент__ _мы тут в центре Европы забанены к чертям (локально только с VPN)_ 