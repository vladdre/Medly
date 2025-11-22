# Medly - Sistem Medical AI

Server Flask complet cu autentificare, procesare text/audio și integrare model ML.

## Structura Proiectului

```
MedlyFinal/
├── backend/              # Cod backend (Python)
│   ├── server.py        # Server Flask principal
│   └── testModel.py     # Model ML pentru procesare
│
├── frontend/            # Interfață utilizator
│   ├── templates/       # Template-uri HTML
│   │   ├── index.html
│   │   ├── login.html
│   │   └── register.html
│   └── static/          # Fișiere statice (CSS, JS)
│
├── data/                # Date și fișiere generate
│   ├── models/         # Model ML antrenat
│   │   └── finetuned_t5_model/
│   ├── uploads/        # Fișiere audio temporare
│   ├── results/        # Rezultate procesare salvate
│   └── medical_records.db  # Baza de date SQLite
│
├── config/              # Configurație și documentație
│   ├── requirements.txt
│   └── README.md
│
└── run.py              # Script de pornire
```

## Instalare

1. Instalați dependențele:
```bash
pip install -r config/requirements.txt
```

2. Asigurați-vă că aveți modelul antrenat în `data/models/finetuned_t5_model/`

3. Pentru conversia audio, instalați `ffmpeg`:
```bash
sudo apt-get install ffmpeg  # Linux/WSL
# sau
brew install ffmpeg  # macOS
```

## Rulare

Porniți serverul:
```bash
python run.py
```

Sau direct din backend:
```bash
cd backend
python server.py
```

Serverul va rula pe `http://localhost:5000`

## Utilizare

### Autentificare

1. **Cont Demo**: 
   - Username: `demo`
   - Parolă: `demo123`
   - Click pe butonul "Cont Demo" pentru autentificare rapidă

2. **Creare Cont Nou**:
   - Accesați linkul "Creați unul aici" de pe pagina de login
   - Completați formularul de înregistrare

3. **Login Normal**:
   - Introduceți username și parolă
   - Click pe "Autentificare"

### Procesare Text sau Audio

1. **Procesare Text**:
   - Selectați tab-ul "Text"
   - Introduceți textul în câmpul de text
   - Click pe "Procesează"

2. **Procesare Audio (înregistrare vocală)**:
   - Selectați tab-ul "Audio"
   - Click pe "Începe Înregistrarea"
   - Vorbiți - textul va apărea în timp real
   - Click pe "Oprește" când terminați
   - Click pe "Procesează"

### Rezultate

- Rezultatele procesării vor fi afișate în format JSON structurat
- Rezultatele sunt salvate automat în directorul `data/results/` pe server
- Puteți descărca rezultatul folosind butonul "Descarcă Rezultatul"

## Note

- Conversia audio folosește Web Speech API din browser (necesită Chrome sau Edge)
- Rezultatele sunt salvate cu nume unic bazat pe user_id și timestamp
- Parolele sunt hash-uite folosind SHA-256
- Modelul ML folosește T5 pentru generarea de fișe medicale structurate

## Dezvoltare

- **Backend**: Python 3.8+, Flask, PyTorch, Transformers
- **Frontend**: HTML5, CSS3, JavaScript (Web Speech API)
- **Database**: SQLite
- **ML Model**: T5 (Text-to-Text Transfer Transformer)
