# Structura Proiectului Medly

## Organizare Fișiere

```
MedlyFinal/
│
├── 📁 backend/              # Cod backend (Python/Flask)
│   ├── server.py           # Server Flask principal cu toate endpoint-urile
│   └── testModel.py        # Model ML pentru procesare text medical
│
├── 📁 frontend/             # Interfață utilizator (HTML/CSS/JS)
│   ├── 📁 templates/       # Template-uri HTML
│   │   ├── index.html      # Pagină principală cu procesare text/audio
│   │   ├── login.html      # Pagină autentificare
│   │   └── register.html   # Pagină înregistrare
│   └── 📁 static/          # Fișiere statice (CSS, JS, imagini) - opțional
│
├── 📁 data/                # Date și fișiere generate
│   ├── 📁 models/         # Model ML antrenat și fișiere de antrenare
│   │   ├── finetuned_t5_model/  # Model T5 pentru procesare
│   │   │   ├── config.json, model.safetensors, tokenizer files
│   │   │   └── checkpoint-*/    # Checkpoint-uri de antrenare (opțional)
│   │   ├── data.json      # Date de antrenare pentru model
│   │   └── training.py    # Script pentru antrenare model
│   ├── 📁 uploads/        # Fișiere audio temporare (șterse după procesare)
│   │   └── .gitkeep       # Fișier pentru a menține directorul în git
│   ├── 📁 results/        # Rezultate procesare salvate (Note Clinice și Rețete)
│   │   └── .gitkeep       # Fișier pentru a menține directorul în git
│   └── medical_records.db # Baza de date SQLite cu utilizatori
│
├── 📁 config/              # Configurație și documentație
│   ├── requirements.txt   # Dependențe Python
│   └── README.md          # Documentație completă
│
├── run.py                  # Script de pornire server
├── .gitignore             # Fișiere ignorate de git
├── STRUCTURE.md           # Acest fișier
└── README.md              # Documentație principală
```

## Descriere Directoare

### backend/
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

### frontend/
Conține interfața utilizatorului:
- **templates/**: Template-uri HTML cu JavaScript embedded pentru funcționalități
  - `index.html`: Pagină principală cu procesare text/audio și afișare rezultate
  - `login.html`: Formular autentificare
  - `register.html`: Formular înregistrare
- **static/**: Fișiere CSS, JS, imagini (opțional - poate fi gol)

### data/
Conține toate datele:
- **models/**: 
  - `finetuned_t5_model/`: Model ML antrenat (T5) cu fișiere de configurare, weights și tokenizer
    - Poate conține checkpoint-uri de antrenare (checkpoint-500, checkpoint-759, etc.)
  - `data.json`: Date de antrenare pentru model
  - `training.py`: Script pentru antrenare model
- **uploads/**: Fișiere audio temporare (șterse automat după procesare)
  - `.gitkeep`: Fișier pentru a menține directorul în git
- **results/**: Rezultate procesare salvate (Notă Clinică și Rețetă Medicală)
  - `.gitkeep`: Fișier pentru a menține directorul în git
- **medical_records.db**: Baza de date SQLite cu utilizatori

### config/
Configurație și documentație:
- **requirements.txt**: Dependențe Python
- **README.md**: Documentație completă

## Rulare

```bash
# Din directorul root
python run.py

# Sau din backend
cd backend
python server.py
```

## Note

- Toate căile relative sunt configurate automat
- Serverul pornește pe http://localhost:5000
- Baza de date se creează automat la prima rulare
