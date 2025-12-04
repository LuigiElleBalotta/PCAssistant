# 🚀 Guida Completa GitHub Actions e GitOps

## 📋 Panoramica

Il progetto PC Assistant è ora completamente configurato per CI/CD con GitHub Actions. Questa guida spiega come funziona tutto il sistema.

## 🔄 Workflow Automatizzati

### 1. CI - Build and Test (`ci.yml`)

**Quando si attiva:**
- Push su branch `main` o `develop`
- Pull request verso `main` o `develop`

**Cosa fa:**
- ✅ Configura Python 3.11
- ✅ Installa dipendenze
- ✅ Esegue linting con flake8
- ✅ Testa import dei moduli
- ✅ Carica risultati test come artifact

**Badge:** 
```markdown
[![CI](https://github.com/USERNAME/pc_assistant/actions/workflows/ci.yml/badge.svg)](https://github.com/USERNAME/pc_assistant/actions/workflows/ci.yml)
```

### 2. Release - Build and Publish (`release.yml`)

**Quando si attiva:**
- Push di tag versione (es: `v1.0.0`, `v1.2.3`)

**Cosa fa:**
1. ✅ Build eseguibile Windows con PyInstaller
2. ✅ Copia file aggiuntivi (README, config, ecc.)
3. ✅ Crea archivio ZIP
4. ✅ Genera checksum SHA256
5. ✅ Crea release GitHub automatica
6. ✅ Carica file scaricabili

**Output:**
- `PCAssistant-vX.X.X-Windows-x64.zip`
- `CHECKSUMS.txt`
- Release notes automatiche

### 3. Weekly Build (`weekly-build.yml`)

**Quando si attiva:**
- Ogni lunedì alle 00:00 UTC
- Manualmente tramite workflow_dispatch

**Cosa fa:**
- ✅ Build di sviluppo settimanale
- ✅ Crea artifact con data
- ✅ Mantiene artifact per 14 giorni

## 📁 Struttura File GitHub

```
.github/
├── workflows/
│   ├── ci.yml                    # Test automatici
│   ├── release.yml               # Release automatiche
│   └── weekly-build.yml          # Build settimanali
├── ISSUE_TEMPLATE/
│   ├── bug_report.yml           # Template bug report
│   ├── feature_request.yml      # Template feature request
│   └── config.yml               # Configurazione template
├── PULL_REQUEST_TEMPLATE.md     # Template PR
├── RELEASE_GUIDE.md             # Guida release (italiano)
└── CODEOWNERS                   # Code ownership
```

## 🎯 Come Creare una Release

### Passo 1: Prepara il Codice

```bash
# Assicurati di essere su main
git checkout main
git pull origin main

# Aggiorna CHANGELOG.md
# Aggiungi le modifiche della nuova versione
```

### Passo 2: Crea e Pusha il Tag

```bash
# Crea tag annotato
git tag -a v1.0.0 -m "Release version 1.0.0"

# Pusha il tag
git push origin v1.0.0
```

### Passo 3: Automatico! 🎉

GitHub Actions automaticamente:
1. Esegue il build
2. Crea la release
3. Carica i file

### Passo 4: Verifica

Vai su: `https://github.com/USERNAME/pc_assistant/releases`

## 📝 Template e Documentazione

### Issue Templates

**Bug Report** (`.github/ISSUE_TEMPLATE/bug_report.yml`):
- Campi strutturati per bug report
- Informazioni versione, Windows, privilegi admin
- Spazio per log e screenshot

**Feature Request** (`.github/ISSUE_TEMPLATE/feature_request.yml`):
- Descrizione problema e soluzione
- Categorizzazione feature
- Livello priorità

### Pull Request Template

Template automatico per PR con:
- Tipo di modifica
- Issue correlato
- Checklist test
- Checklist qualità codice

## 🔐 Sicurezza e Best Practices

### SECURITY.md
- Policy di sicurezza
- Come riportare vulnerabilità
- Versioni supportate
- Best practices per utenti

### CONTRIBUTING.md
- Guida per contribuire
- Setup sviluppo
- Standard di codice
- Processo PR

### LICENSE
- Licenza MIT
- Permessi e limitazioni

## 📊 Monitoraggio

### Visualizzare Workflow

1. Vai su: `https://github.com/USERNAME/pc_assistant/actions`
2. Seleziona il workflow
3. Visualizza log in tempo reale

### Artifact

Gli artifact sono disponibili per:
- **Test results**: 7 giorni
- **Weekly builds**: 14 giorni
- **Release builds**: 30 giorni

## 🎨 Badge per README

Aggiungi al README:

```markdown
[![CI](https://github.com/USERNAME/pc_assistant/actions/workflows/ci.yml/badge.svg)](https://github.com/USERNAME/pc_assistant/actions/workflows/ci.yml)
[![Release](https://github.com/USERNAME/pc_assistant/actions/workflows/release.yml/badge.svg)](https://github.com/USERNAME/pc_assistant/actions/workflows/release.yml)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
```

## 🔧 Configurazione Repository

### Impostazioni Necessarie

1. **Settings → Actions → General**
   - ✅ Allow all actions and reusable workflows
   - ✅ Read and write permissions
   - ✅ Allow GitHub Actions to create and approve pull requests

2. **Settings → Branches**
   - Proteggi branch `main`
   - Richiedi PR review
   - Richiedi status check (CI)

3. **Settings → Pages** (opzionale)
   - Abilita GitHub Pages per documentazione

## 📦 Semantic Versioning

Usa [Semantic Versioning](https://semver.org/):

- **v1.0.0** → **v2.0.0**: Breaking changes
- **v1.0.0** → **v1.1.0**: Nuove feature (compatibili)
- **v1.0.0** → **v1.0.1**: Bug fix

## 🚨 Troubleshooting

### Workflow non parte

**Problema:** Il tag è stato pushato ma il workflow non parte

**Soluzione:**
- Verifica formato tag: `v*.*.*`
- Controlla permessi Actions
- Verifica che il file workflow sia su `main`

### Build fallisce

**Problema:** Il build PyInstaller fallisce

**Soluzione:**
- Testa localmente: `python build.py`
- Verifica `requirements.txt`
- Controlla log GitHub Actions

### Release non creata

**Problema:** Build OK ma release non appare

**Soluzione:**
- Verifica permessi: `contents: write`
- Controlla `GITHUB_TOKEN`
- Verifica che non esista già una release con quel tag

## 📚 Risorse Utili

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [PyInstaller Documentation](https://pyinstaller.org/)
- [Semantic Versioning](https://semver.org/)
- [Keep a Changelog](https://keepachangelog.com/)

## ✅ Checklist Setup Iniziale

Prima di pushare su GitHub:

- [ ] Sostituisci `USERNAME` con il tuo username in tutti i file
- [ ] Aggiorna email in `SECURITY.md`
- [ ] Verifica `CODEOWNERS`
- [ ] Testa workflow localmente se possibile
- [ ] Crea repository su GitHub
- [ ] Pusha codice
- [ ] Abilita GitHub Actions
- [ ] Configura branch protection
- [ ] Crea primo tag per testare release

## 🎉 Risultato Finale

Con questa configurazione hai:

✅ **CI/CD completo** - Test automatici su ogni push
✅ **Release automatiche** - Build e pubblicazione con un tag
✅ **Build settimanali** - Snapshot di sviluppo
✅ **Template standardizzati** - Issue e PR strutturati
✅ **Documentazione completa** - Guide per utenti e sviluppatori
✅ **Sicurezza** - Policy e best practices
✅ **Professionale** - Pronto per open source

---

**Pronto per essere pubblicato su GitHub!** 🚀
