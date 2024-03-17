# -*- coding: utf-8 -*-

from flask import Flask, render_template, request, redirect, session
from google_auth_oauthlib.flow import InstalledAppFlow
import mysql.connector
import hashlib
import os
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

app = Flask(__name__)
app.secret_key = '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'

# Function to connect to the MySQL database
def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="dineshbtech26@gmail.com",
        password="Dinesh@9080",
        database="sparkhub"
    )

# Function to create the database table
def create_table():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL,
            password VARCHAR(255) NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Function to insert a new user into the database
def insert_user(username, email, password):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO users (username, email, password)
        VALUES (%s, %s, %s)
    ''', (username, email, password))
    conn.commit()
    conn.close()

# Function to retrieve a user by email
def get_user_by_email(email):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM users WHERE email = %s
    ''', (email,))
    user = cursor.fetchone()
    conn.close()
    return user

# Function to hash a password
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Create the database table when the application starts
create_table()

@app.route('/')
def index():
    access_token = session.get('access_token')
    channel_data = session.get('channel_data')
    return render_template('index.html', channel_data=channel_data)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = hash_password(request.form['password'])
        insert_user(username, email, password)
        return redirect('/login')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = hash_password(request.form['password'])

        user = get_user_by_email(email)
        if user and user[3] == password:
            session['loggedin'] = True
            session['id'] = user[0]
            session['username'] = user[1]
            # Fetch channel details using the access token
            access_token = session.get('access_token')
            if access_token:
                youtube = get_authenticated_service()
                channel_data = get_channel_data(youtube)
                session['channel_data'] = channel_data
            return redirect('/influencer')
        else:
            return 'Invalid email/password combination'

    return render_template('login.html')

@app.route('/profile')
def profile():
    if 'loggedin' in session:
        return render_template('profile.html', username=session['username'])
    else:
        return redirect('/login')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/influencer')
def influencer():
    if 'loggedin' in session:
        return render_template('influencer.html', username=session['username'])
    else:
        return redirect('/login')

@app.route('/influencer_channels')
def influencer_channels():
    if 'loggedin' in session:
        youtube = get_authenticated_service()
        channel_data = get_channel_data(youtube)
        return render_template('influencer_channels.html', channel_data=channel_data)
    else:
        return redirect('/login')

@app.route('/oauth2callback')
def oauth2callback():
    access_token = request.args.get('access_token')
    if access_token:
        session['access_token'] = access_token
        return redirect('/influencer_channels')  # Redirect to influencer_channels page
    return redirect('/')

def get_authenticated_service():
    scopes = ["https://www.googleapis.com/auth/youtube.readonly"]

    flow = InstalledAppFlow.from_client_secrets_file(
        "client_secret.json", scopes=scopes
    )

    # Run the OAuth flow using a local server
    credentials = flow.run_local_server()

    # Build the YouTube service using the credentials
    youtube = build("youtube", "v3", credentials=credentials)

    return youtube

def get_channel_data(youtube):
    request = youtube.channels().list(
        part="snippet", 
        mine=True
    )   
    response = request.execute()
    if 'items' in response:
        return response['items'][0]  # Assuming only one channel is returned
    else:
        return None
    from flask import render_template

@app.route('/campaigns')
def campaigns():
    return render_template('campaigns.html')

@app.route('/get_channel_details')
def get_channel_details():
    scopes = ["https://www.googleapis.com/auth/youtube.readonly"]

    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"
    client_secrets_file = "clienr_secret.json"

    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        client_secrets_file, scopes)
    credentials = flow.run_console()
    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, credentials=credentials)

    request = youtube.channels().list(
        part="snippet,contentDetails,statistics",
        id="UC_x5XG1OV2P6uZZ5FSM9Ttw"
    )
    response = request.execute()

    return response  # You might want to return this data in a more structured format


if __name__ == '__main__':
    app.run(debug=True)
