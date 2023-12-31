"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, People, Planets
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET'])
def handle_hello():

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(response_body), 200

@app.route('/users', methods=['GET'])
@app.route('/users/<int:user_id>', methods=['GET'])
def handle_users(user_id=None):
    if user_id is None:
        users = User.query.all()
        return jsonify([x.serialize() for x in users]), 200

    user = User.query.filter_by(id=user_id).first()
    if user is not None:
        return jsonify(user.serialize()), 200

    return jsonify({"msg": "Request not valid"}), 400

@app.route('/user/<int:id_user>/favorites', methods=['GET'])
def obtener_favoritos(id_user):

    response_people = User.query.filter_by(id=id_user).first().peopleFav
    response_planets = User.query.filter_by(id=id_user).first().planetsFav
    People = list(map(lambda x: x.serialize(), response_people))
    Planets = list(map(lambda x: x.serialize(), response_planets))

    return jsonify({
        "PeopleFav": People,
        "PlanetsFav": Planets
    }), 200

@app.route('/favorite/planets/<int:planets_id>', methods=['POST'])
def add_planet_fav(planets_id):
    id_user = 2  
    user = User.query.get(id_user)
    planet = Planets.query.get(planets_id)
    favList = User.query.filter_by(id=id_user).first().planetsFav
    favList.append(planet)
    db.session.commit()

    return jsonify({
        "msg": "Your favorite planet has been added correctly :)",
        "PlanetsFav": list(map(lambda x: x.serialize(), favList))
    }), 200

@app.route('/user/<int:user_id>/favorite/people/<int:people_id>', methods=['POST'])
def handle_people_favorites(user_id, people_id):
    id_user = user_id
    user = User.query.get(id_user)
    character = People.query.get(people_id)
    print(id_user)
    favList = User.query.filter_by(id=id_user).first().peopleFav
    favList.append(character)
    db.session.commit()

    return jsonify({
        "msg": "Your favorite character has been added correctly :)",
        "PeopleFav": list(map(lambda x: x.serialize(), favList))
    }), 200

@app.route('/favorite/planets/<int:planets_id>', methods=['DELETE'])
def remove_planet_fav(planets_id):
    id_user = 2
    user = User.query.get(id_user)
    planet = Planets.query.get(planets_id)
    favList = User.query.filter_by(id=id_user).first().planetsFav
    favList.remove(planet)
    db.session.commit()
    return jsonify({
        "msg": "Your favorite planet has been deleted correctly :(",
        "PlanetsFav": list(map(lambda x: x.serialize(), favList))
    }), 200

@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def remove_character_fav(people_id):
    id_user = 2
    user = User.query.get(id_user)
    character = People.query.get(people_id)
    favList = User.query.filter_by(id=id_user).first().peopleFav
    favList.remove(character)
    db.session.commit()

    return jsonify({
        "success": "Your favorite character has been deleted correctly :(",
        "PlanetsFav": list(map(lambda x: x.serialize(), favList))
    }), 200

@app.route('/people', methods=['GET', 'POST'])
def handle_people():

    if request.method == 'POST':
        body = request.get_json()
        character = People(
            name=body['name'], 
            birth_year= body['birth_year'],
            eye_color=body['eye_color']
        )
        db.session.add(character)
        db.session.commit()
        response_body = {
        "msg": "Character added correctly!"
        }
        return jsonify(response_body), 200

    if request.method == 'GET':
        all_people = People.query.all()
        all_people =list(map(lambda x: x.serialize(), all_people))
        response_body = all_people
        return jsonify(response_body), 200

@app.route('/people/<int:character_id>', methods=['GET'])
def get_character(character_id):
    character_query = People.query.get(character_id)
    
    if not character_query:
        response_body = {
            "msg" : "The character you are looking for does not exist."
        }
        return jsonify(response_body), 200

    data_character = character_query.serialize()
    return jsonify({
        "result": data_character
    }), 200

@app.route('/planets', methods=['GET', 'POST'])
def handle_planets():

    if request.method == 'POST':
        body = request.get_json()
        planet = Planets(
            name=body['name'],
            diameter = body['diameter'], 
            gravity = body['gravity'],
            
        )
        db.session.add(planet)
        db.session.commit()
        response_body = {
        "msg": "Planet added correctly!"
        }
        return jsonify(response_body), 200

    if request.method == 'GET':
        all_planets = Planets.query.all()
        all_planets =list(map(lambda x: x.serialize(), all_planets))
        response_body = all_planets
        return jsonify(response_body), 200

@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planet(planet_id):
    planet_query = Planets.query.get(planet_id)
    
    if not planet_query:
        response_body = {
            "msg" : "The planet you are looking for does not exist."
        }
        return jsonify(response_body), 200

    data_planet = planet_query.serialize()
    return jsonify({
        "result": data_planet
    }), 200



# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
