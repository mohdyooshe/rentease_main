import os
import functools
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config
from models.db import get_db_connection
from decimal import Decimal

app = Flask(__name__)
app.config.from_object(Config)

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Custom Login Required Decorator
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if session.get('user_id') is None:
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('login'))
        return view(**kwargs)
    return wrapped_view

@app.context_processor
def inject_pending_requests():
    pending_count = 0
    if session.get('user_id') and session.get('user_type') == 'owner':
        try:
            conn = get_db_connection()
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT COUNT(*) as count FROM rental_requests rr JOIN items i ON rr.item_id = i.id WHERE i.owner_id = %s AND rr.status = 'pending'", 
                    (session['user_id'],)
                )
                res = cursor.fetchone()
                if res:
                    pending_count = res['count']
            conn.close()
        except:
            pass
    return dict(pending_requests_count=pending_count)

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if session.get('user_id'):
        return redirect(url_for('index'))
        
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        user_type = request.form.get('user_type')
        
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return redirect(url_for('signup'))
            
        if not user_type in ['owner', 'renter']:
            flash('Invalid role selected.', 'error')
            return redirect(url_for('signup'))
            
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
                if cursor.fetchone():
                    flash('Email address already exists.', 'error')
                    return redirect(url_for('signup'))
                
                hashed_pw = generate_password_hash(password)
                cursor.execute(
                    "INSERT INTO users (full_name, email, password_hash, user_type) VALUES (%s, %s, %s, %s)",
                    (full_name, email, hashed_pw, user_type)
                )
            connection.commit()
            flash('Account created successfully! You can now log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            flash(f'An error occurred: {str(e)}', 'error')
        finally:
            connection.close()
            
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('user_id'):
        user_type = session.get('user_type')
        if user_type == 'owner':
            return redirect(url_for('owner_dashboard'))
        else:
            return redirect(url_for('renter_dashboard'))
            
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        connection = get_db_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT id, full_name, password_hash, user_type FROM users WHERE email = %s", (email,))
                user = cursor.fetchone()
                
                if user and check_password_hash(user['password_hash'], password):
                    session.clear()
                    session['user_id'] = user['id']
                    session['username'] = user['full_name']
                    session['user_type'] = user['user_type']
                    
                    if user['user_type'] == 'owner':
                        return redirect(url_for('owner_dashboard'))
                    else:
                        return redirect(url_for('renter_dashboard'))
                else:
                    flash('Login unsuccessful. Please check email and password.', 'error')
        except Exception as e:
             flash(f'An error occurred: {str(e)}', 'error')
        finally:
            connection.close()
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))

# --- OWNER ROUTES ---
@app.route('/owner/dashboard')
@login_required
def owner_dashboard():
    if session.get('user_type') != 'owner':
        return redirect(url_for('renter_dashboard'))
    
    owner_id = session['user_id']
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM items WHERE owner_id = %s ORDER BY created_at DESC", (owner_id,))
            items = cursor.fetchall()
            
            total_items = len(items)
            
            cursor.execute("SELECT COUNT(*) as count FROM rental_requests rr JOIN items i ON rr.item_id = i.id WHERE i.owner_id = %s AND rr.status = 'accepted'", (owner_id,))
            active_rentals = cursor.fetchone()['count']
            
            cursor.execute("SELECT COUNT(*) as count FROM rental_requests rr JOIN items i ON rr.item_id = i.id WHERE i.owner_id = %s AND rr.status = 'pending'", (owner_id,))
            pending_requests = cursor.fetchone()['count']
            
            cursor.execute("SELECT SUM(total_amount) as total FROM rental_requests rr JOIN items i ON rr.item_id = i.id WHERE i.owner_id = %s AND rr.status = 'accepted'", (owner_id,))
            earnings_row = cursor.fetchone()
            total_earnings = earnings_row['total'] if earnings_row['total'] else 0
            
    finally:
        conn.close()
        
    return render_template('owner/dashboard.html', items=items, stats={
        'total_items': total_items,
        'active_rentals': active_rentals,
        'pending_requests': pending_requests,
        'total_earnings': total_earnings
    })

@app.route('/owner/add_item', methods=['GET', 'POST'])
@login_required
def add_item():
    if session.get('user_type') != 'owner':
        return redirect(url_for('renter_dashboard'))
        
    if request.method == 'POST':
        title = request.form.get('title')
        category = request.form.get('category')
        description = request.form.get('description')
        price_per_day = request.form.get('price_per_day')
        product_price = request.form.get('product_price', 0)
        
        image = request.files.get('image')
        image_url = ''
        if image and image.filename:
            filename = secure_filename(image.filename)
            filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            image_url = filename
            
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO items (owner_id, title, description, category, price_per_day, product_price, image_url) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                    (session['user_id'], title, description, category, price_per_day, product_price, image_url)
                )
            conn.commit()
            flash('Item listed successfully!', 'success')
            return redirect(url_for('owner_dashboard'))
        finally:
            conn.close()
            
    return render_template('owner/list_item.html')

@app.route('/owner/requests')
@login_required
def owner_requests():
    if session.get('user_type') != 'owner':
        return redirect(url_for('index'))
        
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            query = """
                SELECT rr.*, i.title as item_title, u.full_name as renter_name 
                FROM rental_requests rr 
                JOIN items i ON rr.item_id = i.id 
                JOIN users u ON rr.renter_id = u.id 
                WHERE i.owner_id = %s AND rr.status = 'pending'
                ORDER BY rr.created_at DESC
            """
            cursor.execute(query, (session['user_id'],))
            requests_list = cursor.fetchall()
    finally:
        conn.close()
        
    return render_template('owner/requests.html', requests=requests_list)

@app.route('/owner/request/<int:request_id>/<action>', methods=['POST'])
@login_required
def handle_request(request_id, action):
    if session.get('user_type') != 'owner':
        return redirect(url_for('index'))
        
    if action not in ['accept', 'reject']:
        return redirect(url_for('owner_requests'))
        
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT i.owner_id, rr.item_id FROM rental_requests rr JOIN items i ON rr.item_id = i.id WHERE rr.id = %s", (request_id,))
            req = cursor.fetchone()
            if not req or req['owner_id'] != session['user_id']:
                flash('Invalid request.', 'error')
                return redirect(url_for('owner_requests'))
                
            new_status = 'accepted' if action == 'accept' else 'rejected'
            cursor.execute("UPDATE rental_requests SET status = %s WHERE id = %s", (new_status, request_id))
            
            if action == 'accept':
                cursor.execute("UPDATE items SET is_available = FALSE WHERE id = %s", (req['item_id'],))
                
        conn.commit()
        flash(f'Request {new_status}!', 'success')
    finally:
        conn.close()
        
    return redirect(url_for('owner_requests'))

# --- RENTER ROUTES ---
@app.route('/renter/dashboard')
@login_required
def renter_dashboard():
    if session.get('user_type') != 'renter':
        return redirect(url_for('owner_dashboard'))
        
    renter_id = session['user_id']
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) as count FROM rental_requests WHERE renter_id = %s AND status = 'accepted'", (renter_id,))
            active_rentals = cursor.fetchone()['count']
            
            cursor.execute("SELECT COUNT(*) as count FROM rental_requests WHERE renter_id = %s AND status = 'pending'", (renter_id,))
            pending_requests = cursor.fetchone()['count']
            
            cursor.execute("SELECT SUM(total_amount) as total FROM rental_requests WHERE renter_id = %s AND status = 'accepted'", (renter_id,))
            spent_row = cursor.fetchone()
            total_spent = spent_row['total'] if spent_row['total'] else 0
            
    finally:
        conn.close()
        
    return render_template('renter/dashboard.html', stats={
        'active_rentals': active_rentals,
        'pending_requests': pending_requests,
        'total_spent': total_spent
    })

@app.route('/browse')
def browse():
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT i.*, u.full_name as owner_name FROM items i JOIN users u ON i.owner_id = u.id WHERE i.is_available = TRUE")
            items = cursor.fetchall()
    finally:
        conn.close()
    return render_template('renter/browse.html', items=items)

@app.route('/rent/<int:item_id>', methods=['POST'])
@login_required
def rent_item(item_id):
    if session.get('user_type') != 'renter':
        flash('Only renters can request items.', 'error')
        return redirect(url_for('browse'))
        
    start_date_str = request.form.get('start_date')
    end_date_str = request.form.get('end_date')
    
    if not start_date_str or not end_date_str:
        flash('Start and end dates are required.', 'error')
        return redirect(url_for('browse'))
        
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
    end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
    
    if start_date > end_date:
        flash('End date must be after start date.', 'error')
        return redirect(url_for('browse'))
        
    total_days = (end_date - start_date).days + 1
    if total_days <= 0:
        total_days = 1
        
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT price_per_day, product_price, is_available FROM items WHERE id = %s", (item_id,))
            item = cursor.fetchone()
            
            if not item or not item['is_available']:
                flash('Item is not available.', 'error')
                return redirect(url_for('browse'))
                
            rent_amount = item['price_per_day'] * total_days
            security_deposit = item['product_price'] * Decimal('0.30')
            grand_total = rent_amount + security_deposit
            
            cursor.execute(
                """INSERT INTO rental_requests 
                (item_id, renter_id, start_date, end_date, total_days, total_amount, rent_amount, security_deposit, grand_total, status) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'pending')""",
                (item_id, session['user_id'], start_date, end_date, total_days, grand_total, rent_amount, security_deposit, grand_total)
            )
            conn.commit()
        flash('Request sent! Waiting for owner approval.', 'success')
    finally:
        conn.close()
        
    return redirect(url_for('renter_orders'))

@app.route('/renter/orders')
@login_required
def renter_orders():
    if session.get('user_type') != 'renter':
        return redirect(url_for('index'))
        
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            query = """
                SELECT rr.*, i.title, i.image_url 
                FROM rental_requests rr 
                JOIN items i ON rr.item_id = i.id 
                WHERE rr.renter_id = %s 
                ORDER BY rr.created_at DESC
            """
            cursor.execute(query, (session['user_id'],))
            orders = cursor.fetchall()
    finally:
        conn.close()
        
    return render_template('renter/orders.html', orders=orders)



if __name__ == '__main__':
    app.run(debug=True)
