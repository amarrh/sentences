from flask import Flask, jsonify, request
from flask_restful import Api, Resource
import bcrypt

from pymongo import MongoClient

app = Flask(__name__)
api = Api(app)

client = MongoClient("mongodb://db:27017")
db = client.SentencesDB
users = db["Users"]

def verifyPw(username, password):
    hashed_pw = users.find({
        "Username": username
    })[0]["Password"] # [0] - prvog usera kojeg pronađe
                      # vraća njegov ["Password"]

    if bcrypt.hashpw(password.encode('utf-8'), hashed_pw) == hashed_pw:
        return True
    else:
        return False

def countTokens(username):
    tokens = users.find({
        "Username": username
    })[0]["Tokens"]
    return tokens

class Register(Resource):
    def post(self):
        postedData = request.get_json()
        username = postedData["username"] #"username" iz jsona
        password = postedData["password"]

        hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()) #heširanje passworda

        users.insert({
            "Username": username,
            "Password": hashed_pw,
            "Sentence": "",
            "Tokens": 6
        })

        retJson = {
            "msg": "Successful.",
            "status": 200
        }
        return jsonify(retJson)

class Store(Resource):
    def post(self):
        postedData = request.get_json()
        username = postedData["username"]
        password = postedData["password"]
        sentence = postedData["sentence"]

        correct_pw = verifyPw(username, password)
        if not correct_pw:
            retJson = {
                "status": 302
            }
            return jsonify(retJson)

        num_tokens = countTokens(username)
        if num_tokens <= 0:
            retJson = {
                "status": 301
            }
            return jsonify(retJson)

        users.update({
            "Username": username #kriterij pretrage - tog usera trazi da doda recenicu
            }, {
                "$set":{
                    "Sentence":sentence, #dodaje recenicu
                    "Tokens": num_tokens-1 #umanjuje tokene
                    }
            })

        retJson = {
            "msg": "Sentence saved.",
            "status": 200
            }
        return jsonify(retJson)


class Retrieve(Resource):
    def post(self):
        postedData = request.get_json()

        username = postedData["username"]
        password = postedData["password"]

        correct_pw = verifyPw(username, password)
        if not correct_pw:
            retJson = {
                "status": 302
            }
            return jsonify(retJson)

        num_tokens = countTokens(username)
        if num_tokens <= 0:
            retJson = {
                "status": 301
            }
            return jsonify(retJson)

        sentence = users.find({
            "Username": username
        })[0]["Sentence"]

        users.update({
            "Username": username
            }, {
            "$set":{"Tokens": num_tokens-1}
        })

        retJson = {
            "status": 200,
            "Sentence": str(sentence)
        }
        return jsonify(retJson)

api.add_resource(Register, "/register")
api.add_resource(Store, "/store")
api.add_resource(Retrieve, "/get")

if __name__=="__main__":
    app.run(host='0.0.0.0')

'''
User registration
10 tokena po Useru
1 recenica u bazi 1 token
1 ispis recenice 1 token
'''

"""
from flask import Flask, jsonify, request
from flask_restful import Api, Resource

from pymongo import MongoClient

app = Flask(__name__)
api = Api(app)

client = MongoClient("mongodb://db:27017")
db = client.aNewDB
UserNum = db["UserNum"]

UserNum.insert({
    'num_of_users':0
})

class Visit(Resource):
    def get(self):
        prev_num = UserNum.find({})[0]['num_of_users']
        new_num = prev_num + 1
        UserNum.update({}, {"$set":{"num_of_users": new_num}})
        return str("Hello User " + str(new_num))

class Add(Resource):
    def post(self):
        postedData = request.get_json()

        x = postedData["x"]
        y = postedData["y"]
        x = int(x)
        y = int(y)

        ret = x+y

        retMap = {
            'Message': ret,
            'Status Code': 200
        }
        return jsonify(retMap)


api.add_resource(Add, "/add")
api.add_resource(Visit, "/hello")

if __name__=="__main__":
    app.run(host='0.0.0.0')
"""
