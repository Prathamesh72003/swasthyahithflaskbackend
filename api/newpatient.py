import uuid
from flask import Blueprint, request, jsonify
from firebase_admin import firestore
from datetime import datetime

patient = Blueprint('patient', __name__)

db = firestore.client()
patients_collection = db.collection('patients')
doctors_collection = db.collection('doctors')

@patient.route('/register', methods=['POST'])
def register_patient():
    try:
        data = request.get_json()

        required_fields = ['name', 'phone', 'age', 'gender', 'email', 'IdProof', 'pass']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing field: {field}'}), 400

        email = data['email']
        if patients_collection.document(email).get().exists:
            return jsonify({'error': 'Patient already exists'}), 400

        patient_data = {
            'name': data['name'],
            'phone': data['phone'],
            'age': data['age'],
            'gender': data['gender'],
            'email': email,
            'IdProof': data['IdProof'],
            'pass': data['pass'],
            'appointments': {}
        }

        patients_collection.document(email).set(patient_data)

        return jsonify({'message': 'Patient registered successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@patient.route('/get-patient-info', methods=['GET'])
def get_patient_info():
    email = request.args.get('email')

    if not email:
        return jsonify({'error': 'Email parameter is missing.'}), 400

    try:
        patient_ref = patients_collection.document(email)
        patient_data = patient_ref.get().to_dict()

        if not patient_data:
            return jsonify({'error': 'Patient not found.'}), 404

        return jsonify({'patient': patient_data}), 200
    except Exception as e:
        print('Error fetching patient info:', str(e))
        return jsonify({'error': 'An error occurred while fetching patient info.'}), 500

    
@patient.route('/login-patient', methods=['POST'])
def login_patient():
    data = request.get_json()

    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Please provide email and password.'}), 400

    try:
        patient_ref = patients_collection.document(email)
        patient_data = patient_ref.get().to_dict()

        if not patient_data:
            return jsonify({'error': 'Patient not found.'}), 404

        if patient_data['pass'] != password:
            return jsonify({'error': 'Invalid password.'}), 401

        return jsonify({'message': 'Patient login successful.', 'patient': patient_data}), 200
    except Exception as e:
        print('Error logging in patient:', str(e))
        return jsonify({'error': 'An error occurred. Please try again later.'}), 500

@patient.route('/book-appointment', methods=['POST'])
async def book_appointment():
    try:
        data = request.get_json()

        doctor_email = data.get('doctor_email')
        patient_email = data.get('patient_email')
        appointment_date = data.get('appointment_date')
        current_condition = data.get('current_condition')
        specific_symptoms = data.get('specific_symptoms')
        any_allergy = data.get('any_allergy')

        if not all([doctor_email, patient_email, appointment_date]):
            return jsonify({'error': 'Please provide doctor email, patient email, and appointment date.'}), 400

        doctor_ref = doctors_collection.document(doctor_email)
        doctor_ref.collection('appointments').add({
            'patient_email': patient_email,
            'appointment_date': appointment_date,
            'current_condition': current_condition,
            'specific_symptoms': specific_symptoms,
            'any_allergy': any_allergy
        })

        patient_ref = patients_collection.document(patient_email)
        patient_ref.collection('appointments').add({
            'doctor_email': doctor_email,
            'appointment_date': appointment_date,
            'current_condition': current_condition,
            'specific_symptoms': specific_symptoms,
            'any_allergy': any_allergy
        })

        return jsonify({'message': 'Appointment booked successfully.'}), 200
    except Exception as e:
        print('Error booking appointment:', str(e))
        return jsonify({'error': 'An error occurred while booking appointment.'}), 500