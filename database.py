import mysql.connector

# Connect to the MySQL database
def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="dineshbtech26@gmail",
        password="Dinesh@9080",
        database="sparkhub"
    )

# Function to create the database table
def create_table():
    db = connect_db()
    cursor = db.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL,
            password VARCHAR(255) NOT NULL
        )
    ''')
    db.close()

# Function to insert a new user into the database
def insert_user(username, email, password):
    db = connect_db()
    cursor = db.cursor()
    cursor.execute('''
        INSERT INTO users (username, email, password)
        VALUES (%s, %s, %s)
    ''', (username, email, password))
    db.commit()
    db.close()

# Function to retrieve a user by email
def get_user_by_email(email):
    db = connect_db()
    cursor = db.cursor()
    cursor.execute('''
        SELECT * FROM users WHERE email = %s
    ''', (email,))
    user = cursor.fetchone()
    db.close()
    return user
