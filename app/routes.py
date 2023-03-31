from app import app,jwt,connection_cursor,connection,CREATE_IKEA_TABLE,CREATE_USERS_TABLE,INSERT_IKEA
from flask import jsonify, request, make_response
from flask_bcrypt import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from datetime import timedelta
import requests

@app.post("/api/ikea")
def create_table_ikea():
    with connection.cursor() as cursor:
        cursor.execute(CREATE_IKEA_TABLE)
        cursor.execute(INSERT_IKEA)
        connection.commit()
        return make_response(jsonify({"message": "Ikea table created"}), 201)

@app.post("/api/users")
def create_table_users():
    with connection.cursor() as cursor:
        cursor.execute(CREATE_USERS_TABLE)
        connection.commit()
        return make_response(jsonify({"message": "Users table created"}), 201)

# register
@app.route("/api/v1/register", methods=["POST"])
def register():
    username = request.json.get('username', None)
    password = request.json.get('password', None)

    connection_cursor.execute("select * from users where username=%s", (username,))
    user = connection_cursor.fetchone()
    if user:
        return jsonify({'message': 'user already exists'}), 409

    hashed_password = generate_password_hash(password).decode('utf-8')

    connection_cursor.execute("insert into users (username, password) values (%s,%s)", (username, hashed_password))
    connection.commit()

    return jsonify({'message': 'registered successfully'}), 200

# login
@app.route("/api/v1/login", methods=["POST"])
def login():
    username = request.form['username']
    password = request.form['password']

    if not username or not password:
        return make_response('could not verify', 401, {'WWW.Authentication': 'Basic realm: "login required"'})

    connection_cursor.execute("select * from users where username=%s", (username,))
    user = connection_cursor.fetchone()
    if not user:
        return make_response('could not verify', 401, {'WWW.Authentication': 'Basic realm: "login required"'})

    if check_password_hash(user[1], password):
        access_token = create_access_token(identity=user[0], expires_delta=timedelta(minutes=5))
        return jsonify({'token': access_token}), 200
    return make_response('could not verify', 401, {'WWW.Authentication': 'Basic realm: "login required"'})

#rekomendasi kamar
@app.route("/api/v1/rekomendasi_kamar", methods=["POST"])
@jwt_required()
def rekomendasi_kamar():
    #1. login api mbol
    loginurl = requests.post("https://tubeststrayhan.azurewebsites.net/loginuser", data={"username":"admin","password":"admin"})
    #2. tokennya disimpen ke sebuah variable
    tokenMbol = loginurl.json().get("token")
    roomurl = 'https://tubeststrayhan.azurewebsites.net/roomarea'

    #3. variable token itu dijadikan value dari header Authorization
    jar = requests.cookies.RequestsCookieJar()
    jar.set('access_token_cookie', tokenMbol, domain='tubeststrayhan.azurewebsites.net', path='/')

    #4. request ke api area mbol
    landsize = request.form['landsize']
    bedroom = request.form['bedroom']
    reqroomarea = requests.post(roomurl, cookies=jar, headers={'Authorization': 'Bearer '+tokenMbol, 'Content-Type': 'application/json'}, json={"landsize": landsize, "bedroom": bedroom})
    
    #5. hasilnya diolah deh buat response nya
    roomarea = reqroomarea.json()
    #print(roomarea[0]["bathroom"])
    luaskamar = roomarea[0]["bedroom_area"]

    connection_cursor.execute("select name, category, price, link, height, width, height * width from ikea where category = 'Beds' and height * width <= %s", [luaskamar])
    datakasur = connection_cursor.fetchall()
    listkasur = []
    for i in range(len(datakasur)):
        # luaskasur = float(datakasur[i][0]) * float(datakasur[i][1])
        # listkasur.append(luaskasur)
        rupiah = float(datakasur[i][2]) * 16000
        newItem = {
            "luaskamar": luaskamar,
            "name": datakasur[i][0],
            "category": datakasur[i][1],
            "price": rupiah,
            "link": datakasur[i][3],
            "luas_kasur": datakasur [i][6]
        }

        listkasur.append(newItem)
    return jsonify(listkasur)

#rekomendasi furniture
@app.route("/api/v1/rekomendasi", methods=["POST"])
@jwt_required()
def rekomendasi():
    price = request.json.get('price', None)
    bobot = request.json.get('bobot', None)
    convert_price = (float(price)*(float(bobot)/100))/16000

    connection_cursor.execute("select name,category,price,short_description,link from ikea where price <= %s", [convert_price])
    furniture = connection_cursor.fetchall()
    furList = []
    for i in range(len(furniture)):
        rupiah = float(furniture[i][2]) * 16000

        newItem = {
            "name": furniture[i][0],
            "category": furniture[i][1],
            "price": rupiah,
            "short_description": furniture[i][3],
            "link": furniture[i][4]
        }
        
        furList.append(newItem)

    return jsonify(furList)




# get all ikea
@app.route("/api/v1/ikea", methods=["GET"])
@jwt_required()
def read():
    connection_cursor.execute("select * from ikea")
    return jsonify(connection_cursor.fetchall())

@app.route("/api/v1/ikea", methods=["POST"])
@jwt_required()
def create():
    data = request.get_json()
    connection_cursor.execute("insert into ikea (id,item_id,name,category,price,old_price,sellable_online,link,other_colors,short_description,designer,depth,height,width) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", (data['id'], data['item_id'], data['name'], data['category'], data['price'], data['old_price'], data['sellable_online'], data['link'], data['other_colors'], data['short_description'], data['designer'], data['depth'], data['height'], data['width']))
    connection.commit()
    return jsonify({'ikea': data}),200

@app.route("/api/v1/ikea", methods=["PUT"])
@jwt_required()
def update():
    data = request.get_json()
    connection_cursor.execute("update ikea set name=%s, category=%s, price=%s, old_price=%s, sellable_online=%s, link=%s, other_colors=%s, short_description=%s, designer=%s, depth=%s, height=%s, width=%s where id=%s", (data['name'], data['category'], data['price'], data['old_price'], data['sellable_online'], data['link'], data['other_colors'], data['short_description'], data['designer'], data['depth'], data['height'], data['width'], data['id']))
    connection.commit()
    return jsonify({'ikea': data}),200

@app.route("/api/v1/ikea", methods=["DELETE"])
@jwt_required()
def delete():
    data = request.get_json()
    connection_cursor.execute("delete from ikea where id=%s", (data['id'],))
    connection.commit()
    return jsonify({'ikea': data}),200