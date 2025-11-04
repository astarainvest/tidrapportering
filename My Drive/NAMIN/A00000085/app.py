from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
from functools import wraps

app = Flask(__name__)

# Konfiguration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'din-hemliga-nyckel-här-byt-ut-denna'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or 'sqlite:///tidrapportering.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Sessionskonfiguration - användare loggas ut vid serveromstart
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=8)  # 8 timmars session
app.permanent_session_lifetime = timedelta(hours=8)

# Initialisera extensions
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Vänligen logga in för att komma åt denna sida.'

# Databasmodeller
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relation till tidrapporter
    time_entries = db.relationship('TimeEntry', backref='user', lazy=True)
    
    def __repr__(self):
        return f'<User {self.name}>'

class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationer
    projects = db.relationship('Project', backref='client', lazy=True)
    time_entries = db.relationship('TimeEntry', backref='client', lazy=True)
    
    def __repr__(self):
        return f'<Client {self.name}>'

class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    active = db.Column(db.Boolean, default=True)
    hourly_rate = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relation till tidrapporter
    time_entries = db.relationship('TimeEntry', backref='project', lazy=True)
    
    def __repr__(self):
        return f'<Project {self.name}>'

class TimeEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'), nullable=True)
    date = db.Column(db.Date, nullable=False)
    hours = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<TimeEntry {self.date} - {self.hours}h>'

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

def admin_required(f):
    """Decorator för att kräva admin-behörighet"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Du har inte behörighet att komma åt denna sida.', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# Rutter
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user, remember=False)  # Sessionen är inte permanent
            session.permanent = False  # Säkerställ att sessionen inte är permanent
            flash('Inloggning lyckades!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('Felaktig e-post eller lösenord.', 'danger')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        # Validering
        if not name or len(name.strip()) < 2:
            flash('Namnet måste vara minst 2 tecken långt.', 'danger')
            return render_template('register.html')
        
        if not email or '@' not in email:
            flash('Ange en giltig e-postadress.', 'danger')
            return render_template('register.html')
        
        if len(password) < 6:
            flash('Lösenordet måste vara minst 6 tecken långt.', 'danger')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Lösenorden matchar inte.', 'danger')
            return render_template('register.html')
        
        # Kontrollera om användaren redan finns
        if User.query.filter_by(email=email).first():
            flash('E-postadressen är redan registrerad.', 'danger')
            return render_template('register.html')
        
        # Skapa ny användare
        user = User(
            name=name.strip(),
            email=email.lower().strip(),
            password_hash=generate_password_hash(password)
        )
        
        db.session.add(user)
        db.session.commit()
        
        flash('Registrering lyckades! Du kan nu logga in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Du har loggats ut.', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    import calendar
    
    # Hämta år och månad från query parameters
    now = datetime.now()
    year = int(request.args.get('year', now.year))
    month = int(request.args.get('month', now.month))
    
    # Begränsa navigation till innevarande månad
    current_year = now.year
    current_month = now.month
    
    if year > current_year or (year == current_year and month > current_month):
        year = current_year
        month = current_month
    
    if year < 2025:
        year = 2025
        month = 1
    
    # Hämta timmar per klient för aktuell månad
    from sqlalchemy import func
    client_hours = db.session.query(
        Client.name.label('client_name'),
        func.sum(TimeEntry.hours).label('total_hours')
    ).join(TimeEntry, Client.id == TimeEntry.client_id) \
     .filter(
         TimeEntry.user_id == current_user.id,
         TimeEntry.date >= datetime(year, month, 1).date(),
         TimeEntry.date <= (datetime(year, month + 1, 1).date() - timedelta(days=1)) if month < 12 else datetime(year, 12, 31).date()
     ) \
     .group_by(Client.id, Client.name) \
     .order_by(func.sum(TimeEntry.hours).desc()) \
     .all()
    
    # Historiken flyttas till rapportsidan
    client_history = {}
    
    # Beräkna statistik
    today = now.date()
    
    # Dagens timmar
    hours_today = db.session.query(db.func.sum(TimeEntry.hours)).filter_by(
        user_id=current_user.id, date=today
    ).scalar() or 0
    
    # Timmar för den visade månaden (inte nödvändigtvis nuvarande månaden)
    month_start = datetime(year, month, 1).date()
    if month == 12:
        month_end = datetime(year + 1, 1, 1).date() - timedelta(days=1)
    else:
        month_end = datetime(year, month + 1, 1).date() - timedelta(days=1)
    
    hours_this_month = db.session.query(db.func.sum(TimeEntry.hours)).filter(
        TimeEntry.user_id == current_user.id,
        TimeEntry.date >= month_start,
        TimeEntry.date <= month_end
    ).scalar() or 0
    
    # Kalenderdata för vald månad
    
    cal = calendar.Calendar(firstweekday=0)
    month_days = cal.monthdayscalendar(year, month)
    
    # Hämta tidrapporter för aktuell månad
    month_start = datetime(year, month, 1).date()
    if month == 12:
        month_end = datetime(year + 1, 1, 1).date()
    else:
        month_end = datetime(year, month + 1, 1).date()
    
    month_entries = TimeEntry.query.filter(
        TimeEntry.user_id == current_user.id,
        TimeEntry.date >= month_start,
        TimeEntry.date < month_end
    ).all()
    
    # Organisera entries per datum
    entries_by_date = {}
    for entry in month_entries:
        date_str = entry.date.strftime('%Y-%m-%d')
        if date_str not in entries_by_date:
            entries_by_date[date_str] = []
        
        # Konvertera TimeEntry till dictionary för JSON serialisering
        entry_dict = {
            'id': entry.id,
            'hours': float(entry.hours),
            'description': entry.description or '',
            'client_name': entry.client.name if entry.client else 'Ingen klient',
            'project_name': entry.project.name if entry.project else 'Inget projekt'
        }
        entries_by_date[date_str].append(entry_dict)
    
    # Hämta klienter och projekt för kalender
    clients = Client.query.filter_by(active=True).all()
    projects = Project.query.filter_by(active=True).all()
    
    clients_json = [{'id': c.id, 'name': c.name} for c in clients]
    projects_json = [{'id': p.id, 'name': p.name, 'client_id': p.client_id} for p in projects]
    
    # Månadnamn på svenska
    month_names = [
        '', 'Januari', 'Februari', 'Mars', 'April', 'Maj', 'Juni',
        'Juli', 'Augusti', 'September', 'Oktober', 'November', 'December'
    ]
    
    return render_template('dashboard.html', 
                         client_hours=client_hours,
                         client_history=client_history,
                         hours_today=hours_today,
                         hours_this_month=hours_this_month,
                         month_days=month_days,
                         year=year,
                         month=month,
                         month_name=month_names[month],
                         entries_by_date=entries_by_date,
                         clients=clients_json,
                         projects=projects_json)

@app.route('/api/calendar_data')
@login_required
def calendar_data_api():
    from datetime import datetime, date
    from calendar import monthrange
    from flask import jsonify
    
    # Hämta månad och år från query parameters
    year = int(request.args.get('year', datetime.now().year))
    month = int(request.args.get('month', datetime.now().month))
    
    # Validera input
    if month < 1 or month > 12:
        return jsonify({'error': 'Invalid month'}), 400
    if year < 1900 or year > 2100:
        return jsonify({'error': 'Invalid year'}), 400
    
    # Beräkna första och sista dagen i månaden
    month_start = date(year, month, 1)
    _, last_day = monthrange(year, month)
    month_end = date(year, month, last_day)
    
    # Hämta entries för månaden
    month_entries = TimeEntry.query.filter(
        TimeEntry.user_id == current_user.id,
        TimeEntry.date >= month_start,
        TimeEntry.date <= month_end
    ).all()
    
    # Organisera entries per datum och beräkna statistik
    entries_by_date = {}
    hours_this_month = 0
    today_str = date.today().strftime('%Y-%m-%d')
    hours_today = 0
    
    for entry in month_entries:
        date_str = entry.date.strftime('%Y-%m-%d')
        if date_str not in entries_by_date:
            entries_by_date[date_str] = []
        
        entry_dict = {
            'id': entry.id,
            'hours': float(entry.hours),
            'description': entry.description or '',
            'client_name': entry.client.name if entry.client else 'Ingen klient',
            'project_name': entry.project.name if entry.project else 'Inget projekt'
        }
        entries_by_date[date_str].append(entry_dict)
        
        # Lägg till i månadstotal (alla entries för denna månad)
        hours_this_month += float(entry.hours)
        
        # Lägg till i dagstotal om det är idag OCH vi tittar på nuvarande månad
        if date_str == today_str:
            hours_today += float(entry.hours)
    
    # Månadnamn på svenska
    month_names = [
        '', 'Januari', 'Februari', 'Mars', 'April', 'Maj', 'Juni',
        'Juli', 'Augusti', 'September', 'Oktober', 'November', 'December'
    ]
    
    print(f"API Debug: År={year}, Månad={month}, Timmar denna månad={hours_this_month}, Timmar idag={hours_today}")
    
    return jsonify({
        'year': year,
        'month': month,
        'month_name': month_names[month],
        'entries_by_date': entries_by_date,
        'month_days': last_day,
        'hours_today': hours_today,
        'hours_this_month': hours_this_month
    })

@app.route('/calendar', methods=['GET', 'POST'])
@login_required
def calendar_view():
    # Hämta månad och år från query parameters, default till nuvarande månad
    from datetime import datetime
    import calendar
    
    year = int(request.args.get('year', datetime.now().year))
    month = int(request.args.get('month', datetime.now().month))
    
    # Skapa kalenderdata
    cal = calendar.Calendar(firstweekday=0)  # Måndag först
    month_days = cal.monthdayscalendar(year, month)
    
    # Hämta befintliga tidrapporter för månaden
    month_start = datetime(year, month, 1).date()
    if month == 12:
        month_end = datetime(year + 1, 1, 1).date()
    else:
        month_end = datetime(year, month + 1, 1).date()
    
    existing_entries = TimeEntry.query.filter(
        TimeEntry.user_id == current_user.id,
        TimeEntry.date >= month_start,
        TimeEntry.date < month_end
    ).all()
    
    # Organisera entries per datum
    entries_by_date = {}
    for entry in existing_entries:
        date_str = entry.date.strftime('%Y-%m-%d')
        if date_str not in entries_by_date:
            entries_by_date[date_str] = []
        entries_by_date[date_str].append(entry)
    
    # Hämta klienter och projekt
    clients = Client.query.filter_by(active=True).all()
    projects = Project.query.filter_by(active=True).all()
    
    # Konvertera till JSON-kompatibel format
    clients_json = [{'id': c.id, 'name': c.name} for c in clients]
    projects_json = [{'id': p.id, 'name': p.name, 'client_id': p.client_id} for p in projects]
    
    # Skapa månadnamn på svenska
    month_names = [
        '', 'Januari', 'Februari', 'Mars', 'April', 'Maj', 'Juni',
        'Juli', 'Augusti', 'September', 'Oktober', 'November', 'December'
    ]
    
    return render_template('calendar.html',
                         month_days=month_days,
                         year=year,
                         month=month,
                         month_name=month_names[month],
                         entries_by_date=entries_by_date,
                         clients=clients_json,
                         projects=projects_json)

@app.route('/time_entry', methods=['GET', 'POST'])
@login_required
def time_entry():
    # Redirect to calendar view
    if request.method == 'GET':
        return redirect(url_for('calendar_view'))
        
    if request.method == 'POST':
        try:
            # Validering av formulärdata
            client_id = request.form.get('client_id')
            project_id = request.form.get('project_id')
            date_str = request.form.get('date')
            hours_str = request.form.get('hours')
            description = request.form.get('description', '').strip()
            
            # Kontrollera obligatoriska fält
            if not client_id:
                flash('Du måste välja en klient.', 'danger')
                return redirect(url_for('time_entry'))
            
            if not date_str:
                flash('Du måste ange ett datum.', 'danger')
                return redirect(url_for('time_entry'))
            
            if not hours_str:
                flash('Du måste ange antal timmar.', 'danger')
                return redirect(url_for('time_entry'))
            
            if not description:
                flash('Du måste ange en beskrivning.', 'danger')
                return redirect(url_for('time_entry'))
            
            # Konvertera data
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
            hours = float(hours_str)
            
            # Validera timmar
            if hours <= 0 or hours > 24:
                flash('Antal timmar måste vara mellan 0.25 och 24.', 'danger')
                return redirect(url_for('time_entry'))
            
            # Kontrollera att klienten finns
            client = db.session.get(Client, client_id)
            if not client:
                flash('Vald klient finns inte.', 'danger')
                return redirect(url_for('time_entry'))
            
            # Skapa tidrapport
            entry = TimeEntry(
                user_id=current_user.id,
                client_id=int(client_id),
                project_id=int(project_id) if project_id else None,
                date=date,
                hours=hours,
                description=description
            )
            
            db.session.add(entry)
            db.session.commit()
            
            flash(f'Tidrapport sparad! {hours} timmar för {client.name}.', 'success')
            return redirect(url_for('dashboard'))
            
        except ValueError as e:
            flash('Felaktigt format på timmar eller datum.', 'danger')
            return redirect(url_for('time_entry'))
        except Exception as e:
            flash('Ett fel uppstod när tidrapporten skulle sparas. Försök igen.', 'danger')
            print(f"Error in time_entry: {e}")  # För debugging
            return redirect(url_for('time_entry'))
    
    # GET request - visa formulär
    clients = Client.query.filter_by(active=True).all()
    projects = Project.query.filter_by(active=True).all()
    
    # Kontrollera att det finns klienter
    if not clients:
        flash('Inga aktiva klienter hittades. Kontakta administratören för att lägga till klienter.', 'warning')
    
    return render_template('time_entry.html', clients=clients, projects=projects)

@app.route('/reports')
@login_required
def reports():
    entries = TimeEntry.query.filter_by(user_id=current_user.id).order_by(TimeEntry.date.desc()).all()
    
    # Hämta historisk översikt per månad/klient/projekt för rapportsidan
    historical_data = db.session.query(
        TimeEntry.date,
        Client.name.label('client_name'),
        Project.name.label('project_name'),
        TimeEntry.hours
    ).join(Client, TimeEntry.client_id == Client.id) \
     .outerjoin(Project, TimeEntry.project_id == Project.id) \
     .filter(TimeEntry.user_id == current_user.id) \
     .order_by(TimeEntry.date.desc()) \
     .all()
    
    # Organisera data per månad/klient/projekt
    month_names = [
        '', 'Januari', 'Februari', 'Mars', 'April', 'Maj', 'Juni',
        'Juli', 'Augusti', 'September', 'Oktober', 'November', 'December'
    ]
    
    # Gruppera per månad/klient/projekt
    monthly_summary = {}
    for record in historical_data:
        entry_date = record.date
        year_month = f"{entry_date.year}-{entry_date.month:02d}"
        month_display = f"{month_names[entry_date.month]} {entry_date.year}"
        client_name = record.client_name
        project_name = record.project_name or 'Inget projekt'
        
        key = (year_month, client_name, project_name)
        if key not in monthly_summary:
            monthly_summary[key] = {
                'month_display': month_display,
                'month_key': year_month,
                'client_name': client_name,
                'project_name': project_name,
                'total_hours': 0
            }
        monthly_summary[key]['total_hours'] += float(record.hours)
    
    # Konvertera till lista och sortera (senaste månader först)
    client_history = list(monthly_summary.values())
    client_history.sort(key=lambda x: (x['month_key'], x['client_name'], x['project_name']), reverse=True)
    
    # Hämta alla klienter och projekt för filter-dropdown
    all_clients = Client.query.filter_by(active=True).all()
    all_projects = Project.query.filter_by(active=True).all()
    
    # Hämta alla år som har tidrapporter
    available_years = db.session.query(
        db.extract('year', TimeEntry.date).label('year')
    ).filter(TimeEntry.user_id == current_user.id) \
     .distinct() \
     .order_by(db.desc('year')) \
     .all()
    
    years_list = [int(year.year) for year in available_years]
    
    return render_template('reports.html', 
                         entries=entries, 
                         client_history=client_history,
                         clients=all_clients,
                         projects=all_projects,
                         available_years=years_list)

@app.route('/export_csv')
@login_required
def export_csv():
    from flask import Response
    import io
    import csv
    from datetime import datetime
    
    # Hämta filter-parametrar
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to') 
    client_filter = request.args.get('client_filter')
    
    # Bygg query baserat på filter
    query = TimeEntry.query.filter_by(user_id=current_user.id)
    
    if date_from:
        try:
            from_date = datetime.strptime(date_from, '%Y-%m-%d').date()
            query = query.filter(TimeEntry.date >= from_date)
        except:
            pass
            
    if date_to:
        try:
            to_date = datetime.strptime(date_to, '%Y-%m-%d').date()
            query = query.filter(TimeEntry.date <= to_date)
        except:
            pass
            
    if client_filter:
        query = query.filter(TimeEntry.client_id == client_filter)
    
    entries = query.order_by(TimeEntry.date.desc()).all()
    
    # Skapa CSV
    output = io.StringIO()
    writer = csv.writer(output)
    
    # CSV headers
    writer.writerow(['Datum', 'Klient', 'Projekt', 'Timmar', 'Beskrivning', 'Skapad'])
    
    # CSV data
    for entry in entries:
        writer.writerow([
            entry.date.strftime('%Y-%m-%d'),
            entry.client.name if entry.client else 'Ingen klient',
            entry.project.name if entry.project else 'Inget projekt', 
            f"{entry.hours:.2f}",
            entry.description or '',
            entry.created_at.strftime('%Y-%m-%d %H:%M:%S')
        ])
    
    # Skapa response
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={
            'Content-Disposition': f'attachment; filename=tidrapporter_{datetime.now().strftime("%Y%m%d")}.csv'
        }
    )

@app.route('/export_historic_csv')
@login_required
def export_historic_csv():
    from flask import Response
    import io
    import csv
    from datetime import datetime
    from sqlalchemy import func, extract
    
    # Hämta filter-parametrar
    year = request.args.get('year')
    client_name = request.args.get('client')
    project_name = request.args.get('project')
    
    # Bygg query för månadsvis gruppering
    query = db.session.query(
        extract('year', TimeEntry.date).label('year'),
        extract('month', TimeEntry.date).label('month'),
        Client.name.label('client_name'),
        Project.name.label('project_name'),
        func.sum(TimeEntry.hours).label('total_hours')
    ).select_from(TimeEntry).join(Client).join(Project).filter(
        TimeEntry.user_id == current_user.id
    )
    
    # Tillämpa filter
    if year:
        query = query.filter(extract('year', TimeEntry.date) == int(year))
    
    if client_name:
        query = query.filter(Client.name.contains(client_name))
        
    if project_name:
        query = query.filter(Project.name.contains(project_name))
    
    # Gruppera och sortera
    historic_data = query.group_by(
        extract('year', TimeEntry.date),
        extract('month', TimeEntry.date),
        Client.name,
        Project.name
    ).order_by(
        extract('year', TimeEntry.date).desc(),
        extract('month', TimeEntry.date).desc(),
        Client.name,
        Project.name
    ).all()
    
    # Skapa CSV
    output = io.StringIO()
    writer = csv.writer(output)
    
    # CSV headers
    writer.writerow(['Månad', 'Klient', 'Projekt', 'Totalt timmar'])
    
    # CSV data
    for record in historic_data:
        month_display = f"{int(record.year)}-{int(record.month):02d}"
        writer.writerow([
            month_display,
            record.client_name,
            record.project_name,
            f"{record.total_hours:.1f}"
        ])
    
    # Skapa response
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={
            'Content-Disposition': f'attachment; filename=historisk_tidrapport_{datetime.now().strftime("%Y%m%d")}.csv'
        }
    )

# Admin-rutter
@app.route('/admin')
@login_required
@admin_required
def admin():
    users_count = User.query.count()
    clients_count = Client.query.count()
    projects_count = Project.query.count()
    total_hours = db.session.query(db.func.sum(TimeEntry.hours)).scalar() or 0
    
    return render_template('admin/dashboard.html',
                         users_count=users_count,
                         clients_count=clients_count,
                         projects_count=projects_count,
                         total_hours=total_hours)

@app.route('/admin/users')
@login_required
@admin_required
def admin_users():
    users = User.query.all()
    return render_template('admin/users.html', users=users)

@app.route('/admin/clients')
@login_required
@admin_required
def admin_clients():
    clients = Client.query.all()
    return render_template('admin/clients.html', clients=clients)

# API-endpoints för AJAX
@app.route('/api/save_time_entry', methods=['POST'])
@login_required
def save_time_entry():
    try:
        data = request.get_json()
        
        date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        client_id = int(data['client_id'])
        project_id = int(data['project_id']) if data.get('project_id') else None
        hours = float(data['hours'])
        description = data.get('description', '').strip()
        
        # Validering
        if hours <= 0 or hours > 24:
            return jsonify({'success': False, 'error': 'Timmar måste vara mellan 0.25 och 24'})
        
        # Beskrivning är valfri, sätt default om tom
        if not description:
            client = db.session.get(Client, client_id)
            description = f"Arbete för {client.name if client else 'Okänd klient'}"
        
        # Kontrollera om entry redan finns för detta datum, klient och projekt
        existing_entry = TimeEntry.query.filter_by(
            user_id=current_user.id,
            date=date,
            client_id=client_id,
            project_id=project_id
        ).first()
        
        if existing_entry:
            # Uppdatera befintlig
            existing_entry.hours = hours
            existing_entry.description = description
            existing_entry.updated_at = datetime.utcnow()
        else:
            # Skapa ny
            entry = TimeEntry(
                user_id=current_user.id,
                client_id=client_id,
                project_id=project_id,
                date=date,
                hours=hours,
                description=description
            )
            db.session.add(entry)
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Tidrapport sparad'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/delete_time_entry', methods=['POST'])
@login_required
def delete_time_entry():
    try:
        data = request.get_json()
        entry_id = int(data['entry_id'])
        
        entry = TimeEntry.query.filter_by(
            id=entry_id,
            user_id=current_user.id  # Säkerhet: bara egna entries
        ).first()
        
        if not entry:
            return jsonify({'success': False, 'error': 'Tidrapport hittades inte'})
        
        db.session.delete(entry)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Tidrapport borttagen'})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/projects/<int:client_id>')
@login_required
def get_projects_for_client(client_id):
    projects = Project.query.filter_by(client_id=client_id).all()
    return jsonify([{'id': p.id, 'name': p.name, 'client_id': p.client_id} for p in projects])

@app.route('/api/clients')
@login_required
def get_clients():
    clients = Client.query.filter_by(active=True).all()
    return jsonify([{'id': c.id, 'name': c.name} for c in clients])

@app.route('/api/users/<int:user_id>')
@login_required
@admin_required
def get_user_details(user_id):
    user = db.get_or_404(User, user_id)
    
    # Beräkna statistik
    total_hours = db.session.query(db.func.sum(TimeEntry.hours)).filter_by(user_id=user.id).scalar() or 0
    entries_count = TimeEntry.query.filter_by(user_id=user.id).count()
    last_entry = TimeEntry.query.filter_by(user_id=user.id).order_by(TimeEntry.created_at.desc()).first()
    
    return jsonify({
        'id': user.id,
        'name': user.name,
        'email': user.email,
        'is_admin': user.is_admin,
        'created_at': user.created_at.isoformat(),
        'time_entries_count': entries_count,
        'total_hours': float(total_hours),
        'last_activity': last_entry.created_at.isoformat() if last_entry else None
    })

@app.route('/get_day_entries')
@login_required
def get_day_entries():
    from datetime import datetime
    date_str = request.args.get('date')
    if not date_str:
        return jsonify({'success': False, 'error': 'Datum krävs'})
    
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
        entries = TimeEntry.query.filter_by(user_id=current_user.id, date=date).all()
        
        entries_data = []
        for entry in entries:
            entry_dict = {
                'id': entry.id,
                'hours': float(entry.hours),
                'description': entry.description or '',
                'client_name': entry.client.name if entry.client else 'Ingen klient',
                'project_name': entry.project.name if entry.project else 'Inget projekt'
            }
            entries_data.append(entry_dict)
        
        return jsonify({'success': True, 'entries': entries_data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    # Skapa databastabeller om de inte finns
    with app.app_context():
        db.create_all()
        
        # Skapa admin-användare om den inte finns
        admin_user = User.query.filter_by(email='admin@tidrapport.se').first()
        if not admin_user:
            admin = User(
                name='Administratör',
                email='admin@tidrapport.se',
                password_hash=generate_password_hash('admin123'),
                is_admin=True
            )
            db.session.add(admin)
            db.session.commit()
            print("Admin-användare skapad: admin@tidrapport.se / admin123")
        
        # Skapa exempel-klienter och projekt om de inte finns
        if Client.query.count() == 0:
            # Skapa klienter
            client1 = Client(
                name='NAMIN AB',
                description='Huvudklient för interna projekt och administration'
            )
            
            client2 = Client(
                name='Teknikföretaget XYZ',
                description='IT-konsultuppdrag för systemutveckling'
            )
            
            client3 = Client(
                name='Startup Innovation',
                description='Rådgivning och utveckling för startup-företag'
            )
            
            db.session.add_all([client1, client2, client3])
            db.session.commit()
            
            # Skapa projekt
            project1 = Project(
                name='Intern administration',
                description='Administration, möten och intern utveckling',
                client_id=client1.id,
                hourly_rate=800.0
            )
            
            project2 = Project(
                name='Tidrapporteringssystem',
                description='Utveckling av tidrapporteringssystem',
                client_id=client1.id,
                hourly_rate=950.0
            )
            
            project3 = Project(
                name='Webbutveckling',
                description='Frontend och backend utveckling',
                client_id=client2.id,
                hourly_rate=1200.0
            )
            
            project4 = Project(
                name='Systemarkitektur',
                description='Design och implementering av systemarkitektur',
                client_id=client2.id,
                hourly_rate=1500.0
            )
            
            project5 = Project(
                name='Produktstrategi',
                description='Strategisk rådgivning för produktutveckling',
                client_id=client3.id,
                hourly_rate=1100.0
            )
            
            db.session.add_all([project1, project2, project3, project4, project5])
            db.session.commit()
            
            print("Exempel-klienter och projekt skapade")
    
if __name__ == '__main__':
    # For local development
    app.run(debug=True, host='127.0.0.1', port=5000)