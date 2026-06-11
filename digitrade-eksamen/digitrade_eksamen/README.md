# Digitrade AS – Intern nettside

Teknisk løsningsbeskrivelse. Tverrfaglig eksamen i Informasjonsteknologi (ITK2004), vår 2026. Hovedretning: IT-utvikling.

## 1. Hva løsningen gjør

En nettside for Digitrade AS med:
- Forside med informasjon om bedriften og en kontaktside
- Fleksibel meny som endrer seg etter om du er innlogget og hvilken rolle du har
- Innlogging og autorisering som er skrevet fra bunnen (ingen ferdig login-modul)
- Lagring av brukere i en SQLite-database
- admin/admin sendes til en side for å administrere brukere
- Andre brukere sendes til en side med overskriften «Pythons scripts»

## 2. Teknologivalg

| Komponent | Valg | Begrunnelse |
|-----------|------|-------------|
| Backend | Python + Flask | Enkelt rammeverk, fungerer på PythonAnywhere |
| Lagring | SQLite | Filbasert database, ingen egen databaseserver nødvendig |
| Login/autorisering | Egen kode | Oppgaven krever at dette skrives selv |
| Maler | Jinja2 (HTML) | Følger med Flask |

Flask brukes som webserver/rammeverk, men selve login- og autoriseringslogikken er skrevet for hånd, slik oppgaven krever.

## 3. Slik er innlogging og autorisering laget selv

Det finnes ingen ferdig login-modul i prosjektet. I stedet:

1. Ved innlogging hentes brukeren fra databasen, og passordet sammenlignes direkte (`bruker["passord"] == passord`).
2. Stemmer det, lagres brukernavn og rolle i `session` (en signert cookie).
3. To egne funksjoner styrer tilgangen:
   - `krev_innlogging()` – sender deg til login hvis du ikke er innlogget
   - `krev_admin()` – krever i tillegg admin-rollen
4. Hver beskyttet side kaller en av disse øverst.

Ruting etter login: admin-rolle går til `/admin`, alle andre til `/scripts`.

## 4. Lagring

Brukere lagres i tabellen `brukere` i SQLite:

| Felt | Type | Beskrivelse |
|------|------|-------------|
| id | INTEGER | Primærnøkkel |
| brukernavn | TEXT | Unikt |
| passord | TEXT | Lagres i klartekst (forenkling) |
| rolle | TEXT | admin eller bruker |

> Merk: I et reelt system bør passord hashes, slik at de ikke kan leses selv om databasen lekker. Det er bevisst utelatt her for å holde løsningen enkel.

## 5. Skalerbarhet

Løsningen er laget for å være lett å utvide:
- **Ny side:** lag en ny `@app.route` og en ny HTML-mal. Legg en lenke i menyen i `base.html`.
- **Beskytte en side:** kall `krev_innlogging()` eller `krev_admin()` øverst i ruten.
- **Ny lagring:** legg til en ny `CREATE TABLE` i `opprett_database()`. Resten av koden trenger ikke endres.
- Menyen bygges ut fra rollen, så nye nivåer er enkle å legge til.

## 6. Sikkerhet

- Parameteriserte SQL-spørringer (`?`) beskytter mot SQL-injeksjon
- Sesjonen tømmes ved utlogging (`session.clear()`)
- Tilgang sjekkes på hver beskyttet side
- Svakhet (bevisst): passord i klartekst – ville blitt hashet i produksjon

## 7. Filstruktur

```
digitrade2/
├── app.py              # Flask-app: ruter, login, autorisering
├── templates/          # HTML-maler
│   ├── base.html       # felles ramme + meny
│   ├── hjem.html
│   ├── kontakt.html
│   ├── login.html
│   ├── scripts.html    # <h1>Pythons scripts</h1>
│   └── admin.html      # administrere brukere
├── static/
│   └── stil.css
├── requirements.txt
└── README.md
```

## 8. Kjøre lokalt

```bash
pip install flask
python app.py
# Åpne http://127.0.0.1:5000
```

Standardbrukere (lages automatisk): `admin` / `admin` og `ola` / `ola123`.

## 9. Kilder

- Flask-dokumentasjon – https://flask.palletsprojects.com – (lastet ned 11.06.2026)
- PythonAnywhere hjelp – https://help.pythonanywhere.com – (lastet ned 11.06.2026)
