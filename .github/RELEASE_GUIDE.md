# 🚀 Come Creare una Release

Questa guida spiega come creare una nuova release di PC Assistant usando GitHub Actions.

## Prerequisiti

- Accesso push al repository
- Git configurato localmente
- Modifiche committate e pushate su `main`

## Processo di Release

### 1. Aggiorna il Changelog

Modifica `CHANGELOG.md` e aggiungi le modifiche della nuova versione:

```markdown
## [1.1.0] - 2025-12-XX

### Added
- Nuova funzionalità X
- Nuova funzionalità Y

### Fixed
- Bug fix Z

### Changed
- Miglioramento W
```

Committa le modifiche:
```bash
git add CHANGELOG.md
git commit -m "Update changelog for v1.1.0"
git push origin main
```

### 2. Crea il Tag di Versione

Crea un tag annotato con la versione (segui [Semantic Versioning](https://semver.org/)):

```bash
# Formato: vMAJOR.MINOR.PATCH
git tag -a v1.1.0 -m "Release version 1.1.0"
```

**Semantic Versioning:**
- **MAJOR** (v2.0.0): Modifiche incompatibili con versioni precedenti
- **MINOR** (v1.1.0): Nuove funzionalità compatibili
- **PATCH** (v1.0.1): Bug fix compatibili

### 3. Pusha il Tag

```bash
git push origin v1.1.0
```

### 4. GitHub Actions Automatizza il Resto

Una volta pushato il tag, GitHub Actions automaticamente:

1. ✅ Esegue il build dell'eseguibile Windows
2. ✅ Crea l'archivio ZIP
3. ✅ Genera i checksum SHA256
4. ✅ Crea la release su GitHub
5. ✅ Carica i file scaricabili

### 5. Verifica la Release

1. Vai su: `https://github.com/USERNAME/pc_assistant/releases`
2. Verifica che la release sia stata creata
3. Controlla che i file siano presenti:
   - `PCAssistant-v1.1.0-Windows-x64.zip`
   - `CHECKSUMS.txt`

## Monitoraggio del Build

Puoi monitorare il processo di build:

1. Vai su: `https://github.com/USERNAME/pc_assistant/actions`
2. Clicca sul workflow "Release - Build and Publish"
3. Visualizza i log in tempo reale

## Modificare una Release

Se devi modificare una release già pubblicata:

### Opzione 1: Eliminare e Ricreare

```bash
# Elimina il tag locale
git tag -d v1.1.0

# Elimina il tag remoto
git push origin :refs/tags/v1.1.0

# Elimina la release su GitHub (manualmente dalla UI)

# Ricrea il tag
git tag -a v1.1.0 -m "Release version 1.1.0"
git push origin v1.1.0
```

### Opzione 2: Creare una Patch Release

Se ci sono bug minori, crea una patch release:

```bash
git tag -a v1.1.1 -m "Release version 1.1.1 - Bug fixes"
git push origin v1.1.1
```

## Pre-release (Beta/RC)

Per creare una pre-release:

```bash
git tag -a v1.2.0-beta.1 -m "Beta release 1.2.0-beta.1"
git push origin v1.2.0-beta.1
```

Modifica manualmente la release su GitHub e marca come "Pre-release".

## Hotfix per Versioni Precedenti

Se devi fare un hotfix per una versione precedente:

```bash
# Crea un branch dalla versione precedente
git checkout v1.0.0
git checkout -b hotfix/1.0.1

# Fai le modifiche necessarie
git add .
git commit -m "Fix critical bug"

# Crea il tag
git tag -a v1.0.1 -m "Hotfix release 1.0.1"
git push origin v1.0.1
```

## Checklist Pre-Release

Prima di creare una release, verifica:

- [ ] Tutti i test passano
- [ ] `CHANGELOG.md` è aggiornato
- [ ] La versione segue Semantic Versioning
- [ ] Il codice è stato testato su Windows 10/11
- [ ] Non ci sono errori nei log
- [ ] La documentazione è aggiornata
- [ ] Le dipendenze sono aggiornate in `requirements.txt`

## Rollback di una Release

Se una release ha problemi critici:

1. **Elimina la release su GitHub** (UI)
2. **Elimina il tag:**
   ```bash
   git tag -d v1.1.0
   git push origin :refs/tags/v1.1.0
   ```
3. **Crea una nuova release** con le correzioni

## Troubleshooting

### Il workflow non parte

- Verifica che il tag sia nel formato `v*.*.*`
- Controlla i permessi del repository
- Verifica che GitHub Actions sia abilitato

### Build fallisce

- Controlla i log in GitHub Actions
- Verifica che tutte le dipendenze siano in `requirements.txt`
- Testa il build localmente con `build.py`

### File mancanti nella release

- Verifica che i file siano copiati nello step "Copy additional files"
- Controlla che i path siano corretti nel workflow

## Risorse

- [Semantic Versioning](https://semver.org/)
- [Keep a Changelog](https://keepachangelog.com/)
- [GitHub Releases](https://docs.github.com/en/repositories/releasing-projects-on-github)
- [GitHub Actions](https://docs.github.com/en/actions)

---

**Nota:** Sostituisci `USERNAME` con il tuo username GitHub effettivo.
