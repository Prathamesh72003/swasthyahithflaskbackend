import uuid
from flask import Blueprint, request, jsonify
from firebase_admin import firestore

doctor_api = Blueprint('doctor_api', __name__)

# Initialize Firestore client
db = firestore.client()

# API TO GET ALL DOCTORS RECORD
@doctor_api.route('/', methods=['GET'])
def get_all_doctors():
    try:
        doctors_ref = db.collection('Doctors')
        doctors = [doc.to_dict() for doc in doctors_ref.stream()]
        return jsonify(doctors), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 500

# API TO GET SPECIFIC DOCTOR BY PHONE NUMBER
@doctor_api.route('/<phone>', methods=['GET'])
def get_doctor_by_phone(phone):
    try:
        doctors_ref = db.collection('Doctors')
        query = doctors_ref.where('phone', '==', phone)
        doctors = [doc.to_dict() for doc in query.stream()]
        if not doctors:
            return jsonify({'message': 'Doctor not found'}), 404
        return jsonify(doctors[0]), 200  # Assuming phone numbers are unique
    except Exception as e:
        return jsonify({'message': str(e)}), 500

# API TO REGISTER A DOCTOR IN THE DATABASE
@doctor_api.route('/', methods=['POST'])
def register_doctor():
    try:
        data = request.json
        doctor_data = {
            'id': str(uuid.uuid4()),
            'name': data['name'],
            'qualification': data['qualification'],
            'regNumber': data['regNumber'],
            'hospitalName': data['hospitalName'],
            'hospitalAdr': data['hospitalAdr'],
            'phone': data['phone']
        }
        doctors_ref = db.collection('Doctors')
        doctors_ref.document().set(doctor_data)
        return jsonify(doctor_data), 201
    except Exception as e:
        return jsonify({'message': str(e)}), 400

# API TO UPDATE DOCTOR'S PATIENT DATA ARRAY WHENEVER A PATIENT IS CURED
@doctor_api.route('/<phone>/addPatientsData', methods=['PATCH'])
def update_doctor_patient_data(phone):
    try:
        data = request.json
        doctors_ref = db.collection('Doctors')
        query = doctors_ref.where('phone', '==', phone)
        doctors = [doc for doc in query.stream()]
        if not doctors:
            return jsonify({'message': 'Doctor not found'}), 404
        doctor_ref = doctors[0].reference
        doctor_data = doctors[0].to_dict()
        patient_data = {
            'patientId': data['patientId'],
            'links': data['links']
        }
        doctor_data['patientData'] = doctor_data.get('patientData', []) + [patient_data]
        doctor_ref.set(doctor_data)
        return jsonify(doctor_data), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 400
