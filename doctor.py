from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
db = SQLAlchemy(app)
migrate = Migrate(app, db)


class Doctor(db.Model):
    id = db.Column(db.String(10), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    specialty = db.Column(db.String(100), nullable=False)
    availability = db.Column(db.String(20), nullable=False)
    experience = db.Column(db.String(20), nullable=False)
    phone = db.Column(db.Integer, nullable=False)

#Generate the Custom ID for Doctors
def generate_doctor_id():
    last_doctor = Doctor.query.order_by(Doctor.id.desc()).first()
    if last_doctor:
        last_id_number = int(last_doctor.id.replace("scd", ""))
        return f"scd{last_id_number + 1}"
    else:
        return "scd1"
    

@app.route('/v1/doctors/', methods=['GET'])
def get_all_doctors():
    try:
        doctors = Doctor.query.all()
        doctors_list = [
            {
                'id': doctor.id,
                'name': doctor.name,
                'specialty': doctor.specialty,
                'availability': doctor.availability,
                'experience': doctor.experience,
                'phone': doctor.phone

            }
            for doctor in doctors
        ]
        return jsonify({'doctors': doctors_list})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/v1/doctors', methods=['POST'])
def add_doctor():
    try:
        data = request.json
        new_doctor = Doctor(
            id=generate_doctor_id(),  # Generate custom ID
            name=data['name'],
            specialty=data['specialty'],
            availability=data['availability'],
            experience=data['experience'],
            phone=data['phone']
        )
        db.session.add(new_doctor)
        db.session.commit()
        return jsonify({'message': 'Doctor added successfully', 'doctor': {
            'id': new_doctor.id,
            'name': new_doctor.name,
            'specialty': new_doctor.specialty,
            'availability': new_doctor.availability,
            'experience': new_doctor.experience,
            'phone':new_doctor.phone

        }}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/v1/doctors/<string:id>', methods=['GET'])
def get_patient(id):
    doctor = Doctor.query.get_or_404(id)
    return jsonify({'name': doctor.name, 'specialty':doctor.specialty, 'availability':doctor.availability, 'experience':doctor.experience, 'phone':doctor.phone})


@app.route('/v1/doctors/<string:id>', methods=['PUT'])
def update_doctor(id):
    try:
        doctor = Doctor.query.get(id)
        if not doctor:
            return jsonify({'error': 'Doctor not found'}), 404
        data = request.json
        if 'phone' in data:
            doctor.phone = data['phone']
        if 'availability' in data:
            doctor.availability = data['availability']
        db.session.commit()
        
        return jsonify({'message': 'Doctor data updated successfully', 'doctor': {
            'name': doctor.name,
            'specialty': doctor.specialty,
            'availability': doctor.availability,
            'experience': doctor.experience,
            'phone': doctor.phone
        }}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/v1/doctors/search', methods=['GET'])
def search_doctors_by_specialty():
    try:
        specialty = request.args.get('specialty')
        if not specialty:
            return jsonify({'error': 'Specialty query parameter is required'}), 400
        
        doctors = Doctor.query.filter(Doctor.specialty.ilike(f"%{specialty}%")).all()

        if not doctors:
            return jsonify({'message': f'No doctors found with specialty "{specialty}"'}), 404

        doctors_list = [
            {
                'id': doctor.id,
                'name': doctor.name,
                'specialty': doctor.specialty,
                'availability': doctor.availability,
                'experience': doctor.experience,
                'phone': doctor.phone
            }
            for doctor in doctors
        ]
        return jsonify({'doctors': doctors_list}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/v1/doctors/<string:id>', methods=['DELETE'])
def delete_doctor(id):
    try:
        doctor = Doctor.query.get(id)
        if not doctor:
            return jsonify({'error': 'Doctor not found'}), 404

        db.session.delete(doctor)
        db.session.commit()

        return jsonify({'message': f'Doctor with ID {id} has been deleted successfully'}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)