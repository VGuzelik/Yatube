# Yatube

## Описание:
Социальная сеть Yatube позволяет создать собственную страницу, публиковать посты, подписываться на других пользователей, оставлять и редактировать комментарии к постам.

## Технологии:
Python, Django, Unittest, Django debug toolbar, Django ORM, SQLite

<details>
<summary><h2>Как запустить проект:</h2></summary>

### *Клонируйте репозиторий:*
```
git@github.com:VGuzelik/Yatube.git
```

### *Установите и активируйте виртуальное окружение:*
Win:
```
python -m venv venv
venv/Scripts/activate
```

Mac:
```
python3 -m venv venv
source venv/bin/activate
```

### *Установите зависимости из файла requirements.txt:*
```
pip install -r requirements.txt
```

### *Перейдите в директорию с файлом manage.py, создайте и примените миграции (python3 для Mac):*
```
cd yatube
python manage.py makemigrations
python manage.py migrate
```

### *Создайте суперпользователя (python3 для Mac):*
```
python manage.py createsuperuser
```

### *Запустите сервер (python3 для Mac):*
```
python manage.py runserver
```
</details>

## Разработчик:
[Гузелик_Виктор](https://github.com/VGuzelik)
