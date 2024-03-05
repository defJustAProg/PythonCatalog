
from typing import Annotated
from fastapi import FastAPI, Request, Query, Header, UploadFile, File
import mysql.connector
from pydantic import BaseModel, Field, validator, field_validator
from decimal import Decimal
from mysql.connector import Error
from starlette.requests import Request

app = FastAPI()
authorized_users={}

try:
    mydb = mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="root",
        port="3306"
    )
    cursor = mydb.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS Catalog DEFAULT CHARSET utf8")
    mydb.commit()

    mydb = mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="root",
        port="3306",
        database="catalog"
    )
    cursor = mydb.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS user (login VARCHAR(255) PRIMARY KEY, password VARCHAR(255), discont BOOL)")
    cursor.execute("CREATE TABLE IF NOT EXISTS positions (name VARCHAR(255) PRIMARY KEY, description VARCHAR(255), file LONGBLOB , price DECIMAL(10,2))")
    mydb.commit()
except Error as e:
    print(e)

class UserRegistration(BaseModel):
    login: str
    password: str = Field(..., min_length=8)

    @field_validator('password')
    def has_digit_and_special_char(cls, password):
        for char in ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"]:
            if char in password:
                for char2 in ["@", "#", "%", "^"]:
                    if char2 in password:
                        return password
        else:
            raise ValueError('Invalid login/password')




#начальная страница авторизации
@app.get("/")
async def read_root(request: Request):
    return { "service FAQ": { "/newuser/": "to registrate on server",
                              "/authorization/": "to make authorization",
                              "/catalog/": "to show all product positions",
                              "/catalog/add/": "to add new product in catalog" } }



@app.put("/newuser/")
async def registration(costumer: UserRegistration):
    mydb = mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="root",
        port="3306",
        database="catalog"
    )

    # Создание объекта
    cursor = mydb.cursor()

    # Выполнение SELECT запроса
    cursor.execute(f"SELECT login,password FROM user WHERE login='{costumer.login}' and password='{costumer.password}'")

    # Получение результатов
    result = cursor.fetchall()
    if result:
        authorized_users['login'] = True
        return {"request": "succsessful authorization"}
    else:

        # SQL запрос для добавления user
        sql = f"INSERT INTO user (login, password, discont) VALUES ('{costumer.login}', '{costumer.password}', FALSE)"

        # Выполнение SQL запроса
        cursor.execute(sql)

        # Завершение транзакции
        mydb.commit()
        authorized_users['login'] = True
        return {"request": "succsessful registration. you are authorized now too"}


@app.get("/authorization/")
async def authorization(login: str = Query(...), password: str = Query(...)):


    mydb = mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="root",
        port="3306",
        database="catalog"
    )

    cursor = mydb.cursor()
    sql = f"SELECT login,password FROM user WHERE login='{login}' and password='{password}'"
    cursor.execute(sql)
    result = cursor.fetchall()

    if result:
        authorized_users[f'{login}'] = True
        return {"request": "succsessful authorization"}
    else:
        return {"request": "invalid login/password"}




@app.get("/catalog/")
async def getCatalog(login: Annotated[str, Header()]):

    mydb = mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="root",
        port="3306",
        database="catalog"
    )

    cursor = mydb.cursor()
    cursor.execute("SELECT * FROM positions")
    result = cursor.fetchall()
    if f'{login}' in authorized_users:
        for item in result:
            if isinstance(item, Decimal):
                result[result.index(item)] = item * Decimal('0.85')
        return {"all positions in catalog", tuple(result)}
    else:
        return {"all positions in catalog",tuple(result)}

class Product(BaseModel):
    name: str
    description: str
    file: Annotated[bytes, File()]
    price: float

@app.put("/catalog/add/")
async def addToCatalog(login: Annotated[str, Header()], name: Annotated[str, Query()], description: Annotated[str, Query()], price: Annotated[float, Query()],file: Annotated[bytes, File()] = None):

    if f'{login}' in authorized_users:
        mydb = mysql.connector.connect(
            host="127.0.0.1",
            user="root",
            password="root",
            port="3306",
            database="catalog"
        )

        cursor = mydb.cursor()
        sql = "INSERT INTO positions (name, description, file, price) VALUES (%s, %s, %s, %s)"
        values = (name, description, file, price)
        cursor.execute(sql, values)
        mydb.commit()
        cursor.execute("SELECT * FROM positions")
        result = cursor.fetchall()

        for item in result:
            if isinstance(item, Decimal):
                result[result.index(item)] = item * Decimal('0.85')

        return {'all positions in catalog',tuple(result)}

    else:
        return {"Accsess denied","To add positions, you must be authorized"}



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
