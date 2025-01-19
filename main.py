from flask import Flask, request, jsonify, redirect, abort, render_template
from datetime import datetime, timedelta
import hashlib
import sqlite3
import os

app = Flask(__name__)
BASE_URL = "http://127.0.0.1:5000/"
DB_FILE = "url_shortener.db"

# -------------------- Database Operations --------------------

def init_db():
    """Initialize SQLite database with required tables."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS urls (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original_url TEXT NOT NULL,
            short_url TEXT UNIQUE NOT NULL,
            created_at DATETIME NOT NULL,
            expires_at DATETIME NOT NULL,
            password TEXT,
            name TEXT
        )''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS analytics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            short_url TEXT NOT NULL,
            access_time DATETIME NOT NULL,
            ip_address TEXT NOT NULL
        )''')
        conn.commit()

def add_url_to_db(original_url, short_url, expires_at, password=None, name=None):
    """Add a new URL entry to the database."""
    if password == '' or password is None:
        password = None

    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO urls (original_url, short_url, created_at, expires_at, password, name)
                         VALUES (?, ?, ?, ?, ?, ?)''',
                      (original_url, short_url, datetime.now().isoformat(), expires_at.isoformat(), password, name))
        conn.commit()

def get_url_from_db(short_url):
    """Retrieve URL data from database."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('''SELECT original_url, expires_at, password FROM urls WHERE short_url = ?''', (short_url,))
        return cursor.fetchone()

# -------------------- Analytics Operations --------------------

def log_analytics(short_url, ip_address):
    """Log URL access analytics."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO analytics (short_url, access_time, ip_address)
                          VALUES (?, ?, ?)''',
                       (short_url, datetime.now(), ip_address))
        conn.commit()

def get_analytics_from_db(short_url):
    """Retrieve analytics data for a specific URL."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('''SELECT access_time, ip_address FROM analytics WHERE short_url = ?''', (short_url,))
        return cursor.fetchall()

# -------------------- URL Operations --------------------

def generate_short_url(long_url):
    """Generate a short URL using MD5 hash."""
    hash_object = hashlib.md5(long_url.encode())
    return hash_object.hexdigest()[:6]

# -------------------- Route Handlers --------------------

@app.route('/')
def dashboard():
    return render_template('index.html')

@app.route('/shorten', methods=['POST'])
def shorten_url():
    """Handle URL shortening requests."""
    original_url = request.form.get('url')
    expiry_hours = int(request.form.get('expiry_hours', 24))
    password = request.form.get('password')
    name = request.form.get('name')
    
    if not original_url:
        return jsonify({'error': 'URL is required'}), 400
    
    expires_at = datetime.now() + timedelta(hours=expiry_hours)
    short_url = generate_short_url(original_url)

    try:
        add_url_to_db(original_url, short_url, expires_at, password, name)
    except sqlite3.IntegrityError:
        pass  # URL already exists

    return render_template('index.html', short_url=BASE_URL + short_url)

@app.route('/<short_url>', methods=['GET'])
def redirect_url(short_url):
    """Handle URL redirection."""
    url_data = get_url_from_db(short_url)
    if not url_data:
        abort(404, description="URL not found")

    original_url, expires_at, password = url_data
    if datetime.now() > datetime.fromisoformat(expires_at):
        abort(410, description="URL has expired")

    if password:
        return redirect(f"/check_password/{short_url}")

    log_analytics(short_url, request.remote_addr)
    return redirect(original_url)

# -------------------- Password Protection Routes --------------------

@app.route('/check_password/<short_url>', methods=['GET'])
def check_password(short_url):
    """Show password prompt for protected URLs."""
    url_data = get_url_from_db(short_url)
    if not url_data:
        abort(404, description="URL not found")

    original_url, expires_at, password = url_data
    if datetime.now() > datetime.fromisoformat(expires_at):
        abort(410, description="URL has expired")

    if not password:
        return redirect(original_url)

    return render_template('password_prompt.html', short_url=short_url)

@app.route('/validate_password/<short_url>', methods=['POST'])
def validate_password(short_url):
    """Validate password for protected URLs."""
    url_data = get_url_from_db(short_url)
    if not url_data:
        abort(404, description="URL not found")

    original_url, expires_at, stored_password = url_data
    if datetime.now() > datetime.fromisoformat(expires_at):
        abort(410, description="URL has expired")

    user_password = request.json.get('password')
    if stored_password and stored_password != user_password:
        return jsonify({"success": False, "message": "Invalid password"}), 403

    return jsonify({"success": True, "redirect_url": original_url})

# -------------------- Analytics Routes --------------------

@app.route('/url_analytics')
def url_analytics():
    """Display analytics dashboard."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('''SELECT short_url, original_url, name FROM urls WHERE password IS NOT NULL''')
        private_urls = cursor.fetchall()

        cursor.execute('''SELECT short_url, original_url, name FROM urls WHERE password IS NULL''')
        non_protected_urls = cursor.fetchall()

    return render_template('url_analytics.html', 
                         private_urls=private_urls, 
                         non_protected_urls=non_protected_urls)

@app.route('/analytics/<short_url>')
def analytics(short_url):
    """Display analytics for a specific URL."""
    analytics_data = get_analytics_from_db(short_url)
    if not analytics_data:
        return render_template('analytics.html', error="No analytics data found for this URL")
    return render_template('analytics.html', short_url=short_url, analytics_data=analytics_data)

# -------------------- URL Listing Routes --------------------

@app.route('/private_urls', methods=['GET'])
def private_urls():
    """Display list of password-protected URLs."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('''SELECT short_url, original_url, name FROM urls 
                         WHERE password IS NOT NULL AND password != ""''')
        private_urls = cursor.fetchall()
    return render_template('private_urls.html', private_urls=private_urls, BASE_URL=BASE_URL)

@app.route('/non_protected_urls', methods=['GET'])
def non_protected_urls():
    """Display list of non-protected URLs."""
    with sqlite3.connect(DB_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute('''SELECT short_url, original_url, name FROM urls 
                         WHERE password IS NULL OR password = ""''')
        non_protected_urls = cursor.fetchall()
    return render_template('non_protected_urls.html', 
                         non_protected_urls=non_protected_urls, 
                         BASE_URL=BASE_URL)

# -------------------- Application Entry Point --------------------

if __name__ == '__main__':
    if not os.path.exists(DB_FILE):
        init_db()
    app.run(debug=True)