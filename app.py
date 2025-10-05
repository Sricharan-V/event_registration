import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash, g

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

DATABASE = 'database.db'
ADMIN_PASSWORD = 'admin123'

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

def add_registrant(event_id, name, email, phone):
    db = get_db()
    cur = db.cursor()
    cur.execute("INSERT INTO registrants (event_id, name, email, phone) VALUES (?, ?, ?, ?)",
                (event_id, name, email, phone))
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
        return redirect(url_for('dashboard'))

    return render_template('edit_registrant.html', reg=reg, event_id=event_id, reg_index=reg_index)

@app.route('/')
def home():
    events = get_all_events()
    return render_template('index.html', events=events)

@app.route('/register')
def register():
    event_id = request.args.get('event_id', type=int)
    event = get_event_by_id(event_id)
    if not event:
        return "Event not found", 404

    return render_template('register.html', event=event)

@app.route('/submit', methods=['POST'])
def submit():
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    event_id = request.form.get('event_id', type=int)

    if not name or not email or not phone or not event_id:
        return "Invalid input", 400

    if len(phone) != 10 or not phone.isdigit():
        return "Invalid phone number", 400

    event = get_event_by_id(event_id)
    if not event:
        return "Event not found", 404

    add_registrant(event_id, name, email, phone)

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
