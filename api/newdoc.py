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

        doctor_ref.collection('appointments')
        doctor_ref.collection('prescriptions')

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

@doc.route('/get-appointments', methods=['GET'])
def get_appointments():
    email = request.args.get('email')
    if not email:
        return jsonify({'error': 'Email parameter is missing'}), 400
    
    try:
        # Query the database to fetch the appointments based on doctor's email
        doctor_ref = doctors_collection.document(email)
        appointments_ref = doctor_ref.collection('appointments')
        appointments = [appointment.to_dict() for appointment in appointments_ref.stream()]

        return jsonify({'appointments': appointments}), 200
    except Exception as e:
        print('Error fetching appointments:', str(e))
        return jsonify({'error': 'An error occurred while fetching appointments.'}), 500
@doc.route('/get-patients', methods=['GET'])
def get_patients():
    email = request.args.get('email')
    if not email:
        return jsonify({'error': 'Email parameter is missing'}), 400
    
    try:
        # Query the database to fetch the patients based on doctor's email
        doctor_ref = doctors_collection.document(email)
        patients_ref = doctor_ref.collection('patients')
        patients = [patient.to_dict() for patient in patients_ref.stream()]

        return jsonify({'patients': patients}), 200
    except Exception as e:
        print('Error fetching patients:', str(e))
        return jsonify({'error': 'An error occurred while fetching patients.'}), 500

@doc.route('/get-prescriptions', methods=['GET'])
def get_prescriptions():
    email = request.args.get('email')
    if not email:
        return jsonify({'error': 'Email parameter is missing'}), 400
    
    try:
        # Query the database to fetch the prescriptions based on doctor's email
        doctor_ref = doctors_collection.document(email)
        prescriptions_ref = doctor_ref.collection('prescriptions')
        prescriptions = [prescription.to_dict() for prescription in prescriptions_ref.stream()]

        return jsonify({'prescriptions': prescriptions}), 200
    except Exception as e:
        print('Error fetching prescriptions:', str(e))
        return jsonify({'error': 'An error occurred while fetching prescriptions.'}), 500
    
@doc.route('/get-appointed-patients', methods=['GET'])
def get_appointed_patients():
    email = request.args.get('email')
    if not email:
        return jsonify({'error': 'Email parameter is missing'}), 400
    
    try:
        # Query the database to fetch the doctor's appointments
        doctor_ref = doctors_collection.document(email)
        appointments_ref = doctor_ref.collection('appointments')
        appointments = [appointment.to_dict() for appointment in appointments_ref.stream()]
        
        # Extract patient email from each appointment
        patient_emails = [appointment['email'] for appointment in appointments]
        
        # Fetch patient details using their email
        patients = []
        for patient_email in patient_emails:
            patient_ref = db.collection('patients').document(patient_email)
            patient_data = patient_ref.get().to_dict()
            if patient_data:
                patients.append(patient_data)
        
        return jsonify({'patients': patients}), 200
    
    except Exception as e:
        print('Error fetching appointed patients:', str(e))
        return jsonify({'error': 'An error occurred while fetching appointed patients.'}), 500

patients_collection = db.collection('patients')

@doc.route('/save-prescription', methods=['POST'])
def save_prescription():

    doctor_email = request.args.get('doctor_email')
    patient_email = request.args.get('patient_email')

    data = request.json

    patient_name = data.get('patientName')
    tablet_prescription = data.get('tabletPrescription')
    tonic_prescription = data.get('tonicPrescription')
    duration = data.get('duration')
    extra_suggestions = data.get('extraSuggestions')

    if not all([doctor_email, patient_email, patient_name, tablet_prescription, tonic_prescription, duration, extra_suggestions]):
        return jsonify({'error': 'Please provide all prescription details, including doctor and patient emails.'}), 400

    try:
        # Save prescription to patient's data
        patient_ref = patients_collection.document(patient_email)
        patient_data = patient_ref.get().to_dict()

        if not patient_data or 'prescriptions' not in patient_data:
            # If the prescriptions collection doesn't exist for the patient, create it
            prescriptions_ref = patient_ref.collection('prescriptions').document()
            prescriptions_ref.set({
                'tabletPrescription': tablet_prescription,
                'tonicPrescription': tonic_prescription,
                'duration': duration,
                'extraSuggestions': extra_suggestions,
                'doc_name': doctor_email
            })
        else:
            # If the prescriptions collection exists, add a new document to it
            prescriptions_ref = patient_ref.collection('prescriptions').document()
            prescriptions_ref.set({
                'tabletPrescription': tablet_prescription,
                'tonicPrescription': tonic_prescription,
                'duration': duration,
                'extraSuggestions': extra_suggestions,
                'doc_name': doctor_email
            })

        # Save prescription to doctor's data
        doctor_ref = doctors_collection.document(doctor_email).collection('prescriptions').document()
        doctor_ref.set({
            'patientName': patient_name,
            'tabletPrescription': tablet_prescription,
            'tonicPrescription': tonic_prescription,
            'duration': duration,
            'extraSuggestions': extra_suggestions
        })

        return jsonify({'message': 'Prescription saved successfully.'}), 200
    except Exception as e:
        print('Error saving prescription:', str(e))
        return jsonify({'error': 'An error occurred while saving prescription.'}), 500

@doc.route('/get-prescriptions-by-patient-email', methods=['GET'])
def get_prescriptions_by_patient_email():
    patient_email = request.args.get('patient_email')

    if not patient_email:
        return jsonify({'error': 'Patient email parameter is missing.'}), 400

    try:
        # Get patient's prescriptions
        patient_ref = patients_collection.document(patient_email)
        prescriptions_ref = patient_ref.collection('prescriptions')
        prescriptions = [prescription.to_dict() for prescription in prescriptions_ref.stream()]

        return jsonify({'prescriptions': prescriptions}), 200
    except Exception as e:
        print('Error fetching prescriptions by patient email:', str(e))
        return jsonify({'error': 'An error occurred while fetching prescriptions by patient email.'}), 500



