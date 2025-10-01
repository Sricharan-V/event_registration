from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Temporary in-memory storage for registrations
registrations = []

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

if __name__ == '__main__':
    app.run(debug=True)
