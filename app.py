from os import abort
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import mysql.connector
from config import Config
import sys
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date, datetime
import mysql.connector
def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",          # XAMPP mặc định là rỗng
        database="cinema_booking"
    )
app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = app.config.get('SECRET_KEY')
# ======================
# KẾT NỐI MYSQL
# ======================
def get_db():
    return mysql.connector.connect(
        host=app.config['DB_HOST'],
        port=app.config['DB_PORT'],
        user=app.config['DB_USER'],
        password=app.config['DB_PASSWORD'],
        database=app.config['DB_NAME']
    )
try:
    db_test = get_db()
    db_test.close()
    print("KẾT NỐI DATABASE THÀNH CÔNG!")
except Exception as e:
    print('ERROR: Không thể kết nối tới MySQL:', e, file=sys.stderr)

# ======================
# TRANG CHỦ – DANH SÁCH PHIM
# ======================
@app.route("/")
def home():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)

    # CHỈ PHIM ĐANG CHIẾU
    cursor.execute("""
        SELECT * FROM movies
        WHERE release_date <= CURDATE()
        ORDER BY release_date DESC
    """)
    movies = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("index.html", movies=movies)
# ======================
# CHI TIẾT PHIM
# ======================
@app.route('/movie/<int:movie_id>')
def movie_detail(movie_id):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    # Lấy toàn bộ thông tin phim dựa trên ID
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
        # Sử dụng dấu %s cho MySQL hoặc ? cho SQLite tùy DB của bạn
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()

        # LOG ĐỂ KIỂM TRA (Xóa sau khi xong)
        print(f"User tim thay: {user}") 

        if user:
            # Lưu ý: Thay 'password_hash' bằng đúng tên cột trong SQL của bạn
            if check_password_hash(user['password_hash'], password):
                session['user_id'] = user['id']
                session['username'] = user['username']
                flash('Đăng nhập thành công!', 'success')
                return redirect(url_for('home'))
            else:
                flash('Mật khẩu không chính xác!', 'danger')
        else:
            flash('Tên đăng nhập không tồn tại!', 'danger')
            
        # QUAN TRỌNG: Phải có dòng return này nếu đăng nhập thất bại
        return redirect(url_for('login'))

    return render_template('login.html')

# --- SỬA HÀM ĐĂNG KÝ ---
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # .strip() để loại bỏ khoảng trắng thừa như trong log Terminal của bạn
        username = request.form.get('username').strip()
        email = request.form.get('email').strip()
        password = request.form.get('password')
        phone = request.form.get('phone')

        conn = get_db()
        cursor = conn.cursor()
        
        # Kiểm tra trùng lặp
        cursor.execute('SELECT id FROM users WHERE username = %s OR email = %s', (username, email))
        if cursor.fetchone():
            flash('Username hoặc email đã tồn tại', 'danger')
            return redirect(url_for('register'))

        # QUAN TRỌNG: Phải mã hóa mật khẩu ở đây
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

# ======================
# ĐẶT VÉ (LOGIC MỚI)
# ======================
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

    # Chặn phim chưa chiếu
    if movie['release_date'] and movie['release_date'] > date.today():
        flash('Phim chưa mở đặt vé')
        return redirect(url_for('home'))

    cur.execute("""
        SELECT s.id, s.start_time, s.price,
               sc.name AS screen_name,
               c.name AS cinema_name
        FROM showtimes s
        JOIN screens sc ON s.screen_id = sc.id
        JOIN cinemas c ON sc.cinema_id = c.id
        WHERE s.movie_id = %s
        ORDER BY s.start_time
    """, (movie_id,))
    showtimes = cur.fetchall()

    cur.close()
    conn.close()

    return render_template(
        'booking.html',
        movie=movie,
        showtimes=showtimes
    )
@app.route('/api/get_seats/<int:showtime_id>')
def api_get_seats(showtime_id):
    conn = get_db()
    cur = conn.cursor(dictionary=True)

    # Lấy screen_id
    cur.execute("SELECT screen_id FROM showtimes WHERE id=%s", (showtime_id,))
    showtime = cur.fetchone()

    if not showtime:
        return jsonify({"error": "Showtime not found"}), 404

    screen_id = showtime['screen_id']

    # Tất cả ghế
    cur.execute("SELECT id, label FROM seats WHERE screen_id=%s", (screen_id,))
    all_seats = cur.fetchall()

    # Ghế đã đặt
    cur.execute("""
        SELECT seat_id FROM booking_seats bs
        JOIN bookings b ON bs.booking_id = b.id
        WHERE b.showtime_id=%s
    """, (showtime_id,))
    occupied = [row['seat_id'] for row in cur.fetchall()]

    cur.close()
    conn.close()

    return jsonify({
        "all_seats": all_seats,
        "occupied_seats": occupied
    })

@app.route('/api/create_booking', methods=['POST'])
def api_create_booking():
    if 'user_id' not in session:
        return jsonify({"success": False, "error": "Vui lòng đăng nhập"})
    
    data = request.json
    showtime_id = data.get('showtime_id')
    seats = data.get('seats', [])
    combos = data.get('combos', {}) # Nhận dictionary {id: qty}

    conn = get_db()
    cur = conn.cursor(dictionary=True) # Dùng dictionary để dễ lấy price

    # Tính toán tổng tiền
    cur.execute("SELECT price FROM showtimes WHERE id=%s", (showtime_id,))
    ticket_price = cur.fetchone()['price']
    total = ticket_price * len(seats)


    for combo_id, qty in combos.items():
        if int(qty) > 0:
            cur.execute("SELECT price FROM combos WHERE id=%s", (combo_id,))
            c_price = cur.fetchone()['price']
            total += c_price * int(qty)

    # Lưu Booking
    cur.execute("INSERT INTO bookings (user_id, showtime_id, total_price, status) VALUES (%s, %s, %s, 'paid')",
                (session['user_id'], showtime_id, total))
    booking_id = cur.lastrowid

    # Lưu ghế
    for s_id in seats:
        cur.execute("INSERT INTO booking_seats (booking_id, seat_id) VALUES (%s, %s)", (booking_id, s_id))

    # Lưu combo
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
        # Truy vấn đúng các cột: id, name, description, price, type
        cur.execute("SELECT id, name, description, price, type FROM combos")
        combos = cur.fetchall()
        cur.close()
        conn.close()
        return jsonify(combos)
    except Exception as e:
        print(f"Lỗi: {e}")
        return jsonify([])

# ======================
# PHIM SẮP CHIẾU (Thêm đoạn này vào để sửa lỗi)
# ======================
@app.route('/upcoming')
def upcoming():
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    # Lấy phim có ngày chiếu lớn hơn ngày hiện tại
    cursor.execute("SELECT * FROM movies WHERE release_date > CURDATE()")
    movies = cursor.fetchall()
    
    cursor.close()
    conn.close()
    return render_template("upcoming.html", movies=movies)

# ======================
# THANH TOÁN & LƯU DB
# ======================
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

    if not seat_ids:
        return jsonify({"status": "error", "message": "Chưa chọn ghế"}), 400

    conn = get_db()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO bookings (user_id, showtime_id, total_price, status)
            VALUES (%s, %s, %s, 'confirmed')
        """, (user_id, showtime_id, total_price))
        booking_id = cursor.lastrowid

        for s_id in seat_ids:
            cursor.execute("""
                INSERT INTO booking_seats (booking_id, seat_id)
                VALUES (%s, %s)
            """, (booking_id, s_id))

        for cb in combo_data:
            if cb['qty'] > 0:
                cursor.execute("""
                    INSERT INTO booking_combos (booking_id, combo_id, quantity)
                    VALUES (%s, %s, %s)
                """, (booking_id, cb['id'], cb['qty']))

        conn.commit()
        return jsonify({
            "status": "success",
            "booking_id": booking_id
        })
    except Exception as e:
        conn.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        cursor.close()
        conn.close()
if __name__ == "__main__":
    app.run(debug=True)