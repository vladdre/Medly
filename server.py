from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_file
import os
from datetime import datetime
import json
import sqlite3
import hashlib
import uuid
import testModel
import speech_recognition as sr
from werkzeug.utils import secure_filename
import tempfile
from pydub import AudioSegment

app = Flask(__name__)
app.config['SECRET_KEY'] = 'medly-secret-key-change-in-production-2024'
app.config['DATABASE'] = 'medical_records.db'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['RESULTS_FOLDER'] = 'results'
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
        # Default admin user
        admin_password = hashlib.sha256('admin123'.encode()).hexdigest()
        c.execute('''
            INSERT INTO users (username, password_hash, full_name)
            VALUES (?, ?, ?)
        ''', ('admin', admin_password, 'Administrator'))
        
        # Demo user
        demo_password = hashlib.sha256('demo123'.encode()).hexdigest()
        c.execute('''
            INSERT INTO users (username, password_hash, full_name)
            VALUES (?, ?, ?)
        ''', ('demo', demo_password, 'Utilizator Demo'))
    
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

def save_result_to_file(user_id, input_text, result, result_type='text'):
    """Save processing result to a text file on server"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"result_{user_id}_{timestamp}.txt"
    filepath = os.path.join(app.config['RESULTS_FOLDER'], filename)
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(f"Rezultat procesare - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"Text de intrare:\n{input_text}\n\n")
            f.write("=" * 80 + "\n\n")
            f.write("Rezultat procesare:\n")
            
            if result_type == 'structured':
                f.write(json.dumps(result, ensure_ascii=False, indent=4))
            else:
                if isinstance(result, dict):
                    f.write(json.dumps(result, ensure_ascii=False, indent=4))
                else:
                    f.write(str(result))
        
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

@app.route('/demo-login', methods=['POST'])
def demo_login():
    """Login with demo account"""
    conn = sqlite3.connect(app.config['DATABASE'])
    c = conn.cursor()
    c.execute('SELECT id, username, password_hash, full_name FROM users WHERE username = ?', ('demo',))
    user = c.fetchone()
    conn.close()
    
    if user:
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
        return jsonify({'error': 'Contul demo nu există'}), 404

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
        result = testModel.run_with_input(input_text, structured=False)
        
        # Save result to file
        save_result = save_result_to_file(user_id, input_text, result, result_type='structured' if structured else 'text')
        
        response_data = {
            'success': True,
            'input_text': input_text,
            'result': result,
            'file_saved': save_result.get('success', False),
            'filename': save_result.get('filename') if save_result.get('success') else None
        }
        
        return jsonify(response_data)
    
    except Exception as e:
        return jsonify({'error': f'Eroare la procesarea textului: {str(e)}'}), 500

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

