from os import abort
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import mysql.connector
from config import Config
import sys
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date, datetime

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = app.config.get('SECRET_KEY')

# ======================
# KẾT NỐI MYSQL (Dùng 1 hàm duy nhất)
# ======================
def get_db():
    return mysql.connector.connect(
        host=app.config.get('DB_HOST', 'localhost'),
        port=app.config.get('DB_PORT', 3306),
        user=app.config.get('DB_USER', 'root'),
        password=app.config.get('DB_PASSWORD', ''),
        database=app.config.get('DB_NAME', 'cinema_booking')
    )

# Test kết nối khi khởi động
try:
    db_test = get_db()
    db_test.close()
    print("✅ KẾT NỐI DATABASE THÀNH CÔNG!")
except Exception as e:
    print('❌ ERROR: Không thể kết nối tới MySQL:', e, file=sys.stderr)

# ======================
# LỊCH SỬ ĐẶT VÉ (FIX LỖI ATTRIBUTEERROR)
# ======================
@app.route('/history')
def history():
    if 'user_id' not in session:
        flash('Vui lòng đăng nhập để xem lịch sử', 'warning')
        return redirect(url_for('login'))
        
    user_id = session['user_id']
    conn = get_db()
    # Trong mysql.connector, dùng dictionary=True để trả về kết quả dạng dict
    cursor = conn.cursor(dictionary=True)

    # Truy vấn lấy thông tin từ Bookings, Movies, Showtimes và nối chuỗi Ghế/Combo
    query = """
        SELECT 
            b.id as booking_id,
            b.total_price as amount,
            b.status,
            b.booking_time as paid_at,
            m.title as movie_title,
            m.poster_image,
            s.start_time,
            (SELECT GROUP_CONCAT(st.label SEPARATOR ', ')
             FROM booking_seats bs
             JOIN seats st ON bs.seat_id = st.id
             WHERE bs.booking_id = b.id) as seat_list,
            (SELECT GROUP_CONCAT(CONCAT(c.name, ' (x', bc.quantity, ')') SEPARATOR ', ')
             FROM booking_combos bc
             JOIN combos c ON bc.combo_id = c.id
             WHERE bc.booking_id = b.id) as combo_list
        FROM bookings b
        JOIN showtimes s ON b.showtime_id = s.id
        JOIN movies m ON s.movie_id = m.id
        WHERE b.user_id = %s
        ORDER BY b.booking_time DESC
    """
    
    try:
        cursor.execute(query, (user_id,))
        history_data = cursor.fetchall()
    except Exception as e:
        print(f"Lỗi SQL: {e}")
        history_data = []
    finally:
        cursor.close()
        conn.close()

    return render_template('history.html', history=history_data)

# ======================
# CÁC ROUTE CŨ (GIỮ NGUYÊN VÀ TỐI ƯU)
# ======================

@app.route("/")
def home():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT * FROM movies
        WHERE release_date <= CURDATE()
        ORDER BY release_date DESC
    """)
    movies = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("index.html", movies=movies)

@app.route('/service/<type>')
def service_detail(type):
    return render_template(f'services/{type}.html')

@app.route('/movie/<int:movie_id>')
def movie_detail(movie_id):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM movies WHERE id = %s", (movie_id,))
    movie = cursor.fetchone()
    cursor.close()
    conn.close()
    if movie:
        return render_template('movie.html', movie=movie)
    return "Không tìm thấy phim", 404

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash('Đăng nhập thành công!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Tên đăng nhập hoặc mật khẩu không chính xác!', 'danger')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username').strip()
        email = request.form.get('email').strip()
        password = request.form.get('password')
        phone = request.form.get('phone')

        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM users WHERE username = %s OR email = %s', (username, email))
        if cursor.fetchone():
            flash('Username hoặc email đã tồn tại', 'danger')
            return redirect(url_for('register'))

        pw_hash = generate_password_hash(password)
        cursor.execute('INSERT INTO users (username, email, password_hash, phone) VALUES (%s, %s, %s, %s)',
                       (username, email, pw_hash, phone))
        conn.commit()
        cursor.close()
        conn.close()
        flash('Đăng ký thành công, mời đăng nhập', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/booking/<int:movie_id>')
def booking(movie_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM movies WHERE id = %s", (movie_id,))
    movie = cur.fetchone()
    if not movie:
        abort(404)
    cur.execute("""
        SELECT s.id, s.start_time, s.price, sc.name AS screen_name, c.name AS cinema_name
        FROM showtimes s
        JOIN screens sc ON s.screen_id = sc.id
        JOIN cinemas c ON sc.cinema_id = c.id
        WHERE s.movie_id = %s
        ORDER BY s.start_time
    """, (movie_id,))
    showtimes = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('booking.html', movie=movie, showtimes=showtimes)

@app.route('/api/get_seats/<int:showtime_id>')
def api_get_seats(showtime_id):
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT screen_id FROM showtimes WHERE id=%s", (showtime_id,))
    showtime = cur.fetchone()
    if not showtime:
        return jsonify({"error": "Showtime not found"}), 404
    screen_id = showtime['screen_id']
    cur.execute("SELECT id, label FROM seats WHERE screen_id=%s", (screen_id,))
    all_seats = cur.fetchall()
    cur.execute("""
        SELECT seat_id FROM booking_seats bs
        JOIN bookings b ON bs.booking_id = b.id
        WHERE b.showtime_id=%s
    """, (showtime_id,))
    occupied = [row['seat_id'] for row in cur.fetchall()]
    cur.close()
    conn.close()
    return jsonify({"all_seats": all_seats, "occupied_seats": occupied})

@app.route('/api/create_booking', methods=['POST'])
def api_create_booking():
    if 'user_id' not in session:
        return jsonify({"success": False, "error": "Vui lòng đăng nhập"})
    data = request.json
    showtime_id = data.get('showtime_id')
    seats = data.get('seats', [])
    combos = data.get('combos', {})
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT price FROM showtimes WHERE id=%s", (showtime_id,))
    ticket_price = cur.fetchone()['price']
    total = ticket_price * len(seats)
    for combo_id, qty in combos.items():
        if int(qty) > 0:
            cur.execute("SELECT price FROM combos WHERE id=%s", (combo_id,))
            total += cur.fetchone()['price'] * int(qty)
    cur.execute("INSERT INTO bookings (user_id, showtime_id, total_price, status) VALUES (%s, %s, %s, 'paid')",
                (session['user_id'], showtime_id, total))
    booking_id = cur.lastrowid
    for s_id in seats:
        cur.execute("INSERT INTO booking_seats (booking_id, seat_id) VALUES (%s, %s)", (booking_id, s_id))
    for c_id, qty in combos.items():
        if int(qty) > 0:
            cur.execute("INSERT INTO booking_combos (booking_id, combo_id, quantity) VALUES (%s, %s, %s)",
                        (booking_id, c_id, qty))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"success": True})

@app.route('/api/combos')
def api_get_combos():
    try:
        conn = get_db()
        cur = conn.cursor(dictionary=True)
        cur.execute("SELECT id, name, description, price, type FROM combos")
        combos = cur.fetchall()
        cur.close()
        conn.close()
        return jsonify(combos)
    except Exception as e:
        return jsonify([])

@app.route('/upcoming')
def upcoming():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM movies WHERE release_date > CURDATE()")
    movies = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("upcoming.html", movies=movies)

@app.route('/checkout', methods=['POST'])
def checkout():
    if 'user_id' not in session:
        return jsonify({"status": "error", "message": "Vui lòng đăng nhập"}), 401
    data = request.json
    user_id = session['user_id']
    showtime_id = data['showtime_id']
    seat_ids = data['seats']
    combo_data = data.get('combos', [])
    total_price = data['total_price']
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO bookings (user_id, showtime_id, total_price, status) VALUES (%s, %s, %s, 'confirmed')",
                       (user_id, showtime_id, total_price))
        booking_id = cursor.lastrowid
        for s_id in seat_ids:
            cursor.execute("INSERT INTO booking_seats (booking_id, seat_id) VALUES (%s, %s)", (booking_id, s_id))
        for cb in combo_data:
            if cb['qty'] > 0:
                cursor.execute("INSERT INTO booking_combos (booking_id, combo_id, quantity) VALUES (%s, %s, %s)",
                               (booking_id, cb['id'], cb['qty']))
        conn.commit()
        return jsonify({"status": "success", "booking_id": booking_id})
    except Exception as e:
        conn.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    app.run(debug=True)