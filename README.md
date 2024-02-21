# Сайт для публикации рецептов

### Описание

Сайт, на котором пользователи могут обмениваться рецептами друг с другом.
Целью проекта является применение всех изученных технологий в одном проекте,
чтобы закрепить их взаимодействие друг с другом.

Ссылка: https://tordvist-foodgram.ddns.net/

#### Возможности проекта:
- Регистрация и авторизация пользователей
- Добавление/редактирование/удаление рецептов
- Возможность прикрепить фотографию к рецепту
- Добавление рецепта в избранное
- Добавление рецепта в список покупок и скачивание его в формате .pdf
- Возможность подписаться на других пользователей
- Фильтрация рецептов по различным критериям
- Поиск ингредиентов по названию

### Как запустить проект
#### На сервере локальной разработки:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone git@github.com:olkrpv/foodgram_project_react.git
```

```
cd foodgram_project_react
```

Cоздать виртуальное окружение:

```
python3.9 -m venv venv
```

Активировать виртуальное окружение:
```
source venv/bin/activate
```

Обновить pip:

```
python3 -m pip install --upgrade pip
```

Установить зависимости из файла requirements.txt:

```
cd backend/
```

```
pip install -r requirements.txt
```

Перейти в папку с Django-проектом:

```
cd foodgram/
```

Выполнить миграции:

```
python3 manage.py migrate
```

Запустить проект:

```
python3 manage.py runserver
```

Загрузить данные из файла csv:

```
python3 manage.py importcsv ingredients.csv
```

### Локальный запуск в контейнерах

Для начала установите Docker на ваш компьютер (или проверьте, что он уже установлен).

Далее нужно клонировать репозиторий:

```
git clone git@github.com:olkrpv/foodgram_project_react.git
```

Перейти в папку infra в командной строке:

```
cd foodgram_project_react/infra
```

Выполнить команду (если у вас Linux, последующиее команды начинайте со слова sudo):

```
docker compose up --build
```

Далее нужно зайти в контейнер бэкенда:

```
docker exec -it infra-backend-1 bash
```

И последовательно выполнить следующие команды:
```
./manage.py migrate
./manage.py collectstatic
./manage.py createsuperuser
./manage.py importcsv ingredients.csv
```

Проект будет доступен по адресу:
http://localhost/

### Документация API

После запуска проекта в контейнерах к API будет доступна по адресу:
http://localhost/api/docs/

### Стек технологий:
- Python 3.9
- Django Framework
- Django Rest Framework
- Djoser
- PostgreSQL
- Gunicorn
- Docker
- Nginx
