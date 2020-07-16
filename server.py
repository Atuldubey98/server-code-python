from flask import Flask, jsonify, request
from pymongo import MongoClient
import bcrypt
from flask_socketio import SocketIO, send, emit

app = Flask(__name__)

app.config['SECRET_KEY'] = "kljdaskldas"
socketio = SocketIO(app)
client = MongoClient(
    "mongodb+srv://atuldubey:08091959@cluster0-isxbl.mongodb.net/<dbname>?retryWrites=true&w=majority")
db = client.finalchatAPP
users = db.userlist
chatid = db.chatlist
post = db.Posts
user = 0


@socketio.on("getMessage")
def messageEvent(message):
    print(message['message'])
    print(message['chatid'])

    # send(message, broadcast = True)
    chatidcoll = chatid.find_one({"chatid": message['chatid']})
    chatidcoll['message'].append(
        {"mess": message['message'], "sentby": message['sentby']})

    chatid.update_one({"chatid": message['chatid']}, {"$set": chatidcoll})
    emit(message['chatid'], message, broadcast=True)




@app.route('/')
def index():
    print('Connected to server')
    return jsonify({"status": "ok", "data": {}, "error": {}})


@app.route('/login', methods=['POST'])
def loginuser():
    request_data = request.get_json()
    username = request_data['user']
    password = request_data['password']
    existing_user = users.find_one({'user': username})
    if existing_user is None:
        return jsonify({"status": "notok", "mess": "user does not exist"})
    if(bcrypt.hashpw(password.encode('utf-8'), existing_user['password']) == existing_user['password']):
        return jsonify({"status": "ok", "mess": "user logged in", "user": username})
        print("User Logged in", username)
    return jsonify({"status": "notok", "mess": "password incorrect"})


@app.route('/register', methods=['POST'])
def register():
    request_data = request.get_json()
    username = request_data['user']
    password = request_data['password']

    existing_user = users.find_one({'user': username})
    if existing_user is None:
        hasspass = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        users.insert_one({'user': username, 'password': hasspass})
        print("User Registered", username)
        return jsonify({"status": "OK", "mess": "usercreated", "user": username})
    return jsonify({"status": "notok", "mess": "username already exist", 'user': username})


@app.route('/userlist')
def getUserlist():

    userList = []
    for item in users.find():
        itemtoADD = {"user": item['user']}
        userList.append(itemtoADD)
    print(userList)
    return jsonify({"status": "ok", "data": userList})


@app.route('/createchatID', methods=['POST'])
def createchatID():
    request_data = request.get_json()
    chatitem = request_data['chatid']
    extractchatid = chatid.find_one({"chatid": chatitem})
    if extractchatid is None:
        chatid.insert_one({"chatid": chatitem, "message": []})
        print("Chat id createchatitem", chatitem)
        return jsonify({"status": "ok", "mess": "new"})

    return jsonify({"status": "ok", "mess": "old"})


@app.route("/getchatlist/<string:chatidentity>")
def getchatlist(chatidentity):
    chatList = []
    for item in chatid.find({"chatid": chatidentity}):
        itemtoappend = {"chatid": item['chatid'], "message": item['message']}
        chatList.append(itemtoappend)
    if itemtoappend is None:
        return jsonify({"status": "ok", "data": {}, "mess": "Nochat"})
    return jsonify({"status": "ok", "data": itemtoappend, "mess": "working"})


@app.route('/clients')
def getclients():
    clientList = []
    for item in chatid.find():
        itemtoadd = {"chatid": item['chatid']}
        clientList.append(itemtoadd)
    if itemtoadd is None:
        return jsonify({"status": "ok", "data": {}, "mess": "Nochat"})
    return jsonify({"status": "ok", "data": clientList, "mess": "working"})


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", debug=True)
