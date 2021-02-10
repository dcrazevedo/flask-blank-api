import os
from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy_json import mutable_json_type
from sqlalchemy_serializer import SerializerMixin
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()
        
app = Flask(__name__)

# database
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DB_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model, SerializerMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'

class Cart(db.Model, SerializerMixin):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    data = db.Column(mutable_json_type(dbtype=JSONB, nested=True))

    def __repr__(self):
        return f"<Chart {self.id} {self.user_id}>"
    
# Api
api = Api()

class HelloWorld(Resource):
    def get(self):
        return jsonify({'hello':'world'})

class Users(Resource):
    def get(self):
        users = User.query.all()
        return jsonify({'users':[user.to_dict() for user in users]})

    def post(self):
        data = request.get_json()
        new_user = User(username=data["username"], email=data["email"])
        db.session.add(new_user)
        db.session.commit()
        return jsonify(new_user.to_dict())

class UserItem(Resource):
    def get(self, user_id):
        user = User.query.filter_by(id=user_id).first_or_404()
        return jsonify(user.to_dict())
    
    def put(self, user_id):
        data = request.get_json()
        user = User.query.get_or_404(user_id)
        user.username=data['username']
        user.email=data['email']
        db.session.commit()
        return jsonify(user.to_dict())
    
    def delete(self, user_id):
        user = User.query.filter_by(id=user_id).first_or_404()
        db.session.delete(user)
        db.session.commit()
        return jsonify(user.to_dict())

class MyCarts(Resource):
    def get(self, user_id):
        carts = Cart.query.filter_by(user_id=user_id)
        return jsonify({'charts':[cart.to_dict() for cart in carts]})

class Carts(Resource):
    def get(self):
        carts = Cart.query.all()
        return jsonify({'Charts':[cart.to_dict() for cart in carts]})

    def post(self):
        data = request.get_json()
        new_cart = Cart(user_id=data["user_id"], data=data["data"])
        db.session.add(new_cart)
        db.session.commit()
        return jsonify(new_cart.to_dict())

class CartsItem(Resource):
    def get(self, id):
        cart = Cart.query.filter_by(id=id).first_or_404()
        return jsonify(cart.to_dict())
    
    def put(self, id):
        data = request.get_json()
        cart = Cart.query.get_or_404(id)
        cart.user_id=data['user_id']
        cart.data=data['data']
        db.session.commit()
        return jsonify(cart.to_dict())
    
    def delete(self, id):
        cart = Cart.query.filter_by(id=id).first_or_404()
        db.session.delete(cart)
        db.session.commit()
        return jsonify(cart.to_dict())

api.add_resource(HelloWorld,'/hello')

api.add_resource(Users,'/users')
api.add_resource(UserItem,'/users/<int:user_id>')

api.add_resource(Carts,'/carts')
api.add_resource(CartsItem,'/carts/<int:id>')
api.add_resource(MyCarts,'/mycarts/<int:user_id>')

api.init_app(app)

def add_user(db):
    admin = User(username='admin',email='admin@email.com')
    guest = User(username='guest',email='guest@email.com')

    db.session.add(admin)
    db.session.add(guest)
    db.session.commit()
    
def add_carts(db):
    date = str(datetime.utcnow())
    cart1 = Chart(user_id=1, data={'name':'h1', 'started_date':date, 'data':{'prod': 'item', 'qtd':0.}})
    cart2 = Chart(user_id=2, data={'name':'h2', 'started_date':date, 'data':{'prod': 'item', 'qtd':0.}})
    cart3 = Chart(user_id=2, data={'name':'h3', 'started_date':date, 'data':{'prod': 'item', 'qtd':0.}})
    
    db.session.add(cart1)
    db.session.add(cart2)
    db.session.add(cart3)
    db.session.commit()

if __name__ == "__main__":
    app.run(debug=True)
