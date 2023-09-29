Данный проект представляет собой учебный **RESTful API** проект **Яндекс.Практикум** для создания и управления постами, группами, комментариями и подписками пользователей.

**Установка.**

**Клонировать репозиторий:**

git clone git@github.com:d1g-1t/api_final_yatube.git

**Перейти в папку проекта:**

cd api_final_yatube

**Создать и активировать виртуальное окружение:**

python -m venv venv 
source venv/Scripts/activate

**Обновить pip:**

python -m pip install --upgrade pip

**Установить зависимости:**

pip install -r requirements.txt

**Выполнить миграции:**

python manage.py migrate

**Запустить сервер:**

python manage.py runserver

**Документация проекта будет доступна по адресу:**

http://127.0.0.1:8000/redoc/

**Примеры запросов к API:**

**Get-запрос списка всех постов :**

http://127.0.0.1:8000/api/v1/posts/


**Get-запрос определнного поста:**

http://127.0.0.1:8000/api/v1/posts/1/

**Get-запрос комментариев к посту:**

http://127.0.0.1:8000/api/v1/posts/1/comments/

**Get-запрос списка всех групп:**

http://127.0.0.1:8000/api/v1/groups/