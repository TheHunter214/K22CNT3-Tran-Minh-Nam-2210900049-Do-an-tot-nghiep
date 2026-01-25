from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, abort
import mysql.connector
from config import Config
import sys
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date, datetime
from functools import wraps

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
# LỊCH SỬ ĐẶT VÉ 
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

        # Kiểm tra user có tồn tại trước khi check password
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role'] # Gán role vào session sau khi login đúng
            flash('Đăng nhập thành công!', 'success')
            
            # Nếu là admin thì dẫn thẳng vào trang quản trị
            if user['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
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

# =========================
# CHECK ADMIN ROLE
# =========================
def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        # Kiểm tra session thay vì current_user
        if 'user_id' not in session:
            flash("Vui lòng đăng nhập!", "warning")
            return redirect(url_for("login"))
        if session.get('role') != 'admin':
            flash("Bạn không có quyền admin!", "danger")
            return redirect(url_for("home"))
        return f(*args, **kwargs)
    return wrapper


# =========================
# ADMIN DASHBOARD
# =========================
@app.route("/admin")
@admin_required # Bỏ @login_required vì decorator admin_required đã bao gồm kiểm tra login
def admin_dashboard():
    conn = get_db()
    cur = conn.cursor(dictionary=True)

    cur.execute("SELECT COUNT(*) total FROM movies")
    total_movies = cur.fetchone()["total"]

    cur.execute("SELECT COUNT(*) total FROM users")
    total_users = cur.fetchone()["total"]

    cur.execute("SELECT COUNT(*) total FROM bookings")
    total_bookings = cur.fetchone()["total"]

    cur.execute("SELECT SUM(total_price) revenue FROM bookings WHERE status IN ('paid','confirmed','Success')")
    res_revenue = cur.fetchone()
    revenue = res_revenue["revenue"] if res_revenue["revenue"] else 0

    cur.close()
    conn.close()

    return render_template(
        "admin/dashboard.html",
        total_movies=total_movies,
        total_users=total_users,
        total_bookings=total_bookings,
        revenue=revenue
    )


# =========================
# ADMIN MOVIES MODULE
# =========================
# =========================
# ADMIN MOVIES MODULE (Phim)
# =========================
@app.route("/admin/movies")
@admin_required
def admin_movies():
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM movies ORDER BY id DESC")
    movies = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("admin/movies.html", movies=movies)

@app.route("/admin/movies/add", methods=['POST'])
@admin_required
def admin_add_movie():
    if request.method == 'POST':
        title = request.form.get('title')
        duration = request.form.get('duration')
        director = request.form.get('director')
        release_date = request.form.get('release_date')
        poster_image = request.form.get('poster_image')
        description = request.form.get('description')

        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO movies (title, duration, director, release_date, poster_image, description)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (title, duration, director, release_date, poster_image, description))
        conn.commit()
        cur.close()
        conn.close()
        flash("Thêm phim mới thành công!", "success")
    return redirect(url_for("admin_movies"))

@app.route("/admin/movies/edit/<int:id>", methods=['GET', 'POST'])
@admin_required
def admin_edit_movie(id):
    conn = get_db()
    if request.method == 'POST':
        title = request.form.get('title')
        duration = request.form.get('duration')
        director = request.form.get('director')
        release_date = request.form.get('release_date')
        poster_image = request.form.get('poster_image')
        description = request.form.get('description')

        cur = conn.cursor()
        cur.execute("""
            UPDATE movies SET title=%s, duration=%s, director=%s, release_date=%s, poster_image=%s, description=%s
            WHERE id=%s
        """, (title, duration, director, release_date, poster_image, description, id))
        conn.commit()
        cur.close()
        conn.close()
        flash("Cập nhật thông tin phim thành công!", "success")
        return redirect(url_for("admin_movies"))

    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM movies WHERE id=%s", (id,))
    movie = cur.fetchone()
    cur.close()
    conn.close()
    return render_template("admin/movie_edit.html", movie=movie)

@app.route("/admin/movies/delete/<int:id>")
@admin_required
def admin_delete_movie(id):
    conn = get_db()
    cur = conn.cursor()
    try:
        # Lưu ý: Nếu có khóa ngoại ở showtimes, cần xử lý delete cascade trong DB hoặc xóa thủ công ở đây
        cur.execute("DELETE FROM movies WHERE id=%s", (id,))
        conn.commit()
        flash("Đã xóa phim!", "success")
    except Exception as e:
        flash("Lỗi: Không thể xóa phim (có thể đang có suất chiếu liên quan)!", "danger")
    finally:
        cur.close()
        conn.close()
    return redirect(url_for("admin_movies"))

# =========================
# ADMIN SHOWTIMES MODULE (Suất chiếu)
# =========================
@app.route("/admin/showtimes")
@admin_required
def admin_showtimes():
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    # Lấy danh sách suất chiếu kèm tên phim và tên phòng
    cur.execute("""
        SELECT s.*, m.title AS movie_title, sc.name AS screen_name
        FROM showtimes s
        JOIN movies m ON s.movie_id = m.id
        JOIN screens sc ON s.screen_id = sc.id
        ORDER BY s.start_time DESC
    """)
    showtimes = cur.fetchall()

    cur.execute("SELECT id, title FROM movies")
    movies = cur.fetchall()

    cur.execute("SELECT id, name FROM screens")
    screens = cur.fetchall()

    cur.close()
    conn.close()
    return render_template("admin/showtimes.html", showtimes=showtimes, movies=movies, screens=screens)

@app.route("/admin/showtimes/add", methods=['POST'])
@admin_required
def admin_add_showtime():
    movie_id = request.form.get('movie_id')
    screen_id = request.form.get('screen_id')
    start_time = request.form.get('start_time')
    price = request.form.get('price')

    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO showtimes (movie_id, screen_id, start_time, price)
        VALUES (%s, %s, %s, %s)
    """, (movie_id, screen_id, start_time, price))
    conn.commit()
    cur.close()
    conn.close()
    flash("Đã thêm suất chiếu mới!", "success")
    return redirect(url_for("admin_showtimes"))

@app.route("/admin/showtimes/delete/<int:id>")
@admin_required
def admin_delete_showtime(id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM showtimes WHERE id=%s", (id,))
    conn.commit()
    cur.close()
    conn.close()
    flash("Đã xóa suất chiếu!", "warning")
    return redirect(url_for("admin_showtimes"))


# =========================
# ADMIN BOOKINGS MODULE
# =========================
@app.route("/admin/bookings")
@admin_required
def admin_bookings():
    conn = get_db()
    cur = conn.cursor(dictionary=True)

    cur.execute("""
        SELECT b.id, u.username, b.total_price, b.status, b.booking_time
        FROM bookings b
        JOIN users u ON b.user_id = u.id
        ORDER BY b.booking_time DESC
    """)
    bookings = cur.fetchall()

    cur.close()
    conn.close()

    return render_template("admin/bookings.html", bookings=bookings)


@app.route("/admin/bookings/delete/<int:id>")
@admin_required
def admin_delete_booking(id):
    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM booking_seats WHERE booking_id=%s", (id,))
        cur.execute("DELETE FROM booking_combos WHERE booking_id=%s", (id,))
        cur.execute("DELETE FROM bookings WHERE id=%s", (id,))
        conn.commit()
        flash("Đã xóa đơn vé!", "success")
    except Exception as e:
        flash("Lỗi khi xóa đơn!", "danger")
    finally:
        cur.close()
        conn.close()

    return redirect(url_for("admin_bookings"))


# =========================
# ADMIN USERS MODULE (Người dùng)
# =========================
@app.route("/admin/users")
@admin_required
def admin_users():
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT id, username, email, role FROM users")
    users = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("admin/users.html", users=users)

@app.route("/admin/users/delete/<int:id>")
@admin_required
def admin_delete_user(id):
    conn = get_db()
    cur = conn.cursor()
    # Không cho phép admin tự xóa chính mình (nếu cần)
    cur.execute("DELETE FROM users WHERE id=%s", (id,))
    conn.commit()
    cur.close()
    conn.close()
    flash("Đã xóa tài khoản người dùng!", "success")
    return redirect(url_for("admin_users"))


# =========================
# ADMIN COMBOS MODULE (Bắp nước)
# =========================
@app.route("/admin/combos")
@admin_required
def admin_combos():
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM combos")
    combos = cur.fetchall()
    cur.close()
    conn.close()
    return render_template("admin/combos.html", combos=combos)

@app.route("/admin/combos/add", methods=['POST'])
@admin_required
def admin_add_combo():
    name = request.form.get('name')
    price = request.form.get('price')
    description = request.form.get('description')

    conn = get_db()
    cur = conn.cursor()
    cur.execute("INSERT INTO combos (name, price, description) VALUES (%s, %s, %s)", 
                (name, price, description))
    conn.commit()
    cur.close()
    conn.close()
    flash("Đã thêm combo bắp nước mới!", "success")
    return redirect(url_for("admin_combos"))

@app.route("/admin/combos/delete/<int:id>")
@admin_required
def admin_delete_combo(id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM combos WHERE id=%s", (id,))
    conn.commit()
    cur.close()
    conn.close()
    flash("Đã xóa combo!", "info")
    return redirect(url_for("admin_combos"))


if __name__ == "__main__":
    app.run(debug=True)