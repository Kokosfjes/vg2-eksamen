"""
Digitrade AS - Intern nettside (eksamen v\u00e5r 2026)
==================================================
Login og autorisering er skrevet FRA BUNNEN - ingen ferdige
login-moduler (ikke Flask-Login, ikke werkzeug.security).

- Brukere lagres i en SQLite-database (digitrade.db).
- Passord lagres i klartekst (forenkling for eksamen).
  MERK: I et reelt system burde passord hashes.
- Innlogging holdes styr p\u00e5 med en egen, enkel sesjons-l\u00f8sning
  basert p\u00e5 en signert cookie via Flask sin session.
- Autorisering (hvem f\u00e5r se hva) er en egen funksjon vi skriver selv.

Ruting etter login:
  admin / admin  -> /admin  (administrere brukere)
  alle andre     -> /scripts (siden med <h1>Pythons scripts</h1>)

Skalerbarhet:
  - Nye sider legges til ved \u00e5 lage en ny @app.route + template.
  - krev_innlogging() / krev_admin() gjenbrukes for \u00e5 beskytte sider.
  - Ny lagring legges til ved \u00e5 lage en ny tabell i opprett_database().
"""

from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os

app = Flask(__name__)
# Brukes til \u00e5 signere session-cookien. B\u00f8r v\u00e6re hemmelig i produksjon.
app.secret_key = "digitrade-eksamen-2026"

DB = "digitrade.db"


# ===========================================================
#  DATABASE
# ===========================================================
def koble_til():
    """\u00c5pner databasen og lar oss hente rader som oppslag (dict)."""
    kobling = sqlite3.connect(DB)
    kobling.row_factory = sqlite3.Row
    return kobling


def opprett_database():
    """Lager brukertabellen f\u00f8rste gang, og legger inn standardbrukere.

    Vil du lagre noe nytt (f.eks. meldinger), lager du bare en
    ny CREATE TABLE her - resten av koden trenger ikke endres.
    """
    db = koble_til()
    db.execute("""
        CREATE TABLE IF NOT EXISTS brukere (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            brukernavn TEXT UNIQUE NOT NULL,
            passord    TEXT NOT NULL,
            rolle      TEXT NOT NULL
        )
    """)
    db.commit()

    # Legg inn admin og en vanlig bruker hvis tabellen er tom
    antall = db.execute("SELECT COUNT(*) AS n FROM brukere").fetchone()["n"]
    if antall == 0:
        db.execute("INSERT INTO brukere (brukernavn, passord, rolle) VALUES (?, ?, ?)",
                   ("admin", "admin", "admin"))
        db.execute("INSERT INTO brukere (brukernavn, passord, rolle) VALUES (?, ?, ?)",
                   ("ola", "ola123", "bruker"))
        db.commit()
        print("Database opprettet med standardbrukere (admin/admin og ola/ola123).")
    db.close()


# ===========================================================
#  EGEN AUTORISERING (skrevet selv, ingen ferdig modul)
# ===========================================================
def er_innlogget():
    """Returnerer True hvis det ligger en bruker i sesjonen."""
    return "brukernavn" in session


def er_admin():
    """Returnerer True hvis innlogget bruker har admin-rollen."""
    return session.get("rolle") == "admin"


def krev_innlogging():
    """Sjekker innlogging. Returnerer en redirect hvis ikke innlogget,
    ellers None. Brukes \u00f8verst i hver beskyttet rute."""
    if not er_innlogget():
        flash("Du m\u00e5 logge inn f\u00f8rst.", "feil")
        return redirect(url_for("login"))
    return None


def krev_admin():
    """Som krev_innlogging, men krever ogs\u00e5 admin-rolle."""
    if not er_innlogget():
        flash("Du m\u00e5 logge inn f\u00f8rst.", "feil")
        return redirect(url_for("login"))
    if not er_admin():
        flash("Du har ikke tilgang til denne siden.", "feil")
        return redirect(url_for("scripts"))
    return None


# ===========================================================
#  RUTER - \u00c5PNE SIDER
# ===========================================================
@app.route("/")
def hjem():
    """Forsiden: informasjon om bedriften."""
    return render_template("hjem.html")


@app.route("/kontakt")
def kontakt():
    """Kontaktinformasjon."""
    return render_template("kontakt.html")


# ===========================================================
#  RUTER - LOGIN / LOGOUT (egen autentisering)
# ===========================================================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        brukernavn = request.form["brukernavn"].strip()
        passord = request.form["passord"]

        # Hent brukeren fra databasen
        db = koble_til()
        bruker = db.execute(
            "SELECT * FROM brukere WHERE brukernavn = ?", (brukernavn,)
        ).fetchone()
        db.close()

        # Egen autentisering: sjekk at bruker finnes og at passord stemmer
        if bruker is not None and bruker["passord"] == passord:
            # Lagre hvem som er innlogget i sesjonen
            session["brukernavn"] = bruker["brukernavn"]
            session["rolle"] = bruker["rolle"]

            # Ruting: admin -> admin-side, andre -> scripts-side
            if bruker["rolle"] == "admin":
                return redirect(url_for("admin"))
            else:
                return redirect(url_for("scripts"))
        else:
            flash("Feil brukernavn eller passord.", "feil")
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Du er logget ut.", "ok")
    return redirect(url_for("login"))


# ===========================================================
#  RUTER - BESKYTTEDE SIDER
# ===========================================================
@app.route("/scripts")
def scripts():
    """Side for vanlige brukere. Krever innlogging."""
    vakt = krev_innlogging()
    if vakt:
        return vakt
    return render_template("scripts.html", brukernavn=session["brukernavn"])


@app.route("/admin")
def admin():
    """Adminside: oversikt over brukere. Krever admin."""
    vakt = krev_admin()
    if vakt:
        return vakt
    db = koble_til()
    brukere = db.execute("SELECT * FROM brukere ORDER BY id").fetchall()
    db.close()
    return render_template("admin.html", brukere=brukere)


@app.route("/admin/ny", methods=["POST"])
def admin_ny_bruker():
    """Legg til en ny bruker (kun admin)."""
    vakt = krev_admin()
    if vakt:
        return vakt

    brukernavn = request.form["brukernavn"].strip()
    passord = request.form["passord"]
    rolle = request.form["rolle"]

    db = koble_til()
    finnes = db.execute("SELECT id FROM brukere WHERE brukernavn = ?",
                        (brukernavn,)).fetchone()
    if finnes:
        flash("Brukernavnet finnes allerede.", "feil")
    else:
        db.execute("INSERT INTO brukere (brukernavn, passord, rolle) VALUES (?, ?, ?)",
                   (brukernavn, passord, rolle))
        db.commit()
        flash(f"Bruker '{brukernavn}' lagt til.", "ok")
    db.close()
    return redirect(url_for("admin"))


@app.route("/admin/slett/<int:bruker_id>")
def admin_slett_bruker(bruker_id):
    """Slett en bruker (kun admin)."""
    vakt = krev_admin()
    if vakt:
        return vakt

    db = koble_til()
    db.execute("DELETE FROM brukere WHERE id = ?", (bruker_id,))
    db.commit()
    db.close()
    flash("Bruker slettet.", "ok")
    return redirect(url_for("admin"))


if __name__ == "__main__":
    opprett_database()
    app.run(debug=True)
