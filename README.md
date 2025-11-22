# 🏥 Medly - Sistem Medical AI

<div align="center">

**Sistem inteligent de procesare și generare automată a documentelor medicale**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0.0-green.svg)](https://flask.palletsprojects.com/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0+-orange.svg)](https://pytorch.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

</div>

---

## 📋 Cuprins

- [Despre Proiect](#-despre-proiect)
- [💡 Ideea Proiectului](#-ideea-proiectului)
- [✨ Caracteristici](#-caracteristici)
- [🛠️ Tehnologii Folosite](#️-tehnologii-folosite)
- [📁 Structura Proiectului](#-structura-proiectului)
- [🚀 Instalare și Setup](#-instalare-și-setup)
- [▶️ Cum se Rulează](#️-cum-se-rulează)
- [📦 Requirements](#-requirements)
- [👤 Utilizare](#-utilizare)
- [🔧 Configurare](#-configurare)
- [📝 API Endpoints](#-api-endpoints)
- [🤝 Contribuții](#-contribuții)

---

## 🎯 Despre Proiect

**Medly** este un sistem medical inteligent care automatizează procesarea consultațiilor medicale și generarea documentelor medicale standardizate. Sistemul utilizează inteligență artificială pentru a analiza text sau audio medical și a genera automat **Notă Clinică** și **Rețetă Medicală** conform standardelor medicale.

Proiectul a fost dezvoltat pentru a simplifica și accelera procesul de documentare medicală, permițând medicilor să se concentreze pe pacienți în loc de birocrație.

---

## 💡 Ideea Proiectului

În domeniul medical, documentarea consultațiilor este un proces esențial dar consumator de timp. Medicii trebuie să completeze manual fișe medicale, rețete și note clinice, proces care poate lua o parte semnificativă din timpul de consultație.

**Medly** rezolvă această problemă prin:

1. **Procesare automată**: Sistemul primește descrierea simptomelor sau consultației (text sau audio)
2. **Analiză inteligentă**: Un model de machine learning (T5 fine-tuned) analizează input-ul și identifică:
   - Boala/diagnosticul
   - Tratamentul recomandat
   - Investigațiile necesare
   - Recomandările pentru pacient
3. **Generare documente**: Sistemul generează automat două documente medicale:
   - **Notă Clinică**: Document complet cu diagnostic, tratament, investigații și recomandări
   - **Rețetă Medicală**: Rețetă standardizată cu medicamente, doze și administrare

Sistemul permite editarea manuală a documentelor generate și salvarea lor ca fișiere separate, oferind flexibilitate completă medicilor.

---

## ✨ Caracteristici

### 🎤 Input Flexibil
- **Text manual**: Introducere directă a textului consultației
- **Audio live**: Înregistrare vocală în timp real folosind microfonul browserului
- **Recunoaștere vocală**: Conversie automată audio → text folosind Google Speech Recognition API

### 🤖 Procesare Inteligentă
- **Model T5 fine-tuned**: Model de machine learning specializat pentru text medical românesc
- **Extragere automată**: Identificare automată a diagnosticului, tratamentului, investigațiilor și recomandărilor
- **Folosire strictă a input-ului**: Medicamentele și dozele sunt extrase exact din textul introdus

### 📄 Generare Documente
- **Notă Clinică**: Document complet cu toate informațiile medicale relevante
- **Rețetă Medicală**: Rețetă standardizată cu medicamente, doze și administrare
- **Formatare profesională**: Documente formatate conform standardelor medicale

### ✏️ Editare și Salvare
- **Editare inline**: Posibilitate de editare a ambelor documente direct în interfață
- **Salvare separată**: Fiecare document poate fi salvat ca fișier text separat
- **Descărcare individuală**: Download independent pentru Notă Clinică și Rețetă Medicală

### 🔐 Securitate
- **Autentificare utilizatori**: Sistem de login/register cu hash-uri SHA-256
- **Sesiuni securizate**: Gestionare sesiuni Flask cu secret key
- **Validare input**: Verificare și sanitizare a tuturor input-urilor

---

## 🛠️ Tehnologii Folosite

### Backend
- **Python 3.8+**: Limbajul principal de programare
- **Flask 3.0.0**: Framework web lightweight pentru API și routing
- **PyTorch 2.0+**: Framework pentru deep learning
- **Transformers 4.30+**: Biblioteca Hugging Face pentru modele NLP (T5)
- **SQLite3**: Baza de date pentru gestionarea utilizatorilor
- **SpeechRecognition 3.10.0**: Biblioteca pentru recunoașterea vocală
- **pydub 0.25.1**: Procesare și conversie fișiere audio

### Frontend
- **HTML5**: Structura interfeței
- **CSS3**: Stilizare modernă cu gradient-uri și animații
- **JavaScript (Vanilla)**: Logica client-side și interacțiunea cu API-ul
- **Web Speech API**: Recunoaștere vocală în browser (Chrome/Edge)

### Machine Learning
- **T5 (Text-To-Text Transfer Transformer)**: Model de bază pentru generare text
- **Fine-tuning**: Model antrenat specific pentru domeniul medical românesc
- **Beam Search**: Algoritm de decodare pentru generare text optimă

---

## 📁 Structura Proiectului

```
MedlyFinal/
│
├── 📁 backend/                    # Cod backend (Python/Flask)
│   ├── server.py                 # Server Flask principal cu toate endpoint-urile
│   └── testModel.py              # Integrare cu modelul ML pentru procesare text medical
│
├── 📁 frontend/                   # Interfață utilizator (HTML/CSS/JS)
│   ├── 📁 templates/             # Template-uri HTML
│   │   ├── index.html           # Pagină principală cu procesare text/audio
│   │   ├── login.html           # Pagină autentificare
│   │   └── register.html        # Pagină înregistrare
│   └── 📁 static/               # Fișiere statice (CSS, JS, imagini)
│
├── 📁 data/                      # Date și fișiere generate
│   ├── 📁 models/               # Model ML antrenat
│   │   └── finetuned_t5_model/  # Model T5 pentru procesare
│   ├── 📁 uploads/              # Fișiere audio temporare (șterse după procesare)
│   ├── 📁 results/              # Rezultate procesare salvate
│   └── medical_records.db       # Baza de date SQLite cu utilizatori
│
├── 📁 config/                    # Configurație și documentație
│   ├── requirements.txt         # Dependențe Python
│   └── README.md                # Documentație suplimentară
│
├── run.py                        # Script de pornire server
├── STRUCTURE.md                  # Documentație structură proiect
└── README.md                     # Acest fișier
```

### Descriere Directoare

#### `backend/`
Conține toată logica serverului:
- **server.py**: Server Flask cu endpoint-uri pentru:
  - Autentificare (login/register/logout)
  - Procesare text/audio
  - Generare Notă Clinică și Rețetă Medicală
  - Salvare și descărcare documente
- **testModel.py**: Integrare cu modelul ML, funcții pentru:
  - Încărcare model T5
  - Generare text structurat
  - Parsare și formatare rezultate

#### `frontend/`
Conține interfața utilizatorului:
- **templates/**: Template-uri HTML cu JavaScript embedded
  - `index.html`: Interfață principală cu input text/audio și afișare rezultate
  - `login.html`: Formular autentificare
  - `register.html`: Formular înregistrare
- **static/**: Fișiere statice (CSS, JS, imagini) - opțional

#### `data/`
Conține toate datele:
- **models/**: Model ML antrenat (T5 fine-tuned)
- **uploads/**: Fișiere audio temporare (șterse automat după procesare)
- **results/**: Rezultate procesare salvate (Notă Clinică și Rețetă Medicală)
- **medical_records.db**: Baza de date SQLite cu utilizatori

---

## 🚀 Instalare și Setup

### Cerințe Preliminare

- **Python 3.8** sau mai nou
- **pip** (Python package manager)
- **Git** (opțional, pentru clonare repository)

### Pași de Instalare

1. **Clonează sau descarcă proiectul**
   ```bash
   git clone <repository-url>
   cd MedlyFinal
   ```

2. **Creează un environment virtual (recomandat)**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Instalează dependențele**
   ```bash
   pip install -r config/requirements.txt
   ```

4. **Verifică structura directoarelor**
   ```bash
   # Asigură-te că există directoarele necesare
   mkdir -p data/uploads
   mkdir -p data/results
   mkdir -p data/models
   ```

5. **Plasează modelul ML**
   - Modelul T5 fine-tuned trebuie să fie în `data/models/finetuned_t5_model/`
   - Dacă nu ai modelul, va trebui să îl antrenezi sau să folosești un model pre-antrenat

---

## ▶️ Cum se Rulează

### Metoda 1: Script de pornire (Recomandat)

```bash
python run.py
```

### Metoda 2: Direct din backend

```bash
cd backend
python server.py
```

### Accesare Aplicație

După pornire, aplicația va fi disponibilă la:
- **URL**: `http://localhost:5000`
- **Port**: 5000 (configurabil în `run.py` sau `server.py`)

### Mesaj de Confirmare

La pornire, vei vedea în consolă:
```
============================================================
🏥 Medly - Sistem Medical AI
============================================================
Serverul pornește pe http://localhost:5000
Apăsați Ctrl+C pentru a opri serverul
============================================================
```

---

## 📦 Requirements

### Dependențe Python

Toate dependențele sunt listate în `config/requirements.txt`:

```
Flask==3.0.0              # Framework web
Werkzeug==3.0.1           # WSGI utilities (included cu Flask)
SpeechRecognition==3.10.0  # Recunoaștere vocală
torch>=2.0.0              # PyTorch pentru deep learning
transformers>=4.30.0      # Hugging Face Transformers
pydub==0.25.1             # Procesare audio
```

### Instalare Dependențe

```bash
pip install -r config/requirements.txt
```

### Dependențe Opționale

Pentru funcționalități avansate de procesare audio:
- **ffmpeg**: Necesar pentru `pydub` pentru conversie audio
  - Windows: Descarcă de la [ffmpeg.org](https://ffmpeg.org/download.html)
  - Linux: `sudo apt-get install ffmpeg`
  - Mac: `brew install ffmpeg`

### Cerințe Sistem

- **RAM**: Minim 4GB (recomandat 8GB+ pentru model ML)
- **Spațiu disk**: Minim 2GB (pentru model și dependențe)
- **CPU**: Orice procesor modern (GPU opțional pentru procesare mai rapidă)

---

## 👤 Utilizare

### 1. Autentificare

La prima accesare, vei fi redirecționat către pagina de login.

**Conturi predefinite:**
- **Admin**: 
  - Username: `admin`
  - Parolă: `admin123`
- **Pacient 1**: 
  - Username: `pacient1`
  - Parolă: `pacient123`
- **Pacient 2**: 
  - Username: `pacient2`
  - Parolă: `pacient456`

Sau poți crea un cont nou folosind butonul "Înregistrare".

### 2. Introducere Input

După autentificare, ai două opțiuni:

#### A. Input Text
1. Selectează tab-ul "Text"
2. Introdu textul consultației în textarea
3. Apasă "Procesează"

#### B. Input Audio
1. Selectează tab-ul "Audio"
2. Apasă "Începe Înregistrarea" (permite accesul la microfon)
3. Vorbește consultația
4. Apasă "Oprește" când ai terminat
5. Apasă "Procesează"

**Notă**: Recunoașterea vocală funcționează cel mai bine în Chrome sau Edge.

### 3. Vizualizare Rezultate

După procesare, vei vedea două secțiuni:

- **📄 Notă Clinică**: Document complet cu diagnostic, tratament, investigații și recomandări
- **💊 Rețetă Medicală**: Rețetă cu medicamente, doze și administrare

### 4. Editare Documente

Pentru fiecare document:
1. Apasă butonul "✏️ Editează"
2. Modifică textul în textarea
3. Apasă "💾 Salvează" pentru a salva modificările

### 5. Descărcare Documente

Pentru fiecare document:
1. Apasă butonul "💾 Descarcă Notă Clinică" sau "💾 Descarcă Rețetă"
2. Fișierul va fi salvat automat pe computer

---

## 🔧 Configurare

### Configurare Server

Configurarea se face în `backend/server.py`:

```python
app.config['SECRET_KEY'] = 'your-secret-key'  # Schimbă în producție!
app.config['DATABASE'] = 'path/to/database.db'
app.config['UPLOAD_FOLDER'] = 'path/to/uploads'
app.config['RESULTS_FOLDER'] = 'path/to/results'
app.config['MODEL_DIR'] = 'path/to/model'
```

### Configurare Port

În `run.py` sau `server.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5000)  # Schimbă port-ul aici
```

### Configurare Model ML

Modelul trebuie să fie în `data/models/finetuned_t5_model/` și să conțină:
- `config.json`: Configurație model
- `pytorch_model.bin`: Weights model
- `tokenizer.json`: Tokenizer
- `vocab.json`: Vocabular

---

## 📝 API Endpoints

### Autentificare

- `GET /` - Pagină principală (redirect la login dacă neautentificat)
- `GET /login` - Pagină login
- `POST /login` - Autentificare utilizator
- `GET /register` - Pagină înregistrare
- `POST /register` - Înregistrare utilizator nou
- `POST /logout` - Deconectare

### API

- `GET /api/current-user` - Obține utilizatorul curent autentificat
- `POST /api/process` - Procesează text sau audio și generează documente
- `POST /api/save-nota-clinica` - Salvează Notă Clinică ca fișier
- `POST /api/save-reteta-mediala` - Salvează Rețetă Medicală ca fișier
- `GET /api/download-result/<filename>` - Descarcă un fișier salvat

### Exemplu Request

```bash
# Procesare text
curl -X POST http://localhost:5000/api/process \
  -H "Content-Type: application/json" \
  -d '{"text": "Pacient cu tuse seacă și febră..."}'
```

---

## 🎨 Caracteristici Interfață

- **Design modern**: Interfață clean cu gradient-uri verzi (tema medicală)
- **Responsive**: Funcționează pe desktop și mobile
- **Feedback vizual**: Loading indicators, mesaje de succes/eroare
- **Editare inline**: Editare directă a documentelor fără refresh
- **Descărcare rapidă**: Download instant al documentelor

---

## 🔒 Securitate

### Măsuri Implementate

- **Hash-uri parolă**: SHA-256 pentru stocare securizată
- **Sesiuni Flask**: Gestionare sesiuni securizate
- **Validare input**: Sanitizare și validare a tuturor input-urilor
- **Secure filenames**: Folosire `secure_filename` pentru upload-uri
- **User isolation**: Fiecare utilizator vede doar propriile fișiere

### Recomandări pentru Producție

- Schimbă `SECRET_KEY` cu o valoare aleatoare puternică
- Folosește HTTPS
- Implementează rate limiting
- Adaugă logging pentru audit
- Folosește o bază de date mai robustă (PostgreSQL)

---

## 🤝 Contribuții

Contribuțiile sunt binevenite! Pentru a contribui:

1. Fork repository-ul
2. Creează un branch pentru feature (`git checkout -b feature/AmazingFeature`)
3. Commit modificările (`git commit -m 'Add some AmazingFeature'`)
4. Push la branch (`git push origin feature/AmazingFeature`)
5. Deschide un Pull Request

---

## 📄 Licență

Acest proiect este licențiat sub licența MIT - vezi fișierul [LICENSE](LICENSE) pentru detalii.

---

## 👨‍💻 Autor

Dezvoltat pentru automatizarea procesului de documentare medicală.

---

## 🙏 Mulțumiri

- **Hugging Face** pentru biblioteca Transformers
- **Google** pentru Speech Recognition API
- **Flask** pentru framework-ul web lightweight
- Comunitatea open-source pentru librăriile folosite

---

<div align="center">

**Făcut cu ❤️ pentru medicină**

[⬆ Înapoi sus](#-medly---sistem-medical-ai)

</div>

