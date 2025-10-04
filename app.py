from flask import Flask, render_template, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Temporary in-memory storage for registrations
registrations = []

events = [
    {
        'id': 1,
        'name': 'Tech Conference',
        'date': '2025-10-30',
        'venue': 'City Conference Hall',
        'description': 'Latest technology trends and networking.'
    }
]


@app.route('/')
def home():
    return render_template('index.html', events=events)


@app.route('/register')
def register():
    event_id = request.args.get('event_id', type=int)
    event = next((e for e in events if e['id'] == event_id), None)
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

    event = next((e for e in events if e['id'] == event_id), None)
    if not event:
        return "Event not found", 404

    registration = {'name': name, 'email': email, 'phone': phone, 'event_id': event_id}
    registrations.append(registration)

    return redirect(url_for('success', name=name))


@app.route('/success')
def success():
    name = request.args.get('name', 'Visitor')
    return render_template('success.html', name=name)


ADMIN_PASSWORD = 'admin123'

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


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if not session.get('admin'):
        return redirect(url_for('admin'))
    if request.method == 'POST':
        eid = len(events) + 1
        name = request.form.get('event_name')
        date = request.form.get('event_date')
        venue = request.form.get('event_venue')
        description = request.form.get('event_description')
        events.append({
            'id': eid,
            'name': name,
            'date': date,
            'venue': venue,
            'description': description
        })
    # Group registrations by event_id
    registrations_by_event = {}
    for event in events:
        registrations_by_event[event['id']] = [r for r in registrations if r['event_id'] == event['id']]
    return render_template('dashboard.html', events=events, registrations_by_event=registrations_by_event)


@app.route('/admin/logout')
def admin_logout():
    session.pop('admin', None)  # Remove admin login flag from session
    # flash('You have been logged out successfully.', 'info')
    return redirect(url_for('admin'))  # Redirect to admin login page


# Delete event by ID
@app.route('/admin/delete_event/<int:event_id>', methods=['POST'])
def delete_event(event_id):
    if not session.get('admin'):
        return redirect(url_for('admin'))
    global events, registrations
    events = [e for e in events if e['id'] != event_id]
    # Also remove registrations linked to this event
    registrations = [r for r in registrations if r['event_id'] != event_id]
    flash('Event and related registrations deleted.', 'success')
    return redirect(url_for('dashboard'))

# Delete registrant by index or unique id (for simplicity, by index)
@app.route('/admin/delete_registrant/<int:event_id>/<int:reg_index>', methods=['POST'])
def delete_registrant(event_id, reg_index):
    if not session.get('admin'):
        return redirect(url_for('admin'))
    regs = [r for r in registrations if r['event_id'] == event_id]
    if reg_index < 0 or reg_index >= len(regs):
        flash('Invalid registrant.', 'danger')
        return redirect(url_for('dashboard'))

    # Remove registrant from main registrations list
    reg_to_delete = regs[reg_index]
    registrations.remove(reg_to_delete)
    flash('Registrant deleted.', 'success')
    return redirect(url_for('dashboard'))

# Update routes would normally need forms:
# For simplicity, let's add redirect to update pages or implement inline later.


@app.route('/admin/edit_event/<int:event_id>', methods=['GET', 'POST'])
def edit_event(event_id):
    if not session.get('admin'):
        return redirect(url_for('admin'))

    event = next((e for e in events if e['id'] == event_id), None)
    if not event:
        return "Event not found", 404

    if request.method == 'POST':
        event['name'] = request.form.get('event_name')
        event['date'] = request.form.get('event_date')
        event['venue'] = request.form.get('event_venue')
        event['description'] = request.form.get('event_description')
        flash('Event updated successfully.', 'success')
        return redirect(url_for('dashboard'))

    return render_template('edit_event.html', event=event)


@app.route('/admin/edit_registrant/<int:event_id>/<int:reg_index>', methods=['GET', 'POST'])
def edit_registrant(event_id, reg_index):
    if not session.get('admin'):
        return redirect(url_for('admin'))

    regs = [r for r in registrations if r['event_id'] == event_id]
    if reg_index < 0 or reg_index >= len(regs):
        return "Registrant not found", 404

    reg = regs[reg_index]

    if request.method == 'POST':
        reg['name'] = request.form.get('name')
        reg['email'] = request.form.get('email')
        reg['phone'] = request.form.get('phone')
        flash('Registrant updated successfully.', 'success')
        return redirect(url_for('dashboard'))

    return render_template('edit_registrant.html', reg=reg, event_id=event_id, reg_index=reg_index)



if __name__ == '__main__':
    app.run(debug=True)
