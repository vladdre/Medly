from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_file
import os
import sys
from datetime import datetime
import json
import sqlite3
import hashlib
import uuid
import speech_recognition as sr
from werkzeug.utils import secure_filename
import tempfile
from pydub import AudioSegment

# Add backend directory to path for imports
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(BASE_DIR)
sys.path.insert(0, BASE_DIR)

import testModel

app = Flask(__name__, 
            template_folder=os.path.join(PARENT_DIR, 'frontend', 'templates'),
            static_folder=os.path.join(PARENT_DIR, 'frontend', 'static'))

app.config['SECRET_KEY'] = 'medly-secret-key-change-in-production-2024'
app.config['DATABASE'] = os.path.join(PARENT_DIR, 'data', 'medical_records.db')
app.config['UPLOAD_FOLDER'] = os.path.join(PARENT_DIR, 'data', 'uploads')
app.config['RESULTS_FOLDER'] = os.path.join(PARENT_DIR, 'data', 'results')
app.config['MODEL_DIR'] = os.path.join(PARENT_DIR, 'data', 'models', 'finetuned_t5_model')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['ALLOWED_EXTENSIONS'] = {'wav', 'mp3', 'm4a', 'flac', 'ogg', 'webm'}

# Create necessary directories
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['RESULTS_FOLDER'], exist_ok=True)

# Initialize database
def init_db():
    """Initialize SQLite database for users"""
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
    
    # Create default users if they don't exist
    c.execute('SELECT COUNT(*) FROM users')
    if c.fetchone()[0] == 0:
        # Admin user
        admin_password = hashlib.sha256('admin123'.encode()).hexdigest()
        c.execute('''
            INSERT INTO users (username, password_hash, full_name)
            VALUES (?, ?, ?)
        ''', ('admin', admin_password, 'Administrator'))
        
        # Patient users (2 conturi pacient)
        patient_password1 = hashlib.sha256('pacient123'.encode()).hexdigest()
        patient_password2 = hashlib.sha256('pacient456'.encode()).hexdigest()
        
        patients = [
            ('pacient1', patient_password1, 'Pacient 1'),
            ('pacient2', patient_password2, 'Pacient 2')
        ]
        
        for username, password, full_name in patients:
            c.execute('''
                INSERT INTO users (username, password_hash, full_name)
                VALUES (?, ?, ?)
            ''', (username, password, full_name))
    
    conn.commit()
    conn.close()

init_db()

def hash_password(password):
    """Hash a password"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password, password_hash):
    """Verify a password"""
    return hash_password(password) == password_hash

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def convert_audio_to_text(audio_file_path):
    """Convert audio file to text using SpeechRecognition"""
    try:
        # Convert to WAV if needed (SpeechRecognition works best with WAV)
        temp_wav_path = None
        try:
            # Check file extension
            file_ext = audio_file_path.rsplit('.', 1)[1].lower() if '.' in audio_file_path else ''
            
            if file_ext != 'wav':
                # Convert to WAV using pydub
                audio = AudioSegment.from_file(audio_file_path)
                temp_wav_path = audio_file_path.rsplit('.', 1)[0] + '_converted.wav'
                audio.export(temp_wav_path, format="wav")
                audio_file_path = temp_wav_path
        except Exception as conv_error:
            # If conversion fails, try direct processing
            pass
        
        recognizer = sr.Recognizer()
        
        # Handle different audio formats
        with sr.AudioFile(audio_file_path) as source:
            # Adjust for ambient noise
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.record(source)
        
        # Try to recognize speech using Google Speech Recognition
        try:
            text = recognizer.recognize_google(audio, language='ro-RO')
            
            # Clean up temporary file if created
            if temp_wav_path and os.path.exists(temp_wav_path):
                try:
                    os.remove(temp_wav_path)
                except:
                    pass
            
            return {'success': True, 'text': text}
        except sr.UnknownValueError:
            # Clean up temporary file if created
            if temp_wav_path and os.path.exists(temp_wav_path):
                try:
                    os.remove(temp_wav_path)
                except:
                    pass
            return {'success': False, 'error': 'Nu s-a putut recunoaște vorbirea din audio'}
        except sr.RequestError as e:
            # Clean up temporary file if created
            if temp_wav_path and os.path.exists(temp_wav_path):
                try:
                    os.remove(temp_wav_path)
                except:
                    pass
            return {'success': False, 'error': f'Eroare la serviciul de recunoaștere: {str(e)}'}
    except Exception as e:
        return {'success': False, 'error': f'Eroare la procesarea audio: {str(e)}'}

def format_result(result):
    """Format result to show only the 4 required fields by parsing the generated text"""
    import re
    
    # Extract generated_text from result
    generated_text = ""
    if isinstance(result, dict):
        generated_text = result.get("generated_text", "")
    elif isinstance(result, str):
        generated_text = result
    
    if not generated_text:
        return {
            "boala": "Nu a fost identificată",
            "tratament_recomandat": ["Nu sunt recomandate medicamente"],
            "investigatii_suplimentare": ["Nu sunt recomandate investigații"],
            "recomandari_suplimentare": ["Nu sunt recomandări suplimentare"]
        }
    
    # Parse the text format: "Boala: ... Tratament recomandat: ... Investigații suplimentare: ... Recomandări suplimentare: ..."
    
    # Extract Boala: text after "Boala:" until next field or end
    boala_match = re.search(r'Boala:\s*([^.]*?)(?:\s*\.|$)', generated_text, re.IGNORECASE)
    boala = boala_match.group(1).strip() if boala_match else ""
    
    # Extract Tratament recomandat: text after "Tratament recomandat:" until next field
    tratament_match = re.search(r'Tratament\s+recomandat:\s*([^.]*?)(?:\s*\.|$)', generated_text, re.IGNORECASE)
    tratament_text = tratament_match.group(1).strip() if tratament_match else ""
    # Split by comma and clean
    tratament_list = [item.strip() for item in tratament_text.split(',') if item.strip()] if tratament_text else []
    
    # Extract Investigații suplimentare: text after "Investigații suplimentare:" until next field
    investigatii_match = re.search(r'Investigații\s+suplimentare:\s*([^.]*?)(?:\s*\.|$)', generated_text, re.IGNORECASE)
    investigatii_text = investigatii_match.group(1).strip() if investigatii_match else ""
    # Split by comma and clean
    investigatii_list = [item.strip() for item in investigatii_text.split(',') if item.strip()] if investigatii_text else []
    
    # Extract Recomandări suplimentare: text after "Recomandări suplimentare:" until end
    recomandari_match = re.search(r'Recomandări\s+suplimentare:\s*([^.]*?)(?:\s*\.|$)', generated_text, re.IGNORECASE)
    recomandari_text = recomandari_match.group(1).strip() if recomandari_match else ""
    # Split by comma and clean
    recomandari_list = [item.strip() for item in recomandari_text.split(',') if item.strip()] if recomandari_text else []
    
    return {
        "boala": boala if boala else "Nu a fost identificată",
        "tratament_recomandat": tratament_list if tratament_list else ["Nu sunt recomandate medicamente"],
        "investigatii_suplimentare": investigatii_list if investigatii_list else ["Nu sunt recomandate investigații"],
        "recomandari_suplimentare": recomandari_list if recomandari_list else ["Nu sunt recomandări suplimentare"]
    }

def save_result_to_file(user_id, input_text, result, result_type='text'):
    """Save processing result to a text file on server"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"result_{user_id}_{timestamp}.txt"
    filepath = os.path.join(app.config['RESULTS_FOLDER'], filename)
    
    try:
        # Format result for display
        formatted_result = format_result(result)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"REZULTAT PROCESARE - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"TEXT DE INTRARE:\n{input_text}\n\n")
            f.write("=" * 80 + "\n\n")
            f.write("REZULTAT PROCESARE:\n")
            f.write("=" * 80 + "\n\n")
            
            f.write(f"BOALĂ:\n{formatted_result['boala']}\n\n")
            f.write("-" * 80 + "\n\n")
            
            f.write("TRATAMENT RECOMANDAT:\n")
            for item in formatted_result['tratament_recomandat']:
                f.write(f"  • {item}\n")
            f.write("\n")
            f.write("-" * 80 + "\n\n")
            
            f.write("INVESTIGAȚII SUPLIMENTARE:\n")
            for item in formatted_result['investigatii_suplimentare']:
                f.write(f"  • {item}\n")
            f.write("\n")
            f.write("-" * 80 + "\n\n")
            
            f.write("RECOMANDĂRI SUPLIMENTARE:\n")
            for item in formatted_result['recomandari_suplimentare']:
                f.write(f"  • {item}\n")
        
        return {'success': True, 'filename': filename, 'filepath': filepath}
    except Exception as e:
        return {'success': False, 'error': f'Eroare la salvarea fișierului: {str(e)}'}

# Routes
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
            return jsonify({'error': 'Username și parolă sunt obligatorii'}), 400
        
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
            return jsonify({'error': 'Username sau parolă incorectă'}), 401
    
    # GET request - show login page
    if 'user_id' in session:
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Register new user"""
    if request.method == 'POST':
        data = request.json
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        full_name = data.get('full_name', '').strip()
        
        if not username or not password or not full_name:
            return jsonify({'error': 'Toate câmpurile sunt obligatorii'}), 400
        
        if len(password) < 6:
            return jsonify({'error': 'Parola trebuie să aibă cel puțin 6 caractere'}), 400
        
        conn = sqlite3.connect(app.config['DATABASE'])
        c = conn.cursor()
        
        # Check if username already exists
        c.execute('SELECT id FROM users WHERE username = ?', (username,))
        if c.fetchone():
            conn.close()
            return jsonify({'error': 'Username-ul este deja folosit'}), 400
        
        # Create new user
        password_hash = hash_password(password)
        try:
            c.execute('''
                INSERT INTO users (username, password_hash, full_name)
                VALUES (?, ?, ?)
            ''', (username, password_hash, full_name))
            conn.commit()
            user_id = c.lastrowid
            conn.close()
            
            # Auto-login after registration
            session['user_id'] = user_id
            session['username'] = username
            session['full_name'] = full_name
            
            return jsonify({
                'success': True,
                'user': {
                    'id': user_id,
                    'username': username,
                    'full_name': full_name
                }
            })
        except Exception as e:
            conn.close()
            return jsonify({'error': f'Eroare la crearea contului: {str(e)}'}), 500
    
    # GET request - show register page
    if 'user_id' in session:
        return redirect(url_for('index'))
    return render_template('register.html')


@app.route('/logout', methods=['POST'])
def logout():
    """Logout"""
    session.clear()
    return jsonify({'success': True})

@app.route('/api/current-user', methods=['GET'])
def get_current_user():
    """Get current authenticated user"""
    if 'user_id' not in session:
        return jsonify({'error': 'Nu sunteți autentificat'}), 401
    return jsonify({
        'id': session['user_id'],
        'username': session.get('username'),
        'full_name': session.get('full_name')
    })

@app.route('/api/process', methods=['POST'])
def process_text_or_audio():
    """Process text or audio input"""
    if 'user_id' not in session:
        return jsonify({'error': 'Autentificare necesară'}), 401
    
    user_id = session['user_id']
    input_text = None
    result_type = request.form.get('result_type', 'structured')  # 'structured' or 'text'
    
    # Check if audio file is uploaded
    if 'audio_file' in request.files:
        audio_file = request.files['audio_file']
        if audio_file.filename and allowed_file(audio_file.filename):
            # Save uploaded file temporarily
            filename = secure_filename(f"{uuid.uuid4()}_{audio_file.filename}")
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            audio_file.save(filepath)
            
            # Convert audio to text
            conversion_result = convert_audio_to_text(filepath)
            
            # Clean up uploaded file
            try:
                os.remove(filepath)
            except:
                pass
            
            if not conversion_result['success']:
                return jsonify({'error': conversion_result.get('error', 'Eroare la conversia audio')}), 400
            
            input_text = conversion_result['text']
        else:
            return jsonify({'error': 'Fișier audio invalid sau format neacceptat'}), 400
    
    # Check if text is provided directly
    elif 'text' in request.form:
        input_text = request.form.get('text', '').strip()
    
    # Check if JSON data is provided
    elif request.is_json:
        data = request.json
        input_text = data.get('text', '').strip()
        result_type = data.get('result_type', 'structured')
    
    if not input_text:
        return jsonify({'error': 'Text sau fișier audio necesar'}), 400
    
    try:
        # Process text using testModel
        structured = (result_type == 'structured')
        result = testModel.run_with_input(input_text, structured=False, model_dir=app.config['MODEL_DIR'])
        
        # Format result to show only the 4 required fields
        formatted_result = format_result(result)
        
        # Nu mai salvăm automat - doar când utilizatorul cere download
        response_data = {
            'success': True,
            'input_text': input_text,
            'result': formatted_result
        }
        
        return jsonify(response_data)
    
    except Exception as e:
        return jsonify({'error': f'Eroare la procesarea textului: {str(e)}'}), 500

@app.route('/api/save-result', methods=['POST'])
def save_result():
    """Save result to file when user clicks download button"""
    if 'user_id' not in session:
        return jsonify({'error': 'Autentificare necesară'}), 401
    
    user_id = session['user_id']
    data = request.json
    
    if not data or 'input_text' not in data or 'result' not in data:
        return jsonify({'error': 'Date incomplete'}), 400
    
    input_text = data.get('input_text', '')
    result = data.get('result', {})
    result_type = data.get('result_type', 'text')
    
    # Save result to file
    save_result_data = save_result_to_file(user_id, input_text, result, result_type=result_type)
    
    if save_result_data.get('success'):
        return jsonify({
            'success': True,
            'filename': save_result_data.get('filename'),
            'message': 'Rezultatul a fost salvat cu succes'
        })
    else:
        return jsonify({'error': save_result_data.get('error', 'Eroare la salvare')}), 500

@app.route('/api/download-result/<filename>', methods=['GET'])
def download_result(filename):
    """Download a result file"""
    if 'user_id' not in session:
        return jsonify({'error': 'Autentificare necesară'}), 401
    
    # Security: ensure filename is safe and belongs to user
    filepath = os.path.join(app.config['RESULTS_FOLDER'], secure_filename(filename))
    
    if os.path.exists(filepath) and filename.startswith(f"result_{session['user_id']}_"):
        return send_file(filepath, as_attachment=True, download_name=filename)
    else:
        return jsonify({'error': 'Fișier negăsit sau acces neautorizat'}), 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

