# PythonCatalog
## Python 3.11, FastAPI, MySQL
Скрипт main.py запускает unicorn сервер по адресу '127.0.0.1:8000'.
Для корректной работы необходим установленный сервер MySQl, адрес исходного кода сервера 'C:\Program Files\MySQL\MySQL Server 8.0\bin' должен быть добавлен в системную переменную Path. 
Логин и пароль доступа к серверу MySQL нужно вписать в скрипт main.py вместо 'root' там, где происходит подключение к БДю
## Функции, реализующие сервис

1) authorization - авторизует пользователя, если такой присутствует в БД Пример запроса:
   curl -X 'GET' \
  'http://127.0.0.1:8000/authorization/?login=user1234%40&password=user1234%40' \
  -H 'accept: application/json'
   После авторизации пользователю предоставляется возможность добавлять товары в каталог.
   
2) newuser - регистрирует пользователя в БД и сразу авторизует в системе. Если регистрирующаяся учетная запись уже присутствует в БД, произойдет авторизация.
   Пример запроса:
   curl -X 'PUT' \
  'http://127.0.0.1:8000/newuser/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "login": "user1234@",
  "password": "user1234@"}'

3) catalog - выводит все позиции по товарам, находящимся в БД. Для авторизованных пользователей информация о цене показана со скидкой.
    Пример запроса:
    curl -X 'GET' \
  'http://127.0.0.1:8000/catalog/' \
  -H 'accept: application/json' \
  -H 'login: user1234@'

4) catalog/add - дабавление товара в каталог для авторизованных пользователей. Параметр 'file' для фото необезателен. Для авторизованных пользователей информация о цене показана со скидкой.
   Пример запроса:
   curl -X 'PUT' \
  'http://127.0.0.1:8000/catalog/add/?name=name&description=description&price=4' \
  -H 'accept: application/json' \
  -H 'login: uzer1234@' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file='
