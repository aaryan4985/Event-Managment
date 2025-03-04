from flask import Flask, render_template, request, redirect, Response, flash
from flask_mysqldb import MySQL
from dotenv import load_dotenv
import os
import csv
import re

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your_fallback_secret_key')

# Database Configuration
app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB')

mysql = MySQL(app)

def validate_event_input(name, date, location):
    """Validate event input fields."""
    errors = []
    
    # Name validation
    if not name or len(name) < 3:
        errors.append("Event name must be at least 3 characters long.")
    
    # Date validation (basic check)
    if not date:
        errors.append("Date is required.")
    
    # Location validation
    if not location or len(location) < 2:
        errors.append("Location must be at least 2 characters long.")
    
    return errors

def validate_registration_input(name, email):
    """Validate registration input fields."""
    errors = []
    
    # Name validation
    if not name or len(name) < 2:
        errors.append("Name must be at least 2 characters long.")
    
    # Email validation
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_regex, email):
        errors.append("Invalid email format.")
    
    return errors

# Home Page - List Events
@app.route('/')
def index():
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM events ORDER BY date")
        events = cur.fetchall()
        cur.close()
        return render_template('index.html', events=events)
    except Exception as e:
        flash(f"Error fetching events: {str(e)}", 'error')
        return render_template('index.html', events=[])

# Add Event
@app.route('/add', methods=['POST'])
def add_event():
    name = request.form['name']
    date = request.form['date']
    location = request.form['location']

    # Validate input
    input_errors = validate_event_input(name, date, location)
    if input_errors:
        for error in input_errors:
            flash(error, 'error')
        return redirect('/')

    try:
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO events (name, date, location) VALUES (%s, %s, %s)", (name, date, location))
        mysql.connection.commit()
        cur.close()
        flash("Event added successfully!", 'success')
    except Exception as e:
        flash(f"Error adding event: {str(e)}", 'error')
    
    return redirect('/')

# Edit Event
@app.route('/edit/<int:event_id>', methods=['GET', 'POST'])
def edit_event(event_id):
    cur = mysql.connection.cursor()

    if request.method == 'POST':
        name = request.form['name']
        date = request.form['date']
        location = request.form['location']

        # Validate input
        input_errors = validate_event_input(name, date, location)
        if input_errors:
            for error in input_errors:
                flash(error, 'error')
            return redirect(f'/edit/{event_id}')

        try:
            cur.execute("UPDATE events SET name=%s, date=%s, location=%s WHERE id=%s", (name, date, location, event_id))
            mysql.connection.commit()
            flash("Event updated successfully!", 'success')
            return redirect('/')
        except Exception as e:
            flash(f"Error updating event: {str(e)}", 'error')

    try:
        cur.execute("SELECT * FROM events WHERE id = %s", (event_id,))
        event = cur.fetchone()
        cur.close()
        return render_template('edit.html', event=event)
    except Exception as e:
        flash(f"Error fetching event: {str(e)}", 'error')
        return redirect('/')

# Delete Event
@app.route('/delete/<int:event_id>')
def delete_event(event_id):
    try:
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM events WHERE id = %s", (event_id,))
        mysql.connection.commit()
        cur.close()
        flash("Event deleted successfully!", 'success')
    except Exception as e:
        flash(f"Error deleting event: {str(e)}", 'error')
    
    return redirect('/')

# Search Event
@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '')
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM events WHERE name LIKE %s OR location LIKE %s", (f"%{query}%", f"%{query}%"))
        events = cur.fetchall()
        cur.close()
        return render_template('index.html', events=events, query=query)
    except Exception as e:
        flash(f"Error searching events: {str(e)}", 'error')
        return redirect('/')

# Register for Event
@app.route('/register', methods=['POST'])
def register():
    event_id = request.form['event_id']
    name = request.form['name']
    email = request.form['email']

    # Validate input
    input_errors = validate_registration_input(name, email)
    if input_errors:
        for error in input_errors:
            flash(error, 'error')
        return redirect('/')

    try:
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO registrations (event_id, name, email) VALUES (%s, %s, %s)", (event_id, name, email))
        mysql.connection.commit()
        cur.close()
        flash("Registration successful!", 'success')
    except Exception as e:
        flash(f"Error registering for event: {str(e)}", 'error')
    
    return redirect('/')

@app.route("/registrations")
def view_registrations():
    try:
        cur = mysql.connection.cursor()
        cur.execute("""
            SELECT registrations.id, events.name AS event_name, registrations.name, registrations.email 
            FROM registrations 
            JOIN events ON registrations.event_id = events.id
            ORDER BY events.name
        """)
        registrations = cur.fetchall()
        cur.close()
        return render_template("registrations.html", registrations=registrations)
    except Exception as e:
        flash(f"Error fetching registrations: {str(e)}", 'error')
        return redirect('/')

# Export Events as CSV
@app.route('/export')
def export():
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM events ORDER BY date")
        events = cur.fetchall()
        cur.close()

        output = []
        output.append(['ID', 'Name', 'Date', 'Location'])
        for event in events:
            output.append([event[0], event[1], event[2], event[3]])

        csv_output = '\n'.join([','.join(map(str, row)) for row in output])

        return Response(csv_output, mimetype="text/csv", headers={"Content-Disposition": "attachment;filename=events.csv"})
    except Exception as e:
        flash(f"Error exporting events: {str(e)}", 'error')
        return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)