from flask import Flask, render_template, request, redirect
from db import app, mysql

@app.route('/')
def index():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM events")
    events = cur.fetchall()
    cur.close()
    return render_template('index.html', events=events)

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

if __name__ == '__main__':
    app.run(debug=True)
