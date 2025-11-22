// Medical AI System Frontend

let recognition = null;
let isRecording = false;
let recordedText = '';
let currentUser = null;
let currentRecordId = null;  // Store current record ID for editing

// Load when page loads
document.addEventListener('DOMContentLoaded', async () => {
    // Check authentication
    await checkAuth();
    initSpeechRecognition();
    loadMedicalRecords();
});

// Check authentication
async function checkAuth() {
    try {
        const response = await fetch('/api/current-user');
        if (!response.ok) {
            window.location.href = '/login';
            return;
        }
        currentUser = await response.json();
        document.getElementById('userName').textContent = currentUser.full_name || currentUser.username;
    } catch (error) {
        console.error('Auth check failed:', error);
        window.location.href = '/login';
    }
}

// Logout function
async function logout() {
    try {
        const response = await fetch('/logout', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });
        
        if (response.ok) {
            window.location.href = '/login';
        }
    } catch (error) {
        console.error('Logout error:', error);
        window.location.href = '/login';
    }
}


// Tab Switching
function switchTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Show selected tab
    document.getElementById(tabName + 'Tab').classList.add('active');
    if (event && event.target) {
        event.target.classList.add('active');
    } else {
        // If called programmatically, find the button
        document.querySelectorAll('.tab-btn').forEach(btn => {
            if (btn.textContent.includes(tabName === 'conversation' ? 'Conversație' : 'Istoric')) {
                btn.classList.add('active');
            }
        });
    }
    
    // Load records if switching to records tab
    if (tabName === 'records') {
        loadMedicalRecords();
    }
}

// Speech Recognition
function initSpeechRecognition() {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        recognition = new SpeechRecognition();
        recognition.continuous = true;
        recognition.interimResults = true;
        recognition.lang = 'ro-RO';
        
        recognition.onresult = (event) => {
            let interimTranscript = '';
            let finalTranscript = '';
            
            for (let i = event.resultIndex; i < event.results.length; i++) {
                const transcript = event.results[i][0].transcript;
                if (event.results[i].isFinal) {
                    finalTranscript += transcript + ' ';
                } else {
                    interimTranscript += transcript;
                }
            }
            
            const textarea = document.getElementById('conversationText');
            textarea.value = recordedText + finalTranscript + interimTranscript;
        };
        
        recognition.onerror = (event) => {
            console.error('Speech recognition error:', event.error);
            if (event.error === 'no-speech') {
                // Ignore no-speech errors
                return;
            }
            stopRecording();
            alert('Eroare la recunoașterea vocii: ' + event.error);
        };
        
        recognition.onend = () => {
            if (isRecording) {
                // Restart if still recording
                try {
                    recognition.start();
                } catch (e) {
                    console.error('Error restarting recognition:', e);
                }
            }
        };
    } else {
        console.warn('Speech recognition not supported in this browser');
        document.getElementById('recordBtn').style.display = 'none';
    }
}

function toggleRecording() {
    if (!recognition) {
        alert('Recunoașterea vocală nu este disponibilă în acest browser');
        return;
    }
    
    if (!isRecording) {
        startRecording();
    } else {
        stopRecording();
    }
}

function startRecording() {
    isRecording = true;
    recordedText = document.getElementById('conversationText').value;
    document.getElementById('recordBtn').classList.add('recording');
    document.getElementById('recordBtn').style.display = 'none';
    document.getElementById('stopBtn').style.display = 'flex';
    document.getElementById('recordText').textContent = 'Se înregistrează...';
    
    try {
        recognition.start();
    } catch (e) {
        console.error('Error starting recognition:', e);
        stopRecording();
    }
}

function stopRecording() {
    isRecording = false;
    if (recognition) {
        recognition.stop();
    }
    document.getElementById('recordBtn').classList.remove('recording');
    document.getElementById('recordBtn').style.display = 'flex';
    document.getElementById('stopBtn').style.display = 'none';
    document.getElementById('recordText').textContent = 'Începe Înregistrarea';
    recordedText = document.getElementById('conversationText').value;
}

// Process Conversation
async function processConversation() {
    const conversationText = document.getElementById('conversationText').value.trim();
    
    if (!conversationText) {
        alert('Vă rugăm să introduceți conversația');
        return;
    }
    
    // Show loading
    document.getElementById('loading').style.display = 'block';
    document.getElementById('loadingText').textContent = 'Se procesează conversația...';
    document.getElementById('conversationResults').style.display = 'none';
    
    try {
        const response = await fetch('/api/process-conversation', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                conversation: conversationText
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            displayConversationResults(data);
            // Reload records
            loadMedicalRecords();
        } else {
            if (response.status === 401) {
                window.location.href = '/login';
                return;
            }
            showConversationError(data.error || 'Eroare la procesare');
        }
    } catch (error) {
        console.error('Error:', error);
        showConversationError('Eroare de conexiune');
    } finally {
        document.getElementById('loading').style.display = 'none';
    }
}

function displayConversationResults(data, recordId = null) {
    const resultsDiv = document.getElementById('conversationResults');
    const contentDiv = document.getElementById('conversationResultsContent');
    
    currentRecordId = recordId || data.record_id || null;
    const structured = data.structured_data;
    
    let html = `
        <div class="structured-data">
            <h3>📋 Date Structurate</h3>
            <div class="data-field">
                <label>Pacient:</label>
                <div class="value">${structured.nume_pacient || 'N/A'}</div>
            </div>
            <div class="data-field">
                <label>Vârstă:</label>
                <div class="value">${structured.varsta || 'N/A'} ani</div>
            </div>
            <div class="data-field">
                <label>Sex:</label>
                <div class="value">${structured.sex || 'N/A'}</div>
            </div>
            <div class="data-field">
                <label>Boală:</label>
                <div class="value">
                    ${structured.boala || 'N/A'}
                    ${structured.cod_ICD ? `<span class="icd-badge">ICD-10: ${structured.cod_ICD}</span>` : ''}
                </div>
            </div>
            <div class="data-field">
                <label>Istoric Medical:</label>
                <div class="value">${structured.istoric_medical || 'N/A'}</div>
            </div>
            <div class="data-field">
                <label>Medicamente Recomandate:</label>
                ${structured.medicamente_recomandate && structured.medicamente_recomandate.length > 0
                    ? structured.medicamente_recomandate.map(med => `
                        <div class="medication-item">
                            <strong>${med.nume}</strong> - ${med.doza}<br>
                            <small>${med.administrare}</small>
                        </div>
                    `).join('')
                    : '<div class="value">Niciun medicament recomandat</div>'
                }
            </div>
            <div class="data-field">
                <label>Investigații Recomandate:</label>
                ${structured.investigatii_recomandate && structured.investigatii_recomandate.length > 0
                    ? structured.investigatii_recomandate.map(inv => `
                        <div class="investigation-item">${inv}</div>
                    `).join('')
                    : '<div class="value">Niciună investigație recomandată</div>'
                }
            </div>
            <div class="data-field">
                <label>Recomandări Suplimentare:</label>
                ${structured.recomandari_suplimentare && structured.recomandari_suplimentare.length > 0
                    ? structured.recomandari_suplimentare.map(rec => `
                        <div class="recommendation-item">${rec}</div>
                    `).join('')
                    : '<div class="value">Niciună recomandare suplimentară</div>'
                }
            </div>
        </div>
        
        <div class="structured-data">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                <h3>📝 Notă Clinică</h3>
                <div>
                    <button id="editNoteBtn" class="btn-edit" onclick="enableEdit('note')">✏️ Editează</button>
                    <button id="saveNoteBtn" class="btn-save" onclick="saveEdit('note')" style="display: none;">💾 Salvează</button>
                    <button id="cancelNoteBtn" class="btn-cancel" onclick="cancelEdit('note')" style="display: none;">❌ Anulează</button>
                </div>
            </div>
            <div id="noteDisplay" class="clinical-note">${escapeHtml(data.clinical_note)}</div>
            <textarea id="noteEdit" class="clinical-note-edit" style="display: none;">${escapeHtml(data.clinical_note)}</textarea>
            <div style="margin-top: 10px;">
                <button class="download-btn" onclick="downloadText('${escapeHtml(data.clinical_note)}', 'nota_clinica.txt')">
                    📥 Descarcă Notă Clinică
                </button>
            </div>
        </div>
        
        <div class="structured-data">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                <h3>💊 Rețetă Medicală</h3>
                <div>
                    <button id="editPrescriptionBtn" class="btn-edit" onclick="enableEdit('prescription')">✏️ Editează</button>
                    <button id="savePrescriptionBtn" class="btn-save" onclick="saveEdit('prescription')" style="display: none;">💾 Salvează</button>
                    <button id="cancelPrescriptionBtn" class="btn-cancel" onclick="cancelEdit('prescription')" style="display: none;">❌ Anulează</button>
                </div>
            </div>
            <div id="prescriptionDisplay" class="prescription">${escapeHtml(data.prescription)}</div>
            <textarea id="prescriptionEdit" class="prescription-edit" style="display: none;">${escapeHtml(data.prescription)}</textarea>
            <div style="margin-top: 10px;">
                <button class="download-btn" onclick="downloadText('${escapeHtml(data.prescription)}', 'reteta_medicala.txt')">
                    📥 Descarcă Rețetă
                </button>
            </div>
        </div>
    `;
    
    contentDiv.innerHTML = html;
    resultsDiv.style.display = 'block';
    resultsDiv.scrollIntoView({ behavior: 'smooth' });
}

function showConversationError(message) {
    const resultsDiv = document.getElementById('conversationResults');
    const contentDiv = document.getElementById('conversationResultsContent');
    contentDiv.innerHTML = `<div class="warning">❌ ${message}</div>`;
    resultsDiv.style.display = 'block';
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function downloadText(text, filename) {
    const blob = new Blob([text], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
}

// Edit functions
let originalNote = '';
let originalPrescription = '';

function enableEdit(type) {
    if (type === 'note') {
        originalNote = document.getElementById('noteEdit').value;
        document.getElementById('noteDisplay').style.display = 'none';
        document.getElementById('noteEdit').style.display = 'block';
        document.getElementById('editNoteBtn').style.display = 'none';
        document.getElementById('saveNoteBtn').style.display = 'inline-block';
        document.getElementById('cancelNoteBtn').style.display = 'inline-block';
    } else if (type === 'prescription') {
        originalPrescription = document.getElementById('prescriptionEdit').value;
        document.getElementById('prescriptionDisplay').style.display = 'none';
        document.getElementById('prescriptionEdit').style.display = 'block';
        document.getElementById('editPrescriptionBtn').style.display = 'none';
        document.getElementById('savePrescriptionBtn').style.display = 'inline-block';
        document.getElementById('cancelPrescriptionBtn').style.display = 'inline-block';
    }
}

function cancelEdit(type) {
    if (type === 'note') {
        document.getElementById('noteEdit').value = originalNote;
        document.getElementById('noteDisplay').style.display = 'block';
        document.getElementById('noteEdit').style.display = 'none';
        document.getElementById('editNoteBtn').style.display = 'inline-block';
        document.getElementById('saveNoteBtn').style.display = 'none';
        document.getElementById('cancelNoteBtn').style.display = 'none';
    } else if (type === 'prescription') {
        document.getElementById('prescriptionEdit').value = originalPrescription;
        document.getElementById('prescriptionDisplay').style.display = 'block';
        document.getElementById('prescriptionEdit').style.display = 'none';
        document.getElementById('editPrescriptionBtn').style.display = 'inline-block';
        document.getElementById('savePrescriptionBtn').style.display = 'none';
        document.getElementById('cancelPrescriptionBtn').style.display = 'none';
    }
}

async function saveEdit(type) {
    if (!currentRecordId) {
        alert('Nu se poate salva - înregistrarea nu este identificată');
        return;
    }
    
    let content = '';
    if (type === 'note') {
        content = document.getElementById('noteEdit').value;
    } else if (type === 'prescription') {
        content = document.getElementById('prescriptionEdit').value;
    }
    
    try {
        const response = await fetch(`/api/records/${currentRecordId}/update`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                type: type,
                content: content
            })
        });
        
        if (response.status === 401) {
            window.location.href = '/login';
            return;
        }
        
        const data = await response.json();
        
        if (response.ok) {
            // Update display
            if (type === 'note') {
                document.getElementById('noteDisplay').textContent = content;
                document.getElementById('noteDisplay').style.display = 'block';
                document.getElementById('noteEdit').style.display = 'none';
                document.getElementById('editNoteBtn').style.display = 'inline-block';
                document.getElementById('saveNoteBtn').style.display = 'none';
                document.getElementById('cancelNoteBtn').style.display = 'none';
            } else if (type === 'prescription') {
                document.getElementById('prescriptionDisplay').textContent = content;
                document.getElementById('prescriptionDisplay').style.display = 'block';
                document.getElementById('prescriptionEdit').style.display = 'none';
                document.getElementById('editPrescriptionBtn').style.display = 'inline-block';
                document.getElementById('savePrescriptionBtn').style.display = 'none';
                document.getElementById('cancelPrescriptionBtn').style.display = 'none';
            }
            alert('Modificările au fost salvate cu succes!');
        } else {
            alert('Eroare la salvare: ' + (data.error || 'Eroare necunoscută'));
        }
    } catch (error) {
        console.error('Error saving:', error);
        alert('Eroare de conexiune la salvare');
    }
}

// Medical Records
async function loadMedicalRecords() {
    try {
        const response = await fetch('/api/records');
        if (response.status === 401) {
            window.location.href = '/login';
            return;
        }
        const data = await response.json();
        
        if (response.ok) {
            displayMedicalRecords(data.records);
        }
    } catch (error) {
        console.error('Error loading records:', error);
    }
}

function displayMedicalRecords(records) {
    const container = document.getElementById('recordsList');
    
    if (!records || records.length === 0) {
        container.innerHTML = '<p>Nu există înregistrări medicale.</p>';
        return;
    }
    
    let html = '';
    records.forEach(record => {
        const date = new Date(record.created_at);
        html += `
            <div class="record-card" onclick="viewRecord(${record.id})">
                <div class="record-header">
                    <h3>${record.patient_name || 'Pacient necunoscut'}</h3>
                    <span class="icd-badge">${record.icd_code || 'N/A'}</span>
                </div>
                <div class="record-meta">
                    <strong>Boală:</strong> ${record.disease || 'N/A'} | 
                    <strong>Vârstă:</strong> ${record.age || 'N/A'} ani | 
                    <strong>Data:</strong> ${date.toLocaleDateString('ro-RO')}
                </div>
            </div>
        `;
    });
    
    container.innerHTML = html;
}

async function viewRecord(recordId) {
    try {
        const response = await fetch(`/api/records/${recordId}`);
        if (response.status === 401) {
            window.location.href = '/login';
            return;
        }
        const data = await response.json();
        
        if (response.ok) {
            // Switch to conversation tab and display results
            switchTab('conversation');
            document.getElementById('conversationText').value = data.conversation_text;
            
            // Display the structured data
            displayConversationResults({
                structured_data: data.structured_data,
                clinical_note: data.clinical_note,
                prescription: data.prescription
            }, recordId);
        } else {
            alert('Eroare la încărcarea înregistrării: ' + (data.error || 'Nu aveți acces la această înregistrare'));
        }
    } catch (error) {
        console.error('Error loading record:', error);
        alert('Eroare la încărcarea înregistrării');
    }
}

