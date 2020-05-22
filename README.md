"Онлайн-голосование"
===================

Сайт для голосования

Что нужно для запуска проекта
-------------

- Установите все необходимые пакеты:
```
sudo apt-get install git
sudo apt-get install python3-virtualenv virtualenv  
```
- Склонируйте проект с GitHub
- Создайте и запустите отдельное виртуальное окружение:
```
mkdir ~/venvs
cd ~/venvs
virtualenv -p /usr/bin/python3 dj_venv
source ~/venvs/dj_venv/bin/activate
```
Или создайте автоматически в PyCharm
- Перейдите в папку проекта (предположим, что она находится прямо в домашней): 
```
cd ~/votings_2
```
- Установите все необходимые пакеты: 
```
pip install -r requirements.txt
```
- Запустите процесс инициализации БД: 
```
python manage.py makemigrations
python manage.py migrate
```

- Настройте проект в PyCharm:
  - File->New project
  - Путь к папке проекта: ~/votings_2
  - Интерпретатор: Add local -> Выбираем "~/venvs/dj_venv/bin/python3" -> Ok -> Ждём, пока окружение проиндексируется
  - Нажимаем Ok и соглашаемся с предложением создать проект из существующих исходников
  - Добавляем конфигурацию запуска: "Edit configurations" -> "+" - > Python -> Имя скрипта: votings/manage.py -> параметр "runserver" -> Apply -> Ok
- Проект готов к запуску.
