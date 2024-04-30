from flask import Flask
import firebase_admin
from firebase_admin import credentials, initialize_app

cred = credentials.Certificate("api/key.json")
default_app = initialize_app(cred)

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'secret!'
    
    
    from .doctor_api import doctor_api
    from .patient_api import patient_api

    app.register_blueprint(doctor_api, url_prefix='/doctor')
    app.register_blueprint(patient_api, url_prefix='/patient')
    # app.register_blueprint(doctor_api, url_prefix='/doctors')

    return app