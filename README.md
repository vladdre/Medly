# Medly

**Medly** - Un sistem inteligent de analiză a simptomelor medicale și procesare automată a conversațiilor doctor-pacient, construit cu Flask și JavaScript.

## Caracteristici

- 🎤 **Procesare Conversații Vocale**: Înregistrare și procesare automată a conversațiilor doctor-pacient
- 🔍 **Analiză Inteligentă a Simptomelor**: Analiză bazată pe simptome și evaluare a riscului
- 📋 **Generare Automată de Documente Medicale**:
  - Sumare medicale structurate
  - Note clinice complete
  - Rețete medicale
- 🏥 **Extragere Informații Medicale**:
  - Identificare automată a bolilor și coduri ICD-10
  - Extragere medicamente cu dozaj
  - Identificare investigații recomandate
  - Recomandări personalizate
- 💾 **Stocare Istoric Medical**: Baza de date SQLite pentru înregistrări medicale
- 🎨 Interfață modernă și prietenoasă
- ⚡ API REST pentru integrare
- 📱 Design responsive

## Instalare

1. Instalați dependențele:
```bash
pip install -r requirements.txt
```

2. Rulați aplicația:
```bash
python app.py
```

3. Deschideți browserul la:
```
http://localhost:5000
```

## Structura Proiectului

```
medical_ai_system/
├── app.py                 # Backend Flask cu API endpoints
├── medical_nlp.py         # Modul NLP pentru procesare conversații
├── medical_records.db     # Baza de date SQLite (generată automat)
├── templates/
│   └── index.html        # Interfață principală cu taburi
├── static/
│   ├── css/
│   │   └── style.css     # Stiluri
│   └── js/
│       └── app.js        # Logica frontend (voice, tabs, etc.)
├── requirements.txt      # Dependențe Python
└── README.md            # Documentație
```

## API Endpoints

### `GET /api/symptoms`
Returnează lista de simptome disponibile.

### `POST /api/analyze`
Analizează simptomele și returnează posibile condiții medicale.

**Request Body:**
```json
{
  "symptoms": ["fever", "cough"],
  "age": 35,
  "existing_conditions": ["diabet"]
}
```

### `POST /api/process-conversation`
Procesează conversația doctor-pacient și generează documente medicale structurate.

**Request Body:**
```json
{
  "conversation": "Doamnă Răduță, în urma investigațiilor, am stabilit că aveți boală coronariană. Vă recomand să începeți tratament cu Aspirină și statine..."
}
```

**Response:**
```json
{
  "success": true,
  "record_id": 1,
  "structured_data": {
    "boala": "Boli coronariene",
    "cod_ICD": "I25",
    "nume_pacient": "Răduță Mariana",
    "varsta": 58,
    "sex": "Feminin",
    "istoric_medical": "Fumat, colesterol ridicat",
    "medicamente_recomandate": [
      {
        "nume": "Aspirină",
        "doza": "100 mg",
        "administrare": "1 comprimat pe zi"
      }
    ],
    "investigatii_recomandate": ["Ecocardiogramă", "Test de colesterol"],
    "recomandari_suplimentare": ["Exerciții fizice", "Dieta săracă în grăsimi"]
  },
  "clinical_note": "NOTĂ CLINICĂ\n...",
  "prescription": "REȚETĂ MEDICALĂ\n..."
}
```

### `GET /api/records`
Returnează lista cu toate înregistrările medicale.

### `GET /api/records/<id>`
Returnează o înregistrare medicală specifică.

### `GET /api/health`
Verifică starea serviciului.

## ⚠️ Disclaimer

Acest sistem este doar pentru scopuri educaționale și informaționale. **NU înlocuiește consultul medical profesional.** Consultați întotdeauna un medic pentru diagnostic și tratament adecvat.

## Funcționalități Implementate

✅ Procesare automată a conversațiilor doctor-pacient
✅ Extragere informații medicale (boală, medicamente, investigații)
✅ Generare automată de note clinice și rețete
✅ Mapare coduri ICD-10
✅ Stocare în baza de date SQLite
✅ Interfață cu înregistrare vocală (Web Speech API)
✅ Istoric medical cu vizualizare înregistrări

## Dezvoltare Viitoare

- Integrare cu modele ML avansate (GPT, BERT medical)
- Export rapoarte PDF
- Sistem de autentificare pentru medici
- Integrare cu servicii medicale externe
- Suport pentru mai multe limbi
- Analiză sentiment și ton în conversații
- Notificări și follow-up automat

## Licență

Acest proiect este creat pentru scopuri educaționale.

