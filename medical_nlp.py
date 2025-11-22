"""
Medical NLP Processing Module
Extracts medical information from doctor-patient conversations
"""
import re
from datetime import datetime
from typing import Dict, List, Optional

class MedicalNLPProcessor:
    def __init__(self):
        # ICD-10 Code Database (Romanian medical terms)
        self.icd10_codes = {
            'boală coronariană': {'code': 'I25', 'name': 'Boli coronariene'},
            'hipertensiune': {'code': 'I10', 'name': 'Hipertensiune arterială esențială'},
            'diabet': {'code': 'E11', 'name': 'Diabet zaharat tip 2'},
            'diabet tip 2': {'code': 'E11', 'name': 'Diabet zaharat tip 2'},
            'diabet tip 1': {'code': 'E10', 'name': 'Diabet zaharat tip 1'},
            'astm': {'code': 'J45', 'name': 'Astm'},
            'astm bronșic': {'code': 'J45', 'name': 'Astm bronșic'},
            'astm bronșică': {'code': 'J45', 'name': 'Astm bronșic'},
            'bronșită': {'code': 'J40', 'name': 'Bronșită'},
            'pneumonie': {'code': 'J18', 'name': 'Pneumonie'},
            'gastrită': {'code': 'K29', 'name': 'Gastrită'},
            'ulcer': {'code': 'K25', 'name': 'Ulcer gastric'},
            'artrită': {'code': 'M19', 'name': 'Artrită'},
            'osteoporoză': {'code': 'M81', 'name': 'Osteoporoză'},
            'anemie': {'code': 'D50', 'name': 'Anemie'},
            'depresie': {'code': 'F32', 'name': 'Episod depresiv'},
            'anxietate': {'code': 'F41', 'name': 'Tulburări de anxietate'},
        }
        
        # Medication patterns
        self.medication_patterns = {
            'aspirină': {'name': 'Aspirină', 'common_dose': '100 mg'},
            'aspirina': {'name': 'Aspirină', 'common_dose': '100 mg'},
            'statine': {'name': 'Statine', 'common_dose': '20-40 mg'},
            'atorvastatin': {'name': 'Atorvastatin', 'common_dose': '20-40 mg'},
            'simvastatin': {'name': 'Simvastatin', 'common_dose': '20-40 mg'},
            'metformin': {'name': 'Metformin', 'common_dose': '500-1000 mg'},
            'insulină': {'name': 'Insulină', 'common_dose': 'variabilă'},
            'paracetamol': {'name': 'Paracetamol', 'common_dose': '500-1000 mg'},
            'ibuprofen': {'name': 'Ibuprofen', 'common_dose': '400-600 mg'},
            'amoxicilină': {'name': 'Amoxicilină', 'common_dose': '500 mg'},
            'amoxicilina': {'name': 'Amoxicilină', 'common_dose': '500 mg'},
            'salbutamol': {'name': 'Salbutamol', 'common_dose': '100-200 mcg'},
            'beclometazonă': {'name': 'Beclometazonă', 'common_dose': '100-200 mcg'},
            'beclometazona': {'name': 'Beclometazonă', 'common_dose': '100-200 mcg'},
            'ventolin': {'name': 'Salbutamol', 'common_dose': '100-200 mcg'},
            'budesonid': {'name': 'Budesonid', 'common_dose': '200-400 mcg'},
            'fluticazonă': {'name': 'Fluticazonă', 'common_dose': '100-250 mcg'},
        }
        
        # Investigation patterns
        self.investigation_keywords = {
            'ecocardiogramă': 'Ecocardiogramă',
            'ecocardiograma': 'Ecocardiogramă',
            'ecg': 'ECG',
            'electrocardiogramă': 'ECG',
            'test de colesterol': 'Test de colesterol',
            'colesterol': 'Test de colesterol',
            'glicemie': 'Test de glicemie',
            'hemogramă': 'Hemogramă',
            'radiografie': 'Radiografie',
            'rmn': 'RMN',
            'ct': 'CT',
            'tomografie': 'CT',
            'ultrasunet': 'Ultrasunet',
            'ecografie': 'Ultrasunet',
        }
        
        # Recommendation patterns
        self.recommendation_patterns = {
            'exerciții': 'Exerciții fizice',
            'exerciții fizice': 'Exerciții fizice',
            'dietă': 'Dieta săracă în grăsimi',
            'dieta': 'Dieta săracă în grăsimi',
            'dieta săracă în grăsimi': 'Dieta săracă în grăsimi',
            'renunțare la fumat': 'Renunțare la fumat',
            'fumat': 'Renunțare la fumat',
            'odihnă': 'Odihnă',
            'hidratare': 'Hidratare adecvată',
            'evitați expunerea': 'Evitare alergeni și praf',
            'evitare': 'Evitare alergeni și praf',
            'praf': 'Evitare alergeni și praf',
            'alergeni': 'Evitare alergeni și praf',
            'evitați': 'Evitare alergeni și praf',
        }
    
    def extract_patient_name(self, text: str) -> Optional[str]:
        """Extract patient name from conversation"""
        # Look for patterns like "Doamnă X", "Domnul X", "Pacientul X"
        patterns = [
            r'(?:Doamnă|Domnul|Domn|Doamna)\s+([A-ZĂÂÎȘȚ][a-zăâîșț]+(?:\s+[A-ZĂÂÎȘȚ][a-zăâîșț]+)?)',
            r'Pacient[ul]?\s+([A-ZĂÂÎȘȚ][a-zăâîșț]+(?:\s+[A-ZĂÂÎȘȚ][a-zăâîșț]+)?)',
            r'([A-ZĂÂÎȘȚ][a-zăâîșț]+\s+[A-ZĂÂÎȘȚ][a-zăâîșț]+)',  # First Last name pattern
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                name = match.group(1).strip()
                # Filter out common words that might be matched
                name_lower = name.lower()
                if (name_lower not in ['vă recomand', 'am stabilit', 'este important', 'urma', 'investigațiilor'] and
                    len(name) > 2 and  # Name should be at least 3 characters
                    not name_lower.startswith('suferiți') and
                    not name_lower.startswith('aveți')):
                    return name
        
        return None
    
    def extract_age(self, text: str) -> Optional[int]:
        """Extract patient age"""
        patterns = [
            r'(?:vârstă|varsta|ani)\s*(?:de|:)?\s*(\d+)',
            r'(\d+)\s*(?:ani|de ani)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    age = int(match.group(1))
                    if 0 < age < 150:
                        return age
                except:
                    pass
        
        return None
    
    def extract_sex(self, text: str) -> Optional[str]:
        """Extract patient sex"""
        text_lower = text.lower()
        # Check for feminine indicators (check first, as "doamnă" is more specific)
        if re.search(r'\b(doamnă|doamna|femeie|feminin|f)\b', text_lower):
            return 'Feminin'
        # Check for masculine indicators
        elif re.search(r'\b(domn|domnul|bărbat|masculin|m)\b', text_lower):
            return 'Masculin'
        return None
    
    def extract_disease(self, text: str) -> Dict:
        """Extract disease name and ICD-10 code"""
        text_lower = text.lower()
        
        # Try to match diseases (check longer phrases first)
        sorted_diseases = sorted(self.icd10_codes.items(), key=lambda x: len(x[0]), reverse=True)
        
        for disease_key, disease_info in sorted_diseases:
            if disease_key in text_lower:
                return {
                    'boala': disease_info['name'],
                    'cod_ICD': disease_info['code']
                }
        
        # Also check for partial matches (e.g., "boală coronariană" in "Ghid de boală coronariană")
        for disease_key, disease_info in sorted_diseases:
            # Split disease key and check if all parts are present
            key_parts = disease_key.split()
            if len(key_parts) > 1:
                if all(part in text_lower for part in key_parts):
                    return {
                        'boala': disease_info['name'],
                        'cod_ICD': disease_info['code']
                    }
        
        return {'boala': None, 'cod_ICD': None}
    
    def extract_medications(self, text: str) -> List[Dict]:
        """Extract recommended medications with dosage"""
        medications = []
        text_lower = text.lower()
        found_meds = set()  # To avoid duplicates
        
        # Words that indicate we should NOT extract as medication
        exclude_words = [
            'pentru', 'a', 'să', 'vă', 'ajuta', 'reduce', 'începeți', 'respirați', 
            'mai', 'ușor', 'evitați', 'expunerea', 'la', 'praf', 'alergeni', 'care',
            'pot', 'declanșa', 'simptomele', 'wheezing', 'sifonare', 'tuse', 'dificultăți',
            'în', 'respirație', 'episoade', 'de', 'provoacă', 'cronică', 'afecțiune',
            'căilor', 'respiratorii', 'aceasta', 'este', 'o', 'investigațiilor', 'urma',
            'stabilit', 'că', 'suferiți', 'doamnă', 'domnul', 'munteanu'
        ]
        
        # Strategy 1: Extract from "tratament cu X și Y" pattern (most reliable)
        treatment_pattern = r'tratament\s+cu\s+([^,\.;]+?)(?:\s+și\s+([^,\.;]+?))?(?:\s+pentru|\.|,|$)'
        treatment_match = re.search(treatment_pattern, text_lower)
        if treatment_match:
            med1 = treatment_match.group(1).strip() if treatment_match.group(1) else None
            med2 = treatment_match.group(2).strip() if treatment_match.group(2) else None
            
            for med_text in [med1, med2]:
                if not med_text:
                    continue
                # Clean up - remove common words
                med_text = re.sub(r'\b(pentru|a|să|vă|ajuta|reduce|începeți|respirați|mai|ușor)\b', '', med_text, flags=re.IGNORECASE).strip()
                if not med_text or len(med_text) < 3:
                    continue
                
                med_text_lower = med_text.lower()
                # Check if it's not a descriptive phrase
                if any(word in med_text_lower for word in exclude_words if len(word) > 3):
                    continue
                med_name = None
                dose = None
                admin = "1 comprimat pe zi"
                
                # Check if matches known medication
                matched_known = False
                for med_key, med_info in self.medication_patterns.items():
                    if med_key in med_text_lower or med_text_lower in med_key:
                        med_name = med_info['name']
                        dose = med_info['common_dose']
                        matched_known = True
                        break
                
                # If not known, use extracted text (but only if it looks like a medication name)
                if not matched_known:
                    # Medication names are usually single words or short phrases (max 2-3 words)
                    words = med_text.split()
                    if len(words) <= 3 and not any(exclude in med_text_lower for exclude in exclude_words if len(exclude) > 4):
                        med_name = med_text.strip()
                        if med_name:
                            med_name = med_name[0].upper() + med_name[1:] if len(med_name) > 1 else med_name.upper()
                            dose = "Conform prescripției"
                
                # Extract dosage from context
                if med_name and (med_text in text or med_text_lower in text_lower):
                    med_pos = text_lower.find(med_text_lower)
                    if med_pos >= 0:
                        context_start = max(0, med_pos - 50)
                        context_end = min(len(text), med_pos + len(med_text) + 50)
                        context = text_lower[context_start:context_end]
                        
                        # Extract dosage
                        dose_patterns = [
                            r'(\d+(?:\s*-\s*\d+)?)\s*(?:mg|ml|g|mcg|miligrame|mililitri|grame)',
                            r'(\d+)\s*(?:mg|ml|g|mcg)',
                        ]
                        for dose_pattern in dose_patterns:
                            dose_match = re.search(dose_pattern, context)
                            if dose_match:
                                dose = dose_match.group(0).strip()
                                break
                
                if med_name and med_name not in found_meds:
                    found_meds.add(med_name)
                    medications.append({
                        'nume': med_name,
                        'doza': dose or "Conform prescripției",
                        'administrare': admin
                    })
        
        # Strategy 2: Check known medications in text
        for med_key, med_info in self.medication_patterns.items():
            if med_key in text_lower and med_info['name'] not in found_meds:
                found_meds.add(med_info['name'])
                med_positions = [m.start() for m in re.finditer(re.escape(med_key), text_lower)]
                
                for med_pos in med_positions:
                    context_start = max(0, med_pos - 100)
                    context_end = min(len(text), med_pos + len(med_key) + 100)
                    context = text_lower[context_start:context_end]
                    
                    # Extract dosage
                    dose_patterns = [
                        r'(\d+(?:\s*-\s*\d+)?)\s*(?:mg|ml|g|mcg|miligrame|mililitri|grame)',
                        r'(\d+)\s*(?:mg|ml|g|mcg)',
                    ]
                    dose = med_info['common_dose']
                    for dose_pattern in dose_patterns:
                        dose_match = re.search(dose_pattern, context)
                        if dose_match:
                            dose = dose_match.group(0).strip()
                            break
                    
                    # Extract administration
                    admin = "1 comprimat pe zi"
                    admin_patterns = [
                        r'(\d+)\s*(?:comprimat|pastilă|tabletă|capsulă|doză|puf)',
                        r'(\d+)\s*(?:ori|dată)\s*(?:pe|în)\s*(?:zi|săptămână)',
                    ]
                    for admin_pattern in admin_patterns:
                        admin_match = re.search(admin_pattern, context)
                        if admin_match:
                            num_match = re.search(r'(\d+)', admin_match.group(0))
                            if num_match:
                                num = num_match.group(1)
                                if 'zi' in admin_match.group(0):
                                    admin = f"{num} comprimat pe zi"
                                elif 'săptămână' in admin_match.group(0):
                                    admin = f"{num} comprimat pe săptămână"
                            break
                    
                    medications.append({
                        'nume': med_info['name'],
                        'doza': dose,
                        'administrare': admin
                    })
                    break
        
        return medications
    
    def extract_investigations(self, text: str) -> List[str]:
        """Extract recommended investigations"""
        investigations = []
        text_lower = text.lower()
        found_investigations = set()
        
        # Words that are NOT investigations
        exclude_words = [
            'tratament', 'medicament', 'cu', 'și', 'pentru', 'a', 'să', 'vă', 
            'ajuta', 'reduce', 'începeți', 'respirați', 'mai', 'ușor', 'evitați',
            'expunerea', 'la', 'praf', 'alergeni', 'care', 'pot', 'declanșa',
            'simptomele', 'wheezing', 'sifonare', 'tuse', 'dificultăți', 'în',
            'respirație', 'episoade', 'de', 'provoacă', 'cronică', 'afecțiune',
            'căilor', 'respiratorii', 'aceasta', 'este', 'o', 'stabilit', 'că',
            'suferiți', 'doamnă', 'domnul', 'munteanu', 'am', 'salbutamol',
            'beclometazonă', 'inflamația'
        ]
        
        # Strategy 1: Look for known investigation keywords
        for keyword, investigation_name in self.investigation_keywords.items():
            pattern = r'\b' + re.escape(keyword) + r'\b'
            if re.search(pattern, text_lower) and investigation_name not in found_investigations:
                found_investigations.add(investigation_name)
                investigations.append(investigation_name)
            elif keyword in text_lower and investigation_name not in found_investigations:
                found_investigations.add(investigation_name)
                investigations.append(investigation_name)
        
        # Strategy 2: Look for capitalized investigation names in original text
        investigation_capitalized = [
            'Ecocardiogramă', 'Ecocardiograma', 'ECG', 'RMN', 'CT', 
            'Ultrasunet', 'Ecografie', 'Radiografie', 'Hemogramă', 
            'Test de colesterol', 'Test de glicemie', 'Colesterol', 'Glicemie'
        ]
        for inv_name in investigation_capitalized:
            if inv_name in text and inv_name not in found_investigations:
                found_investigations.add(inv_name)
                investigations.append(inv_name)
        
        # Strategy 3: Extract from "recomand [investigatie]" pattern (only if it looks like an investigation)
        investigation_patterns = [
            r'(?:recomand|sugerez|faceți)\s+(?:o\s+)?([A-ZĂÂÎȘȚ][a-zăâîșț]+(?:\s+[a-zăâîșț]+)?)',
            r'(?:investigați|investigație|investigații|test|analiză|examen)\s+(?:de\s+)?([A-ZĂÂÎȘȚ][a-zăâîșț]+)',
        ]
        
        for pattern in investigation_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                potential_inv = match.group(1).strip()
                potential_inv_lower = potential_inv.lower()
                
                # Skip if it's not a real investigation (too many words or contains excluded words)
                words = potential_inv.split()
                if len(words) > 3 or any(exclude in potential_inv_lower for exclude in exclude_words if len(exclude) > 4):
                    continue
                
                # Check if matches known investigation
                matched_known = False
                for keyword, investigation_name in self.investigation_keywords.items():
                    if keyword in potential_inv_lower or potential_inv_lower in keyword:
                        if investigation_name not in found_investigations:
                            found_investigations.add(investigation_name)
                            investigations.append(investigation_name)
                        matched_known = True
                        break
                
                # Only add if it's a known investigation type
                # Don't add random capitalized words
        
        return investigations
    
    def extract_recommendations(self, text: str) -> List[str]:
        """Extract additional recommendations"""
        recommendations = []
        text_lower = text.lower()
        found_recommendations = set()
        
        # Strategy 1: Special patterns for common recommendations (most reliable)
        special_patterns = {
            r'\bexerciții\s+fizice\b': 'Exerciții fizice',
            r'\bprogram\s+de\s+exerciții\s+fizice\b': 'Exerciții fizice',
            r'\bprogram\s+de\s+exerciții\b': 'Exerciții fizice',
            r'\bexerciții\b': 'Exerciții fizice',
            r'\bdietă\s+săracă\s+în\s+grăsimi\b': 'Dieta săracă în grăsimi',
            r'\bdietă\s+sănătoasă\b': 'Dieta săracă în grăsimi',
            r'\bdietă\b': 'Dieta săracă în grăsimi',
            r'\brenunțare\s+la\s+fumat\b': 'Renunțare la fumat',
            r'\boprire\s+fumat\b': 'Renunțare la fumat',
            r'\bnu\s+mai\s+fumați\b': 'Renunțare la fumat',
            r'\bodihnă\b': 'Odihnă',
            r'\brest\b': 'Odihnă',
            r'\bhidratare\b': 'Hidratare adecvată',
            r'\bapă\s+multă\b': 'Hidratare adecvată',
            r'\bevitați\s+expunerea\s+la\s+praf\s+și\s+alergeni\b': 'Evitare alergeni și praf',
            r'\bevitați\s+expunerea\s+la\s+praf\b': 'Evitare alergeni și praf',
            r'\bevitați\s+praf\s+și\s+alergeni\b': 'Evitare alergeni și praf',
            r'\bevitare\s+praf\s+și\s+alergeni\b': 'Evitare alergeni și praf',
            r'\bevitați\s+alergeni\b': 'Evitare alergeni și praf',
        }
        
        for pattern, rec_name in special_patterns.items():
            if re.search(pattern, text_lower, re.IGNORECASE) and rec_name not in found_recommendations:
                found_recommendations.add(rec_name)
                recommendations.append(rec_name)
        
        # Strategy 2: Extract from "recomand să evitați/faceți X" pattern
        recommendation_patterns = [
            r'(?:recomand|sugerez|vă\s+recomand)\s+(?:să\s+)?(evitați|faceți|începeți|urmați)\s+([^,\.;]+)',
        ]
        
        for pattern in recommendation_patterns:
            matches = re.finditer(pattern, text_lower, re.IGNORECASE)
            for match in matches:
                action = match.group(1).strip()
                rec_text = match.group(2).strip() if match.group(2) else None
                
                if not rec_text:
                    continue
                
                # Clean up
                rec_text = re.sub(r'\s+', ' ', rec_text)
                # Remove trailing descriptive words
                rec_text = re.sub(r'\s+(care|pot|declanșa|simptomele|mai|ușor|reduce|inflamația)\b.*$', '', rec_text, flags=re.IGNORECASE).strip()
                
                if not rec_text or len(rec_text) < 3:
                    continue
                
                rec_text_lower = rec_text.lower()
                
                # Check if matches known recommendation
                matched_known = False
                for keyword, recommendation_name in self.recommendation_patterns.items():
                    if keyword in rec_text_lower or rec_text_lower in keyword:
                        if recommendation_name not in found_recommendations:
                            found_recommendations.add(recommendation_name)
                            recommendations.append(recommendation_name)
                        matched_known = True
                        break
                
                # If action is "evitați" and mentions praf/alergeni, add recommendation
                if action == 'evitați' and ('praf' in rec_text_lower or 'alergeni' in rec_text_lower):
                    if 'Evitare alergeni și praf' not in found_recommendations:
                        found_recommendations.add('Evitare alergeni și praf')
                        recommendations.append('Evitare alergeni și praf')
        
        # Strategy 3: Direct keyword matching
        for keyword, recommendation_name in self.recommendation_patterns.items():
            pattern = r'\b' + re.escape(keyword) + r'\b'
            if re.search(pattern, text_lower) and recommendation_name not in found_recommendations:
                found_recommendations.add(recommendation_name)
                recommendations.append(recommendation_name)
            elif keyword in text_lower and recommendation_name not in found_recommendations:
                found_recommendations.add(recommendation_name)
                recommendations.append(recommendation_name)
        
        return recommendations
    
    def extract_medical_history(self, text: str) -> str:
        """Extract medical history mentions"""
        history_keywords = [
            'fumat', 'fumător', 'colesterol ridicat', 'hipertensiune',
            'diabet', 'obezitate', 'alergii', 'istoric', 'antecedente'
        ]
        
        found_history = []
        text_lower = text.lower()
        
        for keyword in history_keywords:
            if keyword in text_lower:
                # Extract context around keyword
                pattern = rf'.{{0,30}}{keyword}.{{0,30}}'
                matches = re.findall(pattern, text_lower)
                if matches:
                    found_history.append(keyword)
        
        return ', '.join(found_history) if found_history else ""
    
    def process_conversation(self, conversation_text: str) -> Dict:
        """Process full conversation and extract structured medical information"""
        # Extract all information
        patient_name = self.extract_patient_name(conversation_text)
        age = self.extract_age(conversation_text)
        sex = self.extract_sex(conversation_text)
        disease_info = self.extract_disease(conversation_text)
        medications = self.extract_medications(conversation_text)
        investigations = self.extract_investigations(conversation_text)
        recommendations = self.extract_recommendations(conversation_text)
        medical_history = self.extract_medical_history(conversation_text)
        
        # Build structured output
        result = {
            'input': conversation_text,
            'boala': disease_info.get('boala'),
            'cod_ICD': disease_info.get('cod_ICD'),
            'nume_pacient': patient_name,
            'varsta': age,
            'sex': sex,
            'istoric_medical': medical_history,
            'medicamente_recomandate': medications,
            'investigatii_recomandate': investigations,
            'recomandari_suplimentare': recommendations,
            'data_procesare': datetime.now().isoformat()
        }
        
        return result
    
    def generate_clinical_note(self, structured_data: Dict) -> str:
        """Generate clinical note from structured data"""
        note = f"""NOTĂ CLINICĂ
Data: {datetime.now().strftime('%d.%m.%Y %H:%M')}

PACIENT:
Nume: {structured_data.get('nume_pacient', 'N/A')}
Vârstă: {structured_data.get('varsta', 'N/A')} ani
Sex: {structured_data.get('sex', 'N/A')}

DIAGNOSTIC:
{structured_data.get('boala', 'N/A')} (ICD-10: {structured_data.get('cod_ICD', 'N/A')})

ISTORIC MEDICAL:
{structured_data.get('istoric_medical', 'N/A')}

TRATAMENT RECOMANDAT:
"""
        for med in structured_data.get('medicamente_recomandate', []):
            note += f"- {med['nume']} {med['doza']}, {med['administrare']}\n"
        
        note += f"\nINVESTIGAȚII RECOMANDATE:\n"
        for inv in structured_data.get('investigatii_recomandate', []):
            note += f"- {inv}\n"
        
        note += f"\nRECOMANDĂRI:\n"
        for rec in structured_data.get('recomandari_suplimentare', []):
            note += f"- {rec}\n"
        
        return note
    
    def generate_prescription(self, structured_data: Dict) -> str:
        """Generate prescription from structured data"""
        prescription = f"""REȚETĂ MEDICALĂ
Data: {datetime.now().strftime('%d.%m.%Y')}

Pacient: {structured_data.get('nume_pacient', 'N/A')}
Vârstă: {structured_data.get('varsta', 'N/A')} ani

MEDICAMENTE:
"""
        for i, med in enumerate(structured_data.get('medicamente_recomandate', []), 1):
            prescription += f"{i}. {med['nume']} {med['doza']}\n"
            prescription += f"   Administrare: {med['administrare']}\n\n"
        
        prescription += f"\nDiagnostic: {structured_data.get('boala', 'N/A')} (ICD-10: {structured_data.get('cod_ICD', 'N/A')})"
        
        return prescription

