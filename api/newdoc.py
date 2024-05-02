import uuid
from flask import Blueprint, request, jsonify
from firebase_admin import firestore

doc = Blueprint('doc', __name__)

db = firestore.client()
doctors_collection = db.collection('doctors')

@doc.route('/register-doctor', methods=['POST'])
def register_doctor():
    data = request.get_json()

    name = data.get('name')
    phone = data.get('phone')
    specialization = data.get('specialization')
    gender = data.get('gender')
    email = data.get('email')
    id_proof = data.get('idProof')
    password = data.get('pass')

    if not all([name, phone, specialization, gender, email, id_proof, password]):
        return jsonify({'error': 'Please provide all required fields.'}), 400

    try:
        doctor_ref = doctors_collection.document(email)
        doctor_ref.set({
            'name': name,
            'phone': phone,
            'specialization': specialization,
            'gender': gender,
            'email': email,
            'idProof': id_proof,
            'password': password,
            'appointments': [],
            'prescriptions': []
        })

        return jsonify({'message': 'Doctor registered successfully.', 'email': email}), 201
    except Exception as e:
        print('Error registering doctor:', str(e))
        return jsonify({'error': 'An error occurred. Please try again later.'}), 500
    
@doc.route('/login-doctor', methods=['POST'])
def login_doctor():
    data = request.get_json()

    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Please provide email and password.'}), 400

    try:
        # Check if the doctor exists in the database
        doctor_ref = doctors_collection.document(email)
        doctor_data = doctor_ref.get().to_dict()

        if not doctor_data:
            return jsonify({'error': 'Doctor not found.'}), 404

        # Check if the provided password matches the stored password
        if doctor_data['password'] != password:
            return jsonify({'error': 'Invalid password.'}), 401

        # Return the doctor's data on successful login
        return jsonify({'message': 'Doctor login successful.', 'doctor': doctor_data}), 200
    except Exception as e:
        print('Error logging in doctor:', str(e))
        return jsonify({'error': 'An error occurred. Please try again later.'}), 500
    
@doc.route('/get-doctor', methods=['GET'])
def get_doctor_by_email():
    email = request.args.get('email')
    if not email:
        return jsonify({'error': 'Email parameter is missing'}), 400
    
    try:
        # Query the database to fetch the doctor based on email
        doctor_ref = doctors_collection.document(email)
        doctor_data = doctor_ref.get().to_dict()

        if not doctor_data:
            return jsonify({'error': 'Doctor not found.'}), 404

        # Return the doctor's data
        return jsonify({'doctor': doctor_data}), 200
    except Exception as e:
        print('Error fetching doctor:', str(e))
        return jsonify({'error': 'An error occurred while fetching doctor details.'}), 500

