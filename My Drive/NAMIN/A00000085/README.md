# Tidrapporteringssystem för Konsulter

Ett komplett webbaserat tidrapporteringssystem utvecklat med Flask för konsulter att registrera och hantera sin arbetstid.

## Funktioner

### För Användare
- **Användarregistrering och inloggning** - Säker autentisering med Flask-Login
- **Dashboard** - Översikt över registrerad tid och statistik
- **Tidrapportering** - Lägg till arbetstimmar för olika klienter och projekt
- **Rapporter** - Visa och filtrera tidrapporter med diagram och statistik
- **Export** - Exportera tidrapporter till CSV

### För Administratörer
- **Användarhantering** - Hantera användarkonton och behörigheter
- **Klienthantering** - Lägg till och hantera klienter
- **Projekthantering** - Skapa projekt kopplade till klienter
- **Systemöversikt** - Statistik och överblick över hela systemet

## Teknisk Stack

- **Backend**: Flask (Python)
- **Databas**: SQLite med SQLAlchemy ORM
- **Frontend**: Bootstrap 5, HTML5, CSS3, JavaScript
- **Autentisering**: Flask-Login
- **Diagram**: Chart.js

## Installation och Setup

### Förutsättningar
- Python 3.8 eller senare
- pip (Python package manager)

### Steg 1: Klona/ladda ner projektet
Alla filer finns redan i mappen: `c:\Users\Ali Eghtedari\My Drive\NAMIN\A00000081`

### Steg 2: Installera dependencies
Öppna PowerShell i projektmappen och kör:
```powershell
pip install -r requirements.txt
```

### Steg 3: Starta applikationen
```powershell
python app.py
```

Systemet kommer att:
- Skapa SQLite-databasen (`tidrapportering.db`) automatiskt
- Skapa ett admin-konto: `admin@tidrapport.se` / `admin123`
- Starta webbservern på `http://localhost:5000`

### Steg 4: Åtkomst till systemet
1. Öppna webbläsare och gå till: `http://localhost:5000`
2. Logga in med admin-kontot eller registrera ett nytt konto
3. Börja använda systemet!

## Mappstruktur

```
A00000081/
├── app.py                 # Huvudapplikation
├── requirements.txt       # Python-dependencies
├── README.md             # Denna fil
├── tidrapportering.db    # SQLite-databas (skapas automatiskt)
├── templates/            # HTML-mallar
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── time_entry.html
│   ├── reports.html
│   └── admin/
│       ├── dashboard.html
│       ├── users.html
│       └── clients.html
└── static/
    ├── css/
    │   └── style.css     # Anpassade stilar
    └── js/
        └── main.js       # JavaScript-funktionalitet
```

## Användning

### För nya användare
1. Gå till startsidan
2. Klicka på "Registrera"
3. Fyll i namn, e-post och lösenord
4. Logga in med dina uppgifter

### Registrera arbetstid
1. Logga in och gå till Dashboard
2. Klicka på "Ny tidrapport"
3. Välj datum, klient, projekt (om tillämpligt)
4. Ange antal timmar och beskrivning
5. Klicka "Spara tidrapport"

### Visa rapporter
1. Gå till "Rapporter" i menyn
2. Filtrera efter datum eller klient
3. Se statistik och diagram
4. Exportera till CSV om önskat

### Administration (endast för admins)
1. Logga in som admin
2. Gå till "Admin" i menyn
3. Hantera användare, klienter och projekt
4. Se systemstatistik

## Säkerhet

- Lösenord hashas med Werkzeug's säkra hash-funktion
- Session-baserad autentisering med Flask-Login
- CSRF-skydd genom Flask's inbyggda funktionalitet
- SQL-injection skydd genom SQLAlchemy ORM

## Anpassning

### Ändra admin-konto
Redigera följande rader i `app.py` (rad ~180):
```python
admin = User(
    name='Ditt namn',
    email='din@email.se',
    password_hash=generate_password_hash('ditt_lösenord'),
    is_admin=True
)
```

### Lägg till nya klienter programmatiskt
I `app.py`, lägg till efter admin-användaren:
```python
client = Client(name='Klientnamn', description='Beskrivning')
db.session.add(client)
```

### Anpassa utseende
- Redigera `static/css/style.css` för stiländringar
- Modifiera HTML-mallar i `templates/` mappen
- Lägg till JavaScript i `static/js/main.js`

## Utveckling och utökning

### Lägg till nya funktioner
1. Skapa nya rutter i `app.py`
2. Lägg till HTML-mallar i `templates/`
3. Uppdatera navigation i `base.html`

### Databasändringar
1. Modifiera modellerna i `app.py`
2. Ta bort `tidrapportering.db`
3. Starta om applikationen för att skapa ny databas

## Felsökning

### Vanliga problem

**"ModuleNotFoundError"**
- Kör: `pip install -r requirements.txt`

**"Database is locked"**
- Stäng applikationen helt och starta om

**"Port already in use"**
- Ändra port i `app.py`: `app.run(port=5001)`

**Kan inte logga in**
- Kontrollera att admin-kontot skapats
- Kolla konsolen för felmeddelanden

### Loggar och debugging
- Aktivera debug-läge: `app.run(debug=True)`
- Kontrollera konsolen för felmeddelanden
- Använd webbläsarens utvecklarverktyg

## Support och kontakt

För frågor och support angående detta system:
- Kontakta systemutvecklaren
- Se dokumentation i koden
- Använd webbläsarens utvecklarverktyg för felsökning

## Licens

Utvecklat för NAMIN konsultverksamhet. Alla rättigheter förbehållna.

---

**Version**: 1.0  
**Skapad**: November 2025  
**Utvecklare**: AI Assistant för NAMIN  
**Plattform**: Windows/Python/Flask