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

class Chart(db.Model, SerializerMixin):
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

class MyCharts(Resource):
    def get(self, user_id):
        charts = Chart.query.filter_by(user_id=user_id)
        return jsonify({'charts':[chart.to_dict() for chart in charts]})

class Charts(Resource):
    def get(self):
        hives = Chart.query.all()
        return jsonify({'Charts':[chart.to_dict() for chart in charts]})

    def post(self):
        data = request.get_json()
        new_hive = Chart(user_id=data["user_id"], data=data["data"])
        db.session.add(new_hive)
        db.session.commit()
        return jsonify(new_hive.to_dict())

class ChartsItem(Resource):
    def get(self, id):
        hive = Beehive.query.filter_by(id=id).first_or_404()
        return jsonify(hive.to_dict())
    
    def put(self, id):
        data = request.get_json()
        hive = Beehive.query.get_or_404(id)
        hive.user_id=data['user_id']
        hive.data=data['data']
        db.session.commit()
        return jsonify(hive.to_dict())
    
    def delete(self, id):
        hive = Beehive.query.filter_by(id=id).first_or_404()
        db.session.delete(hive)
        db.session.commit()
        return jsonify(hive.to_dict())

api.add_resource(HelloWorld,'/hello')

api.add_resource(Users,'/users')
api.add_resource(UserItem,'/users/<int:user_id>')

api.add_resource(Charts,'/charts')
api.add_resource(ChartsItem,'/charts/<int:id>')
api.add_resource(MyCharts,'/mycharts/<int:user_id>')

api.init_app(app)

def add_user(db):
    admin = User(username='admin',email='admin@email.com')
    guest = User(username='guest',email='guest@email.com')

    db.session.add(admin)
    db.session.add(guest)
    db.session.commit()
    
def add_hives(db):
    date = str(datetime.utcnow())
    chart1 = Chart(user_id=1, data={'name':'h1', 'started_date':date, 'data':{'prod': 'item', 'qtd':0.}})
    chart2 = Chart(user_id=2, data={'name':'h2', 'started_date':date, 'data':{'prod': 'item', 'qtd':0.}})
    chart3 = Chart(user_id=2, data={'name':'h3', 'started_date':date, 'data':{'prod': 'item', 'qtd':0.}})
    
    db.session.add(chart1)
    db.session.add(chart2)
    db.session.add(chart3)
    db.session.commit()

if __name__ == "__main__":
    app.run(debug=True)
