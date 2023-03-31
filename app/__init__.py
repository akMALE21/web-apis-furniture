from flask import Flask, request 
from flask_jwt_extended import JWTManager
import os
import psycopg2
from dotenv import load_dotenv

CREATE_IKEA_TABLE = ("""CREATE TABLE IF NOT EXISTS ikea (
    id INT,
    item_id INT,
    name VARCHAR(21),
    category VARCHAR(13),
    price NUMERIC(5, 1),
    old_price VARCHAR(12),
    sellable_online VARCHAR(5),
    link VARCHAR(127),
    other_colors VARCHAR(3),
    short_description VARCHAR(66),
    designer VARCHAR(518),
    depth INT,
    height INT,
    width INT
    );"""
)

CREATE_USERS_TABLE = (
    "CREATE TABLE IF NOT EXISTS users (username VARCHAR, password VARCHAR);"
)

INSERT_IKEA = (
    "insert into ikea (id,item_id,name,category,price,old_price,sellable_online,link,other_colors,short_description,designer,depth,height,width) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
)
load_dotenv()

host = "tiny.db.elephantsql.com"
databae = "evraaplf"
user = "evraaplf"
password = "NFS3gR7li2xSae2TgMWqKXdWqGYm7S69"

app = Flask(__name__)
url = os.getenv('DATABASE_URL')
connection = psycopg2.connect(host=host, database=databae, user=user, password=password)
connection_cursor = connection.cursor()

app.config['JWT_SECRET_KEY'] = 'secret'
jwt = JWTManager(app)

from app import routes #Memanggil file routes (akan segera dibuat)