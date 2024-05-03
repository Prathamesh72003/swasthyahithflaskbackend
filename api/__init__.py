from flask import Flask
import firebase_admin
from firebase_admin import credentials, initialize_app

cred = credentials.Certificate("api/key.json")
default_app = initialize_app(cred)

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'secret!'
    
    from .newdoc import doc
    from .newpatient import patient

    app.register_blueprint(doc, url_prefix='/doc')
    app.register_blueprint(patient, url_prefix='/patient')

    return app