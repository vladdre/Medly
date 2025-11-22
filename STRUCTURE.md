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
│   └── 📁 static/          # Fișiere statice (CSS, JS, imagini)
│
├── 📁 data/                # Date și fișiere generate
│   ├── 📁 models/         # Model ML antrenat
│   │   └── finetuned_t5_model/  # Model T5 pentru procesare
│   ├── 📁 uploads/        # Fișiere audio temporare (șterse după procesare)
│   ├── 📁 results/        # Rezultate procesare salvate
│   └── medical_records.db # Baza de date SQLite cu utilizatori
│
├── 📁 config/              # Configurație și documentație
│   ├── requirements.txt   # Dependențe Python
│   └── README.md          # Documentație completă
│
├── run.py                  # Script de pornire server
├── .gitignore             # Fișiere ignorate de git
└── STRUCTURE.md           # Acest fișier
```

## Descriere Directoare

### backend/
Conține toată logica serverului:
- **server.py**: Server Flask cu endpoint-uri pentru autentificare, procesare text/audio
- **testModel.py**: Integrare cu modelul ML pentru procesare text medical

### frontend/
Conține interfața utilizatorului:
- **templates/**: Template-uri HTML cu JavaScript pentru funcționalități
- **static/**: Fișiere CSS, JS, imagini (dacă sunt necesare)

### data/
Conține toate datele:
- **models/**: Model ML antrenat (T5)
- **uploads/**: Fișiere audio temporare
- **results/**: Rezultate procesare salvate
- **medical_records.db**: Baza de date cu utilizatori

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
