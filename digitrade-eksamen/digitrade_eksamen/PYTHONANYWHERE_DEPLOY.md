# Deploy til PythonAnywhere – steg for steg

Denne guiden viser hvordan du legger Digitrade-nettsiden ut på PythonAnywhere (gratis konto). Følg stegene i rekkefølge.

## 1. Lag konto
1. Gå til https://www.pythonanywhere.com
2. Lag en gratis konto («Create a Beginner account»).

## 2. Få koden inn på PythonAnywhere

**Alternativ A – via GitHub (anbefalt):**
1. Push prosjektet til et eget GitHub-repo først.
2. På PythonAnywhere: åpne fanen **Consoles** → start en **Bash**-konsoll.
3. Hent koden:
   ```bash
   git clone https://github.com/BRUKERNAVN/digitrade.git
   ```

**Alternativ B – last opp filer:**
- Bruk fanen **Files** og last opp filene manuelt i en mappe.

## 3. Installer Flask
I Bash-konsollen:
```bash
pip install --user flask
```

## 4. Sett opp web-appen
1. Gå til fanen **Web** → **Add a new web app**.
2. Velg **Manual configuration** (ikke «Flask»-malen).
3. Velg samme Python-versjon som du brukte lokalt (f.eks. Python 3.10).

## 5. Koble appen til koden din
På **Web**-siden, finn feltet **WSGI configuration file** og klikk på lenken for å redigere den. Bytt ut innholdet med (tilpass stien til din mappe og ditt brukernavn):

```python
import sys

# Sti til mappen der app.py ligger
sti = "/home/BRUKERNAVN/digitrade"
if sti not in sys.path:
    sys.path.append(sti)

# Importer Flask-appen din (objektet heter "app" i app.py)
from app import app as application

# Opprett databasen første gang
from app import opprett_database
opprett_database()
```

## 6. Start appen
1. Gå tilbake til **Web**-fanen.
2. Klikk den grønne **Reload**-knappen.
3. Åpne nettadressen din: `https://BRUKERNAVN.pythonanywhere.com`

## 7. Logg inn for å teste
- admin / admin → adminsiden
- ola / ola123 → «Pythons scripts»

## Vanlige feil
- **«Something went wrong»:** sjekk **Error log** nederst på Web-fanen.
- **Finner ikke app:** sjekk at stien i WSGI-fila peker til riktig mappe, og at den importerer `app as application`.
- **Endringer vises ikke:** husk å klikke **Reload** etter hver endring.
