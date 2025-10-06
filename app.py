import sqlite3
import os
from flask import Flask, render_template, request, redirect, url_for, session, flash, g
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'default_fallback_secret')

DATABASE = 'database.db'
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')

def add_user(username, email, password, full_name=None, phone=None):
    db = get_db()
    pw_hash = generate_password_hash(password)
    cur = db.cursor()
    try:
        cur.execute(
            "INSERT INTO users (username, email, password_hash, full_name, phone) VALUES (?, ?, ?, ?, ?)",
            (username, email, pw_hash, full_name, phone)
        )
        db.commit()
        return cur.lastrowid
    except sqlite3.IntegrityError:
        return None


def get_user_by_username(username):
    db = get_db()
    cur = db.execute("SELECT * FROM users WHERE username = ?", (username,))
    return cur.fetchone()


def get_user_by_id(user_id):
    db = get_db()
    cur = db.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    return cur.fetchone()


def update_user_info(user_id, full_name, phone):
    db = get_db()
    db.execute(
        "UPDATE users SET full_name = ?, phone = ? WHERE id = ?",
        (full_name, phone, user_id)
    )
    db.commit()

@app.route('/register_user', methods=['GET', 'POST'])
def register_user():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        full_name = request.form.get('full_name')
        phone = request.form.get('phone')

        existing_user = get_user_by_username(username)
        if existing_user:
            flash('Username already exists.', 'danger')
            return render_template('register_user.html')

        user_id = add_user(username, email, password, full_name, phone)
        if user_id:
            flash('Registration successful, please log in.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Error while registering, please try again.', 'danger')
    return render_template('register_user.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    session.pop('_flashes', None)
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = get_user_by_username(username)
        if user is None:
            flash('User does not exist.', 'danger')
        elif not check_password_hash(user['password_hash'], password):
            flash('Wrong password.', 'danger')
        else:
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash(f'Welcome {user["username"]}!', 'success')
            return redirect(url_for('home'))
    
    return render_template('login.html')



@app.route('/logout')
def logout():
    session.clear()
    flash('You were logged out.', 'info')
    return redirect(url_for('home'))


def user_registered(event_id, user_id):
    db = get_db()
    cur = db.execute('SELECT 1 FROM registrants WHERE event_id = ? AND user_id = ?', (event_id, user_id))
    return cur.fetchone() is not None


@app.route('/unregister/<int:event_id>', methods=['POST'])
def unregister(event_id):
    if not session.get('user_id'):
        return redirect(url_for('login'))
    user_id = session['user_id']

    db = get_db()
    db.execute('DELETE FROM registrants WHERE event_id = ? AND user_id = ?', (event_id, user_id))
    db.commit()
    flash('You have been unregistered from the event.', 'success')
    return redirect(url_for('my_events'))

def get_user_registrations(user_id):
    db = get_db()
    cur = db.execute("""
        SELECT events.*
        FROM events
        JOIN registrants ON events.id = registrants.event_id
        WHERE registrants.user_id = ?
    """, (user_id,))
    return cur.fetchall()


@app.route('/my_events')
def my_events():
    if not session.get('user_id'):
        flash('Please log in to view your registered events.')
        return redirect(url_for('login'))

    user_id = session['user_id']
    events = get_user_registrations(user_id)
    return render_template('my_events.html', events=events)


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        with open('schema.sql', 'r') as f:
            db.executescript(f.read())
        db.commit()

def add_event(name, date, venue, description):
    db = get_db()
    cur = db.cursor()
    cur.execute("INSERT INTO events (name, date, venue, description) VALUES (?, ?, ?, ?)",
                (name, date, venue, description))
    db.commit()
    return cur.lastrowid

def get_all_events():
    db = get_db()
    cur = db.execute("SELECT * FROM events")
    return cur.fetchall()

def get_event_by_id(event_id):
    db = get_db()
    cur = db.execute("SELECT * FROM events WHERE id = ?", (event_id,))
    return cur.fetchone()

def update_event(event_id, name, date, venue, description):
    db = get_db()
    db.execute("UPDATE events SET name = ?, date = ?, venue = ?, description = ? WHERE id = ?",
               (name, date, venue, description, event_id))
    db.commit()

def delete_event_by_id(event_id):
    db = get_db()
    db.execute("DELETE FROM events WHERE id = ?", (event_id,))
    db.commit()

def add_registrant(event_id, user_id, name, email, phone):
    db = get_db()
    cur = db.cursor()
    cur.execute("INSERT INTO registrants (event_id, user_id, name, email, phone) VALUES (?, ?, ?, ?, ?)",
                (event_id, user_id, name, email, phone))
    db.commit()
    return cur.lastrowid

def get_registrants_by_event(event_id):
    db = get_db()
    cur = db.execute("SELECT * FROM registrants WHERE event_id = ?", (event_id,))
    return cur.fetchall()

def get_registrant_by_id(reg_id):
    db = get_db()
    cur = db.execute("SELECT * FROM registrants WHERE id = ?", (reg_id,))
    return cur.fetchone()

def update_registrant(reg_id, name, email, phone):
    db = get_db()
    db.execute("UPDATE registrants SET name = ?, email = ?, phone = ? WHERE id = ?",
               (name, email, phone, reg_id))
    db.commit()

def delete_registrant_by_id(reg_id):
    db = get_db()
    db.execute("DELETE FROM registrants WHERE id = ?", (reg_id,))
    db.commit()

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == ADMIN_PASSWORD:
            session['admin'] = True
            return redirect(url_for('dashboard'))
        else:
            return render_template('admin_login.html', error='Invalid password')
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin', None)
    return redirect(url_for('admin'))

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if not session.get('admin'):
        return redirect(url_for('admin'))

    if request.method == 'POST':
        name = request.form.get('event_name')
        date = request.form.get('event_date')
        venue = request.form.get('event_venue')
        description = request.form.get('event_description')
        add_event(name, date, venue, description)
        flash('Event added successfully.', 'success')

    events = get_all_events()
    registrations_by_event = {}
    for event in events:
        registrations_by_event[event['id']] = get_registrants_by_event(event['id'])

    return render_template('dashboard.html', events=events, registrations_by_event=registrations_by_event)

@app.route('/admin/delete_event/<int:event_id>', methods=['POST'])
def delete_event(event_id):
    if not session.get('admin'):
        return redirect(url_for('admin'))
    delete_event_by_id(event_id)  # call helper, not route
    flash('Event deleted successfully.', 'success')
    return redirect(url_for('dashboard'))


@app.route('/admin/delete_registrant/<int:event_id>/<int:reg_index>', methods=['POST'])
def delete_registrant(event_id, reg_index):
    if not session.get('admin'):
        return redirect(url_for('admin'))

    registrants = get_registrants_by_event(event_id)
    if reg_index < 0 or reg_index >= len(registrants):
        flash('Invalid registrant.', 'danger')
        return redirect(url_for('dashboard'))

    reg_id = registrants[reg_index]['id']
    delete_registrant_by_id(reg_id)
    flash('Registrant deleted.', 'success')
    # Redirect back to the event detail page, not the dashboard
    return redirect(url_for('admin_event_detail', event_id=event_id))


@app.route('/admin/edit_event/<int:event_id>', methods=['GET', 'POST'])
def edit_event(event_id):
    if not session.get('admin'):
        return redirect(url_for('admin'))

    event = get_event_by_id(event_id)
    if not event:
        return "Event not found", 404

    if request.method == 'POST':
        name = request.form.get('event_name')
        date = request.form.get('event_date')
        venue = request.form.get('event_venue')
        description = request.form.get('event_description')
        update_event(event_id, name, date, venue, description)
        flash('Event updated successfully.', 'success')
        return redirect(url_for('dashboard'))

    return render_template('edit_event.html', event=event)

@app.route('/admin/edit_registrant/<int:event_id>/<int:reg_index>', methods=['GET', 'POST'])
def edit_registrant(event_id, reg_index):
    if not session.get('admin'):
        return redirect(url_for('admin'))

    registrants = get_registrants_by_event(event_id)
    if reg_index < 0 or reg_index >= len(registrants):
        return "Registrant not found", 404

    reg = registrants[reg_index]

    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        update_registrant(reg['id'], name, email, phone)
        flash('Registrant updated successfully.', 'success')
        # Redirect back to the event detail page
        return redirect(url_for('admin_event_detail', event_id=event_id))

    return render_template('edit_registrant.html', reg=reg, event_id=event_id, reg_index=reg_index)


@app.route('/')
def home():
    events = get_all_events()
    return render_template('index.html', events=events)

@app.route('/register')
def register():
    if not session.get('user_id'):
        flash('Please log in to register for events.')
        return redirect(url_for('login'))

    event_id = request.args.get('event_id', type=int)
    event = get_event_by_id(event_id)
    if not event:
        return "Event not found", 404

    registered = user_registered(event_id, session['user_id'])
    user = get_user_by_id(session['user_id'])
    return render_template('register.html', event=event, registered=registered, user=user)


@app.route('/submit', methods=['POST'])
def submit():
    if not session.get('user_id'):
        flash('Please log in to register.')
        return redirect(url_for('login'))

    user_id = session['user_id']
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    event_id = request.form.get('event_id', type=int)

    if not all([name, email, phone, event_id]):
        return "Invalid input", 400

    if len(phone) != 10 or not phone.isdigit():
        return "Invalid phone number", 400

    # Update user info in DB
    update_user_info(user_id, name, phone)

    if user_registered(event_id, user_id):
        flash('Already registered for this event!', 'warning')
        return redirect(url_for('register', event_id=event_id))

    add_registrant(event_id, user_id, name, email, phone)

    return redirect(url_for('success', name=name))


@app.route('/admin/event/<int:event_id>')
def admin_event_detail(event_id):
    if not session.get('admin'):
        return redirect(url_for('admin'))

    event = get_event_by_id(event_id)
    if not event:
        return "Event not found", 404

    registrants = get_registrants_by_event(event_id)
    return render_template('event_detail.html', event=event, registrants=registrants)


@app.route('/success')
def success():
    name = request.args.get('name', '')
    return render_template('success.html', name=name)

if __name__ == '__main__':
    # Uncomment this line and run once to initialize your database tables
    # init_db()
    app.run(debug=True)
