# Medly - Sistem Medical AI

Server Flask complet cu autentificare, procesare text/audio și integrare model ML.

## Instalare

1. Instalați dependențele:
```bash
pip install -r requirements.txt
```

2. Asigurați-vă că aveți modelul antrenat în directorul `finetuned_t5_model/`

3. Pentru conversia audio, instalați `ffmpeg`:
```bash
sudo apt-get install ffmpeg  # Linux/WSL
# sau
brew install ffmpeg  # macOS
```

## Rulare

Porniți serverul:
```bash
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

2. **Procesare Audio**:
   - Selectați tab-ul "Audio"
   - Click pentru a selecta un fișier audio (WAV, MP3, M4A, FLAC, OGG, WEBM)
   - Click pe "Procesează"
   - Audio-ul va fi convertit automat în text și apoi procesat

### Rezultate

- Rezultatele procesării vor fi afișate în format JSON structurat
- Rezultatele sunt salvate automat în directorul `results/` pe server
- Puteți descărca rezultatul folosind butonul "Descarcă Rezultatul"

## Structura Proiectului

```
MedlyFinal/
├── server.py              # Server Flask principal
├── testModel.py           # Model ML pentru procesare
├── requirements.txt       # Dependențe Python
├── templates/
│   ├── login.html         # Pagină login
│   ├── register.html      # Pagină înregistrare
│   └── index.html         # Pagină principală
├── uploads/               # Fișiere audio încărcate (temporare)
├── results/               # Rezultate procesare salvate
└── finetuned_t5_model/   # Model antrenat (trebuie adăugat)
```

## Note

- Conversia audio folosește Google Speech Recognition API (necesită conexiune la internet)
- Rezultatele sunt salvate cu nume unic bazat pe user_id și timestamp
- Toate fișierele audio încărcate sunt șterse după procesare
- Parolele sunt hash-uite folosind SHA-256

