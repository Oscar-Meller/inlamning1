from flask import Flask, render_template, request, session
import mysql.connector
from mysql.connector import Error
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Genererar en slumpmässig 24-byte nyckel

# Databaskonfiguration 
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',  
    'database': 'inlamning_1'
}

def get_db_connection():
    """Skapa och returnera en databasanslutning"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"Fel vid anslutning till MySQL: {e}")
        return None

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')  # Hämtar username från POST-data
        password = request.form.get('password')  # Hämtar password från POST-data
        
        # Anslut till databasen
        connection = get_db_connection()
        if connection is None:
            return "Databasanslutning misslyckades", 500
        
        try:
            cursor = connection.cursor(dictionary=True)
            query = "SELECT * FROM users WHERE username = %s"
            cursor.execute(query, (username,))
            user = cursor.fetchone()  # Hämtar användaren från databasen
            
            if user and user['password'] == password:  # Kontrollerar att användaren finns och lösenordet matchar
                # Spara användarinfo i session
                session['logged_in'] = True
                session['user_id'] = user['id']
                session['username'] = user['username']
                return f'Inloggning lyckades! Välkommen {user["username"]}!'
            else:
                return ('Ogiltigt användarnamn eller lösenord', 401)

        except Error as e:
            print(f"Databasfel: {e}")
            return "Databasfel inträffade", 500
        
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

if __name__ == '__main__':
    app.run(debug=True)