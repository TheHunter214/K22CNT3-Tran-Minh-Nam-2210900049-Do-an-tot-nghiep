
CREATE DATABASE IF NOT EXISTS cinema_booking 
DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE cinema_booking;
-- Người dùng
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;
-- Phim
CREATE TABLE IF NOT EXISTS movies (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    director VARCHAR(255),
    cast TEXT,
    genre VARCHAR(100),
    release_date DATE,
    duration INT,
    language VARCHAR(100),
    age_rating VARCHAR(10),
    rating DECIMAL(3,1),
    price INT,
    description TEXT,
    poster_image VARCHAR(255)
) ENGINE=InnoDB;
-- Rạp chiếu
CREATE TABLE IF NOT EXISTS cinemas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    address VARCHAR(255)
) ENGINE=InnoDB;

-- Phòng chiếu
CREATE TABLE IF NOT EXISTS screens (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cinema_id INT NOT NULL,
    name VARCHAR(100),
    capacity INT,
    FOREIGN KEY (cinema_id) REFERENCES cinemas(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Ghế vật lý trong phòng
CREATE TABLE IF NOT EXISTS seats (
    id INT AUTO_INCREMENT PRIMARY KEY,
    screen_id INT NOT NULL,
    seat_row VARCHAR(5),
    seat_col INT,
    label VARCHAR(10),
    FOREIGN KEY (screen_id) REFERENCES screens(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Suất chiếu
CREATE TABLE IF NOT EXISTS showtimes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    movie_id INT NOT NULL,
    screen_id INT NOT NULL,
    start_time DATETIME NOT NULL,
    price INT,
    seats_available INT,
    FOREIGN KEY (movie_id) REFERENCES movies(id) ON DELETE CASCADE,
    FOREIGN KEY (screen_id) REFERENCES screens(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Đồ ăn/Combo
CREATE TABLE IF NOT EXISTS combos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price INT NOT NULL
) ENGINE=InnoDB;

-- Đơn đặt vé (Hóa đơn)
CREATE TABLE IF NOT EXISTS bookings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    showtime_id INT NOT NULL,
    booking_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    total_price INT,
    status VARCHAR(20) DEFAULT 'pending',
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (showtime_id) REFERENCES showtimes(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Chi tiết ghế đã đặt
CREATE TABLE IF NOT EXISTS booking_seats (
    booking_id INT NOT NULL,
    seat_id INT NOT NULL,
    PRIMARY KEY (booking_id, seat_id),
    FOREIGN KEY (booking_id) REFERENCES bookings(id) ON DELETE CASCADE,
    FOREIGN KEY (seat_id) REFERENCES seats(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Chi tiết đồ ăn đã đặt
CREATE TABLE IF NOT EXISTS booking_combos (
    booking_id INT NOT NULL,
    combo_id INT NOT NULL,
    quantity INT DEFAULT 1,
    PRIMARY KEY (booking_id, combo_id),
    FOREIGN KEY (booking_id) REFERENCES bookings(id) ON DELETE CASCADE,
    FOREIGN KEY (combo_id) REFERENCES combos(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Thanh toán
CREATE TABLE IF NOT EXISTS payments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    booking_id INT NOT NULL,
    amount INT NOT NULL,
    method VARCHAR(50),
    status VARCHAR(50),
    paid_at DATETIME,
    FOREIGN KEY (booking_id) REFERENCES bookings(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- ==========================================================
-- 3. NHẬP DỮ LIỆU MẪU (DỮ LIỆU TĨNH)
-- ==========================================================

-- Nhập 8 bộ phim của bạn
INSERT INTO movies (id, title, director, cast, genre, release_date, duration, language, age_rating, rating, price, description, poster_image) VALUES
(1, 'Zootopia 2', 'Jared Bush', 'Jason Bateman', 'Gia đình', '2025-11-28', 120, 'Tiếng Anh', '13+', 8.5, 80000, 'Tiếp nối những cuộc phiêu lưu của Cáo và Thỏ', 'movie1.jpg'),
(2, 'Jujutsu Kaisen: Shibuya', 'Park Sunghoo', 'Yuuichi Nakamura', 'Anime', '2024-12-24', 144, 'Tiếng Nhật', '16+', 9.0, 100000, 'Biến cố Shibuya', 'movie2.jpg'),
(3, 'Chainsaw Man Movie', 'Motonobu Hori', 'Kikunosuke Toya', 'Anime', '2025-02-15', 109, 'Tiếng Nhật', '18+', 8.8, 110000, 'Chương Reze', 'movie3.jpg'),
(4, 'Demon Slayer: Infinity Castle', 'Haruo Sotozaki', 'Natsuki Hanae', 'Anime', '2024-12-31', 110, 'Tiếng Nhật', '18+', 9.8, 125000, 'Trận chiến vô hạn', 'movie4.jpg'),
(5, 'Five Nights at Freddy’s 2', 'Emma Tammi', 'Josh Hutcherson', 'Kinh dị', '2024-12-14', 115, 'Tiếng Anh', '18+', 8.5, 95000, 'Chuỗi sự kiện rùng rợn', 'movie5.jpg'),
(6, 'Avatar: Fire and Ash', 'James Cameron', 'Sam Worthington, Zoe Saldana', 'Khoa học viễn tưởng', '2024-12-20', 110, 'Tiếng Anh', '18+', 9.5, 150000, 'Hành trình sử thi', 'movie6.jpg'),
(7, '5 CENTIMET TRÊN GIÂY', 'Makoto Shinkai', 'Yoshito Isomaki, Mika Shinoda', 'Hoạt Hình, Tình cảm', '2024-11-28', 115, 'Tiếng Nhật', '13+', 8.7, 100000, 'Câu chuyện nhẹ nhàng, cảm xúc về những khoảnh khắc nhỏ bé.', 'movie7.jpg'),
(8, 'Conan : Dư Ảnh Của Độc Nhãn', 'Yuzuru Tachikawa', 'Minami Takayama, Wakana Yamazaki', 'Hành Động, Hoạt Hình', '2024-10-27', 115, 'Tiếng Nhật', '13+', 9.0, 95000, 'Hành động giải đố cùng các pha rượt đuổi kịch tính.', 'movie8.jpg');

-- Nhập Rạp và Phòng
INSERT INTO cinemas (id, name, address) VALUES 
(1, 'KUNCINEMA Thủ Đức', 'Võ Văn Ngân, Thủ Đức, TP.HCM'),
(2, 'KUNCINEMA Quận 1', 'Lê Thánh Tôn, Quận 1, TP.HCM');

INSERT INTO screens (id, cinema_id, name, capacity) VALUES 
(1, 1, 'Phòng 01', 60),
(2, 1, 'Phòng 02', 60);

-- Nhập mẫu một số Ghế (Hàng A phòng 1)
INSERT INTO seats (screen_id, seat_row, seat_col, label) VALUES 
(1, 'A', 1, 'A1'), (1, 'A', 2, 'A2'), (1, 'A', 3, 'A3'), (1, 'A', 4, 'A4'), (1, 'A', 5, 'A5'),
(1, 'A', 6, 'A6'), (1, 'A', 7, 'A7'), (1, 'A', 8, 'A8'), (1, 'A', 9, 'A9'), (1, 'A', 10, 'A10');

-- Nhập Suất chiếu mẫu
INSERT INTO showtimes (id, movie_id, screen_id, start_time, price, seats_available) VALUES 
(1, 1, 1, '2025-12-30 14:30:00', 80000, 60),
(2, 2, 1, '2025-12-30 19:00:00', 100000, 60);

-- Nhập Combo mẫu
INSERT INTO combos (id, name, description, price) VALUES 
(1, 'Combo Vàng', '1 Bắp L + 1 Nước L', 85000),
(2, 'Combo Đôi', '1 Bắp L + 2 Nước L', 110000);