import uuid
from flask import Blueprint, request, jsonify
from firebase_admin import firestore

patient = Blueprint('patient', __name__)

db = firestore.client()
patients_collection = db.collection('patients')

@patient.route('/register', methods=['POST'])
def register_patient():
    try:
        # Extract data from request
        data = request.get_json()

        # Check if all required fields are present
        required_fields = ['name', 'phone', 'age', 'gender', 'email', 'IdProof', 'pass']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing field: {field}'}), 400

        # Check if patient already exists
        email = data['email']
        if patients_collection.document(email).get().exists:
            return jsonify({'error': 'Patient already exists'}), 400

        # Create patient document with email as document ID
        patient_data = {
            'name': data['name'],
            'phone': data['phone'],
            'age': data['age'],
            'gender': data['gender'],
            'email': email,
            'IdProof': data['IdProof'],
            'pass': data['pass'],
        }

        patients_collection.document(email).set(patient_data)

        # Create empty prescriptions collection
        prescriptions_collection = patients_collection.document(email).collection('prescriptions')
        prescriptions_collection.add({})

        # Create empty appointments collection
        appointments_collection = patients_collection.document(email).collection('appointments')
        appointments_collection.add({})

        return jsonify({'message': 'Patient registered successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@patient.route('/login-patient', methods=['POST'])
def login_patient():
    data = request.get_json()

    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Please provide email and password.'}), 400

    try:
        # Check if the patient exists in the database
        patient_ref = patients_collection.document(email)
        patient_data = patient_ref.get().to_dict()

        if not patient_data:
            return jsonify({'error': 'Patient not found.'}), 404

        # Check if the provided password matches the stored password
        if patient_data['pass'] != password:
            return jsonify({'error': 'Invalid password.'}), 401

        # Return the patient's data on successful login
        return jsonify({'message': 'Patient login successful.', 'patient': patient_data}), 200
    except Exception as e:
        print('Error logging in patient:', str(e))
        return jsonify({'error': 'An error occurred. Please try again later.'}), 500

