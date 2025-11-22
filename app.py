from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import os
from datetime import datetime
import json
from medical_nlp import MedicalNLPProcessor
import sqlite3
import hashlib

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here-change-in-production'
app.config['DATABASE'] = 'medical_records.db'

# Medical AI System Backend
class MedicalAISystem:
    def __init__(self):
        self.symptoms_db = {
            'fever': ['infection', 'inflammation', 'viral', 'bacterial'],
            'cough': ['respiratory', 'infection', 'allergy', 'asthma'],
            'headache': ['migraine', 'tension', 'sinus', 'hypertension'],
            'nausea': ['gastrointestinal', 'infection', 'motion_sickness'],
            'fatigue': ['anemia', 'infection', 'chronic_fatigue', 'depression']
        }
        
        self.conditions_db = {
            'common_cold': {
                'symptoms': ['cough', 'fever', 'headache', 'fatigue'],
                'severity': 'low',
                'recommendation': 'Rest, hydration, over-the-counter medication'
            },
            'flu': {
                'symptoms': ['fever', 'cough', 'headache', 'fatigue', 'nausea'],
                'severity': 'medium',
                'recommendation': 'Rest, antiviral medication if early, see doctor if severe'
            },
            'migraine': {
                'symptoms': ['headache', 'nausea'],
                'severity': 'medium',
                'recommendation': 'Dark room, pain medication, see doctor if frequent'
            }
        }
    
    def analyze_symptoms(self, symptoms_list):
        """Analyze symptoms and provide preliminary assessment"""
        matched_conditions = []
        confidence_scores = {}
        
        for condition, data in self.conditions_db.items():
            symptom_matches = len(set(symptoms_list) & set(data['symptoms']))
            if symptom_matches > 0:
                match_ratio = symptom_matches / len(data['symptoms'])
                matched_conditions.append({
                    'condition': condition.replace('_', ' ').title(),
                    'match_ratio': match_ratio,
                    'severity': data['severity'],
                    'recommendation': data['recommendation']
                })
                confidence_scores[condition] = match_ratio
        
        # Sort by match ratio
        matched_conditions.sort(key=lambda x: x['match_ratio'], reverse=True)
        
        return {
            'possible_conditions': matched_conditions[:3],  # Top 3
            'analysis_date': datetime.now().isoformat(),
            'symptoms_analyzed': symptoms_list
        }
    
    def get_risk_assessment(self, age, symptoms_list, existing_conditions=None):
        """Calculate risk assessment based on patient data"""
        risk_factors = 0
        warnings = []
        
        if age > 65:
            risk_factors += 1
            warnings.append("Advanced age increases risk")
        
        if existing_conditions:
            risk_factors += len(existing_conditions)
            warnings.append(f"Existing conditions: {', '.join(existing_conditions)}")
        
        if len(symptoms_list) > 4:
            risk_factors += 1
            warnings.append("Multiple symptoms present")
        
        if 'fever' in symptoms_list and age > 65:
            risk_factors += 1
            warnings.append("Fever in elderly requires attention")
        
        risk_level = 'low' if risk_factors < 2 else 'medium' if risk_factors < 4 else 'high'
        
        return {
            'risk_level': risk_level,
            'risk_factors': risk_factors,
            'warnings': warnings,
            'recommendation': 'See doctor immediately' if risk_level == 'high' else 
                            'Monitor and see doctor if symptoms worsen' if risk_level == 'medium' else 
                            'Monitor symptoms'
        }

# Initialize AI systems
medical_ai = MedicalAISystem()
nlp_processor = MedicalNLPProcessor()

# Initialize database
def init_db():
    """Initialize SQLite database for medical records and users"""
    conn = sqlite3.connect(app.config['DATABASE'])
    c = conn.cursor()
    
    # Users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Medical records table (updated with doctor_id)
    c.execute('''
        CREATE TABLE IF NOT EXISTS medical_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            doctor_id INTEGER NOT NULL,
            patient_name TEXT,
            age INTEGER,
            sex TEXT,
            disease TEXT,
            icd_code TEXT,
            conversation_text TEXT,
            structured_data TEXT,
            clinical_note TEXT,
            prescription TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (doctor_id) REFERENCES users(id)
        )
    ''')
    
    # Add doctor_id column if it doesn't exist (for existing databases)
    try:
        c.execute('ALTER TABLE medical_records ADD COLUMN doctor_id INTEGER')
        c.execute('UPDATE medical_records SET doctor_id = 1 WHERE doctor_id IS NULL')
    except sqlite3.OperationalError:
        pass  # Column already exists
    
    # Create default admin user if no users exist
    c.execute('SELECT COUNT(*) FROM users')
    if c.fetchone()[0] == 0:
        # Default password: admin123 (hash)
        default_password = hashlib.sha256('admin123'.encode()).hexdigest()
        c.execute('''
            INSERT INTO users (username, password_hash, full_name)
            VALUES (?, ?, ?)
        ''', ('admin', default_password, 'Administrator'))
        # Create demo doctor
        demo_password = hashlib.sha256('doctor123'.encode()).hexdigest()
        c.execute('''
            INSERT INTO users (username, password_hash, full_name)
            VALUES (?, ?, ?)
        ''', ('doctor1', demo_password, 'Dr. Popescu'))
        c.execute('''
            INSERT INTO users (username, password_hash, full_name)
            VALUES (?, ?, ?)
        ''', ('doctor2', demo_password, 'Dr. Ionescu'))
    
    conn.commit()
    conn.close()

init_db()

def hash_password(password):
    """Hash a password"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, password_hash):
    """Verify a password"""
    return hash_password(password) == password_hash

def require_auth(f):
    """Decorator to require authentication"""
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function

@app.route('/')
def index():
    """Main page - redirect to login if not authenticated"""
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        data = request.json
        username = data.get('username', '')
        password = data.get('password', '')
        
        if not username or not password:
            return jsonify({'error': 'Username and password required'}), 400
        
        conn = sqlite3.connect(app.config['DATABASE'])
        c = conn.cursor()
        c.execute('SELECT id, username, password_hash, full_name FROM users WHERE username = ?', (username,))
        user = c.fetchone()
        conn.close()
        
        if user and verify_password(password, user[2]):
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['full_name'] = user[3]
            return jsonify({
                'success': True,
                'user': {
                    'id': user[0],
                    'username': user[1],
                    'full_name': user[3]
                }
            })
        else:
            return jsonify({'error': 'Invalid username or password'}), 401
    
    # GET request - show login page
    if 'user_id' in session:
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/logout', methods=['POST'])
def logout():
    """Logout"""
    session.clear()
    return jsonify({'success': True})

@app.route('/api/current-user', methods=['GET'])
def get_current_user():
    """Get current authenticated user"""
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    return jsonify({
        'id': session['user_id'],
        'username': session.get('username'),
        'full_name': session.get('full_name')
    })

@app.route('/api/analyze', methods=['POST'])
def analyze():
    """API endpoint for symptom analysis"""
    try:
        data = request.json
        symptoms = data.get('symptoms', [])
        age = data.get('age', None)
        existing_conditions = data.get('existing_conditions', [])
        
        if not symptoms:
            return jsonify({'error': 'No symptoms provided'}), 400
        
        # Analyze symptoms
        analysis = medical_ai.analyze_symptoms(symptoms)
        
        # Get risk assessment if age provided
        if age:
            risk_assessment = medical_ai.get_risk_assessment(age, symptoms, existing_conditions)
            analysis['risk_assessment'] = risk_assessment
        
        return jsonify(analysis)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/symptoms', methods=['GET'])
def get_symptoms():
    """Get list of available symptoms"""
    symptoms = list(medical_ai.symptoms_db.keys())
    return jsonify({'symptoms': symptoms})

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Medly',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/process-conversation', methods=['POST'])
@require_auth
def process_conversation():
    """Process doctor-patient conversation and generate structured output"""
    try:
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        
        data = request.json
        conversation_text = data.get('conversation', '')
        
        if not conversation_text:
            return jsonify({'error': 'No conversation text provided'}), 400
        
        # Process conversation with NLP
        structured_data = nlp_processor.process_conversation(conversation_text)
        
        # Generate clinical note
        clinical_note = nlp_processor.generate_clinical_note(structured_data)
        
        # Generate prescription
        prescription = nlp_processor.generate_prescription(structured_data)
        
        # Store in database with doctor_id
        conn = sqlite3.connect(app.config['DATABASE'])
        c = conn.cursor()
        c.execute('''
            INSERT INTO medical_records 
            (doctor_id, patient_name, age, sex, disease, icd_code, conversation_text, 
             structured_data, clinical_note, prescription)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            session['user_id'],
            structured_data.get('nume_pacient'),
            structured_data.get('varsta'),
            structured_data.get('sex'),
            structured_data.get('boala'),
            structured_data.get('cod_ICD'),
            conversation_text,
            json.dumps(structured_data, ensure_ascii=False),
            clinical_note,
            prescription
        ))
        record_id = c.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'record_id': record_id,
            'structured_data': structured_data,
            'clinical_note': clinical_note,
            'prescription': prescription
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/records', methods=['GET'])
@require_auth
def get_records():
    """Get medical records for current doctor"""
    try:
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        
        conn = sqlite3.connect(app.config['DATABASE'])
        c = conn.cursor()
        c.execute('''
            SELECT id, patient_name, age, disease, icd_code, created_at
            FROM medical_records
            WHERE doctor_id = ?
            ORDER BY created_at DESC
            LIMIT 100
        ''', (session['user_id'],))
        records = []
        for row in c.fetchall():
            records.append({
                'id': row[0],
                'patient_name': row[1],
                'age': row[2],
                'disease': row[3],
                'icd_code': row[4],
                'created_at': row[5]
            })
        conn.close()
        return jsonify({'records': records})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/records/<int:record_id>', methods=['GET'])
@require_auth
def get_record(record_id):
    """Get specific medical record (only if belongs to current doctor)"""
    try:
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        
        conn = sqlite3.connect(app.config['DATABASE'])
        c = conn.cursor()
        c.execute('''
            SELECT * FROM medical_records WHERE id = ? AND doctor_id = ?
        ''', (record_id, session['user_id']))
        row = c.fetchone()
        conn.close()
        
        if not row:
            return jsonify({'error': 'Record not found'}), 404
        
        return jsonify({
            'id': row[0],
            'doctor_id': row[1],
            'patient_name': row[2],
            'age': row[3],
            'sex': row[4],
            'disease': row[5],
            'icd_code': row[6],
            'conversation_text': row[7],
            'structured_data': json.loads(row[8]),
            'clinical_note': row[9],
            'prescription': row[10],
            'created_at': row[11]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/records/<int:record_id>/update', methods=['POST'])
@require_auth
def update_record(record_id):
    """Update clinical note or prescription for a medical record"""
    try:
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        
        data = request.json
        update_type = data.get('type')  # 'note' or 'prescription'
        content = data.get('content', '')
        
        if update_type not in ['note', 'prescription']:
            return jsonify({'error': 'Invalid update type'}), 400
        
        conn = sqlite3.connect(app.config['DATABASE'])
        c = conn.cursor()
        
        # Verify record belongs to current doctor
        c.execute('SELECT doctor_id FROM medical_records WHERE id = ?', (record_id,))
        record = c.fetchone()
        
        if not record:
            conn.close()
            return jsonify({'error': 'Record not found'}), 404
        
        if record[0] != session['user_id']:
            conn.close()
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Update the appropriate field
        if update_type == 'note':
            c.execute('''
                UPDATE medical_records 
                SET clinical_note = ? 
                WHERE id = ? AND doctor_id = ?
            ''', (content, record_id, session['user_id']))
        elif update_type == 'prescription':
            c.execute('''
                UPDATE medical_records 
                SET prescription = ? 
                WHERE id = ? AND doctor_id = ?
            ''', (content, record_id, session['user_id']))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Record updated successfully'})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    
    app.run(debug=True, host='0.0.0.0', port=5000)

