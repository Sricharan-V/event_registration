from flask import Flask, render_template, request, redirect, url_for

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
    return render_template('index.html')


@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/submit', methods=['POST'])
def submit():
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')

    # Simple server-side validation
    if not name or not email or not phone or len(phone) != 10 or not phone.isdigit():
        # Could redirect back with error message in real app
        return "Invalid input, please fill all fields correctly.", 400

    registration = {
        'name': name,
        'email': email,
        'phone': phone
    }
    registrations.append(registration)

    # Redirect to success page passing name info via query or session (simplified here)
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
        # Add a new event
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
    return render_template('dashboard.html', registrations=registrations, events=events)


if __name__ == '__main__':
    app.run(debug=True)
