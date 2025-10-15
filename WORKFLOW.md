# Git Workflow - TaskMaster DevOps

## Vetvy (Branches)

### `main`
- **Účel:** Produkčná vetva, stabilný kód
- **Pravidlá:** 
  - Nikdy nepushuj priamo do `main`
  - Merge len z `develop` po testovaní
  - Každý merge do `main` = release

### `develop`
- **Účel:** Vývojová vetva, integrácia features
- **Pravidlá:**
  - Všetky nové features sa mergeujú sem
  - Testovanie pred merge do `main`

### `feature/*`
- **Účel:** Vývoj konkrétnej funkcionality
- **Naming:** `feature/nazov-funkcie`
- **Workflow:**
  1. Vytvor z `develop`: `git checkout -b feature/moja-funkcia develop`
  2. Pracuj na feature
  3. Merge do `develop`
  4. Vymaž feature vetvu

---

## Conventional Commits

Formát: `<type>: <description>`

### Typy commitov:
- `feat:` - Nová funkcionalita
  - Príklad: `feat: add user authentication`
- `fix:` - Oprava bugu
  - Príklad: `fix: resolve login timeout issue`
- `docs:` - Dokumentácia
  - Príklad: `docs: update installation guide`
- `chore:` - Údržba, konfigurácia
  - Príklad: `chore: update dependencies`
- `refactor:` - Refaktoring kódu
  - Príklad: `refactor: simplify database queries`
- `test:` - Testy
  - Príklad: `test: add unit tests for API`

### Pravidlá:
- Lowercase popis
- Bez bodky na konci
- Krátky a výstižný (max 50 znakov)

---

## Workflow príklad
```bash
# 1. Začni na develop
git checkout develop
git pull

# 2. Vytvor feature vetvu
git checkout -b feature/add-docker-config

# 3. Pracuj a commituj
git add .
git commit -m "feat: add Dockerfile for backend"

# 4. Push feature vetvy
git push -u origin feature/add-docker-config

# 5. Merge do develop (lokálne alebo cez PR)
git checkout develop
git merge feature/add-docker-config

# 6. Vymaž feature vetvu
git branch -d feature/add-docker-config
git push origin --delete feature/add-docker-config

# 7. Keď je develop stabilný, merge do main
git checkout main
git merge develop
git push
```

---

## Autor
René Kuda  
Projekt: TaskMaster DevOps  
Dátum: 15.10.2025
