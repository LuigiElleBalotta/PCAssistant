# PC Assistant - Quick Start Guide

## 🚀 Avvio Rapido

### Metodo 1: Launcher Script (Consigliato)

Doppio click su uno di questi file:
- **`run.bat`** - Per Command Prompt
- **`run.ps1`** - Per PowerShell

Gli script si occupano automaticamente di:
- ✅ Attivare l'ambiente virtuale
- ✅ Verificare le dipendenze
- ✅ Avviare l'applicazione

### Metodo 2: Manuale

```powershell
.\venv\Scripts\Activate.ps1
python src/main.py
```

## 📦 Creare un Eseguibile

### Build Rapida

Doppio click su uno di questi file:
- **`build.bat`** - Per Command Prompt
- **`build.ps1`** - Per PowerShell

### Build Manuale

```powershell
.\venv\Scripts\Activate.ps1
python build.py
```

### Risultato Build

Ogni build crea una cartella con timestamp in `builds/`:

```
builds/
└── build_20251204_105900/
    ├── dist/
    │   └── PCAssistant/
    │       └── PCAssistant.exe  ← ESEGUIBILE PRINCIPALE
    └── BUILD_INFO.txt
```

### Distribuzione

1. Vai in `builds/build_XXXXXXXX_XXXXXX/dist/`
2. Comprimi la cartella `PCAssistant` in un file ZIP
3. Condividi il file ZIP
4. Gli utenti possono estrarre ed eseguire `PCAssistant.exe` senza installare Python!

## ⚙️ Funzionalità Principali

### 🧹 Cleaner Tab
- Seleziona le opzioni di pulizia
- Clicca **Analyze** per vedere cosa verrà rimosso
- Clicca **Clean** per pulire

### 🔧 Tools Tab

**Duplicate Finder:**
1. Clicca "Select Directory"
2. Scegli la cartella da scansionare
3. Clicca "Scan for Duplicates"
4. Seleziona i duplicati da eliminare

**Software Manager:**
1. La lista si carica automaticamente
2. Seleziona i programmi da disinstallare
3. Clicca "Uninstall Selected"

### 🚀 Optimizer Tab
- Visualizza risorse in tempo reale
- Gestisci programmi di avvio
- Disabilita programmi non necessari

### ⚙️ Settings Tab
- Configura opzioni predefinite
- Imposta numero di passaggi per cancellazione sicura
- Salva le preferenze

## ⚠️ Privilegi Amministratore

Per funzionalità complete, esegui come amministratore:
- Tasto destro su `run.bat` → "Esegui come amministratore"
- Oppure tasto destro su `PCAssistant.exe` → "Esegui come amministratore"

Funzionalità che richiedono admin:
- ✓ Pulizia registro
- ✓ Disinstallazione software
- ✓ Modifica programmi di avvio
- ✓ Accesso a file di sistema

## 📝 Note

- I log vengono salvati in `logs/`
- I backup del registro in `registry_backups/`
- Le impostazioni in `config.json`

## 🆘 Risoluzione Problemi

**Errore "Virtual environment not found":**
```powershell
python -m venv venv
```

**Errore "Module not found":**
```powershell
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**Build fallita:**
```powershell
pip install pyinstaller
python build.py
```
