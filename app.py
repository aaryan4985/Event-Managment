from flask import Flask, render_template, request, redirect
from flask_mysqldb import MySQL
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Database Config from .env
app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB')

mysql = MySQL(app)

# Home Page - List Events
@app.route('/')
def index():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM events")
    events = cur.fetchall()
    cur.close()
    return render_template('index.html', events=events)

# Add Event
@app.route('/add', methods=['POST'])
def add_event():
    name = request.form['name']
    date = request.form['date']
    location = request.form['location']

    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO events (name, date, location) VALUES (%s, %s, %s)", (name, date, location))
    mysql.connection.commit()
    cur.close()
    return redirect('/')

# Edit Event
@app.route('/edit/<int:event_id>', methods=['GET', 'POST'])
def edit_event(event_id):
    cur = mysql.connection.cursor()
    
    if request.method == 'POST':
        name = request.form['name']
        date = request.form['date']
        location = request.form['location']
        cur.execute("UPDATE events SET name=%s, date=%s, location=%s WHERE id=%s", (name, date, location, event_id))
        mysql.connection.commit()
        cur.close()
        return redirect('/')
    
    cur.execute("SELECT * FROM events WHERE id = %s", (event_id,))
    event = cur.fetchone()
    cur.close()
    return render_template('edit.html', event=event)

# Delete Event
@app.route('/delete/<int:event_id>')
def delete_event(event_id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM events WHERE id = %s", (event_id,))
    mysql.connection.commit()
    cur.close()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
