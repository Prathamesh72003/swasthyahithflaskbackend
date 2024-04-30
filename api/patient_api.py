import uuid
from flask import Blueprint, request, jsonify
from firebase_admin import firestore

patient_api = Blueprint('patient_api', __name__)

# Initialize Firestore client
db = firestore.client()

# API TO GET ALL PATIENTS RECORD
@patient_api.route('/', methods=['GET'])
def get_all_patients():
    try:
        patients_ref = db.collection('Patients')
        patients = [doc.to_dict() for doc in patients_ref.stream()]
        return jsonify(patients), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500

# API TO GET SPECIFIC PATIENT'S RECORD
@patient_api.route('/<phone>', methods=['GET'])
def get_patient_by_phone(phone):
    try:
        patients_ref = db.collection('Patients')
        query = patients_ref.where('phone', '==', phone)
        patients = [doc.to_dict() for doc in query.stream()]
        if not patients:
            return jsonify({'message': 'Patient not found'}), 404
        return jsonify(patients[0]), 200  # Assuming phone numbers are unique
    except Exception as e:
        return jsonify({'message': str(e)}), 500

# API TO REGISTER A PATIENT IN THE DATABASE
@patient_api.route('/', methods=['POST'])
def register_patient():
    try:
        data = request.json
        patient_data = {
            'id': str(uuid.uuid4()),
            'name': data['name'],
            'phone': data['phone'],
            'age': data['age'],
            'address': data['address']
        }
        patients_ref = db.collection('Patients')
        patients_ref.document().set(patient_data)
        return jsonify(patient_data), 201
    except Exception as e:
        return jsonify({'message': str(e)}), 400

# API FOR PATIENT TO INSERT THEIR PRESCRIPTION TO DATABASE
@patient_api.route('/<phone>/addReports', methods=['PATCH'])
def add_reports(phone):
    try:
        data = request.json
        patients_ref = db.collection('Patients')
        query = patients_ref.where('phone', '==', phone)
        patients = [doc for doc in query.stream()]
        if not patients:
            return jsonify({'message': 'Patient not found'}), 404
        patient_ref = patients[0].reference
        patient_data = patients[0].to_dict()
        patient_data['reports'] = patient_data.get('reports', []) + data['reports']
        patient_ref.set(patient_data)
        return jsonify(patient_data), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 400
