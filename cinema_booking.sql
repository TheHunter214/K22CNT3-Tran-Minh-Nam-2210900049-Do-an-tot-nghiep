-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Máy chủ: 127.0.0.1
-- Thời gian đã tạo: Th1 19, 2026 lúc 05:16 PM
-- Phiên bản máy phục vụ: 10.4.32-MariaDB
-- Phiên bản PHP: 8.0.30

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Cơ sở dữ liệu: `cinema_booking`
--

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `bookings`
--

CREATE TABLE `bookings` (
  `id` int(11) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `showtime_id` int(11) NOT NULL,
  `booking_time` datetime DEFAULT current_timestamp(),
  `total_price` int(11) DEFAULT NULL,
  `status` varchar(20) DEFAULT 'pending'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Đang đổ dữ liệu cho bảng `bookings`
--

INSERT INTO `bookings` (`id`, `user_id`, `showtime_id`, `booking_time`, `total_price`, `status`) VALUES
(1, 3, 3, '2026-01-17 23:31:40', 330000, 'pending'),
(3, 3, 20, '2026-01-19 20:47:17', 335000, 'paid');

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `booking_combos`
--

CREATE TABLE `booking_combos` (
  `booking_id` int(11) NOT NULL,
  `combo_id` int(11) NOT NULL,
  `quantity` int(11) DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Đang đổ dữ liệu cho bảng `booking_combos`
--

INSERT INTO `booking_combos` (`booking_id`, `combo_id`, `quantity`) VALUES
(3, 1, 1);

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `booking_seats`
--

CREATE TABLE `booking_seats` (
  `booking_id` int(11) NOT NULL,
  `seat_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Đang đổ dữ liệu cho bảng `booking_seats`
--

INSERT INTO `booking_seats` (`booking_id`, `seat_id`) VALUES
(1, 245),
(1, 246),
(1, 259),
(3, 273),
(3, 290);

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `cinemas`
--

CREATE TABLE `cinemas` (
  `id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `address` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Đang đổ dữ liệu cho bảng `cinemas`
--

INSERT INTO `cinemas` (`id`, `name`, `address`) VALUES
(1, 'KUNCINEMA Hà Nội ', 'Hà Nội'),
(2, 'KUNCINEMA HCM', 'TP.HCM'),
(3, 'KUNCINEMA Ba Đình', 'Hà Nội '),
(4, 'KUNCINEMA Biên Hòa', 'TP.HCM');

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `combos`
--

CREATE TABLE `combos` (
  `id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `description` text DEFAULT NULL,
  `price` int(11) NOT NULL,
  `type` enum('combo','single') NOT NULL DEFAULT 'combo'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Đang đổ dữ liệu cho bảng `combos`
--

INSERT INTO `combos` (`id`, `name`, `description`, `price`, `type`) VALUES
(1, 'Combo Vàng', '1 Bắp L + 1 Nước L', 85000, 'combo'),
(2, 'Combo Đôi', '1 Bắp L + 2 Nước L', 110000, 'combo'),
(3, 'Bắp rang nhỏ', '1 bắp rang bơ size S', 35000, 'single'),
(4, 'Bắp rang lớn', '1 bắp rang bơ size L', 55000, 'single'),
(5, 'Nước ngọt', '1 chai Coca / Pepsi', 25000, 'single'),
(6, 'Nước suối', '1 chai nước suối', 20000, 'single');

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `movies`
--

CREATE TABLE `movies` (
  `id` int(11) NOT NULL,
  `title` varchar(255) NOT NULL,
  `director` varchar(255) DEFAULT NULL,
  `cast` text DEFAULT NULL,
  `genre` varchar(100) DEFAULT NULL,
  `release_date` date DEFAULT NULL,
  `duration` int(11) DEFAULT NULL,
  `language` varchar(100) DEFAULT NULL,
  `age_rating` varchar(10) DEFAULT NULL,
  `rating` decimal(3,1) DEFAULT NULL,
  `price` int(11) DEFAULT NULL,
  `description` text DEFAULT NULL,
  `poster_image` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Đang đổ dữ liệu cho bảng `movies`
--

INSERT INTO `movies` (`id`, `title`, `director`, `cast`, `genre`, `release_date`, `duration`, `language`, `age_rating`, `rating`, `price`, `description`, `poster_image`) VALUES
(1, 'Zootopia 2', 'Jared Bush', 'Jason Bateman, Quinta Brunson, Fortune Feimster', 'Gia đình, Hành động, Phiêu lưu', '2025-11-28', 120, 'Tiếng Anh', '13+', 8.5, 80000, 'Tiếp nối những cuộc phiêu lưu của Cáo và Thỏ', 'movie1.jpg'),
(2, 'Jujutsu Kaisen: Shibuya', 'Park Sunghoo', 'Yuuichi Nakamura, Asami Seto, Junya Enoki', 'Anime, Hành động, Siêu nhiên, Kỳ ảo', '2024-12-24', 144, 'Tiếng Nhật', '16+', 9.0, 100000, 'Biến cố Shibuya', 'movie2.jpg'),
(3, 'Chainsaw Man Movie', 'Motonobu Hori', 'Kikunosuke Toya, Maaya Uchida, Tomokazu Seki', 'Anime, Hành động, Kinh dị, Hài hước', '2025-02-15', 109, 'Tiếng Nhật', '18+', 8.8, 110000, 'Chương Reze', 'movie3.jpg'),
(4, 'Demon Slayer: Infinity Castle', 'Haruo Sotozaki', 'Natsuki Hanae, Akari Kitou, Hiro Shimono', 'Anime, Hành động, Giả tưởng, Siêu nhiên', '2024-12-31', 110, 'Tiếng Nhật', '18+', 9.8, 125000, 'Trận chiến vô hạn', 'movie4.jpg'),
(5, 'Five Nights at Freddy’s 2', 'Emma Tammi', 'Josh Hutcherson, Matthew Lillard, Piper Rubio', 'Kinh dị, Bí ẩn, Hồi hộp', '2024-12-14', 115, 'Tiếng Anh', '18+', 8.5, 95000, 'Chuỗi sự kiện rùng rợn', 'movie5.jpg'),
(6, 'Avatar: Fire and Ash', 'James Cameron', 'Sam Worthington, Zoe Saldana, Sigourney Weaver', 'Khoa Học Viễn Tưởng, Phiêu Lưu, Sử thi', '2024-12-20', 110, 'Tiếng Anh', '18+', 9.5, 150000, 'Hành trình sử thi', 'movie6.jpg'),
(7, '5 CENTIMET TRÊN GIÂY', 'Makoto Shinkai', 'Yoshito Isomaki, Mika Shinoda', 'Hoạt Hình, Tình cảm', '2024-11-28', 115, 'Tiếng Nhật', '13+', 8.7, 100000, 'Câu chuyện nhẹ nhàng, cảm xúc về những khoảnh khắc nhỏ bé.', 'movie7.jpg'),
(8, 'Conan : Dư Ảnh Của Độc Nhãn', 'Yuzuru Tachikawa', 'Minami Takayama, Wakana Yamazaki', 'Hành Động, Hoạt Hình', '2024-10-27', 115, 'Tiếng Nhật', '13+', 9.0, 90000, 'Hành động giải đố cùng các pha rượt đuổi kịch tính.', 'movie8.jpg'),
(9, 'Ngôi Đền Tử Thần', 'Trần Hữu Tấn', 'Samuel An, Phương Anh Đào', 'Kinh dị, Tâm linh', '2026-01-20', 110, 'Tiếng Việt', '18+', 8.6, 90000, 'Một nhóm người vô tình bước vào ngôi đền bị nguyền rủa và đối mặt với những thế lực siêu nhiên.', 'movie9.jpg'),
(10, 'Linh Trưởng', 'Lê Thanh Sơn', 'Kaity Nguyễn, Quốc Trường', 'Kinh dị, Bí ẩn', '2026-02-15', 115, 'Tiếng Việt', '18+', 8.8, 95000, 'Câu chuyện về nghi lễ cổ xưa và linh hồn bị giam cầm qua nhiều thế hệ.', 'movie10.jpg'),
(11, 'Mortal Kombat 2', 'Simon McQuoid', 'Lewis Tan, Joe Taslim, Hiroyuki Sanada', 'Hành động, Võ thuật, Giả tưởng', '2026-04-05', 125, 'Tiếng Anh', '18+', 9.0, 140000, 'Cuộc chiến sinh tử giữa các chiến binh mạnh nhất của hai thế giới tiếp tục.', 'movie11.jpg'),
(12, 'Moana (Live Action)', 'Thomas Kail', 'Dwayne Johnson, Catherine Laga’aia', 'Phiêu lưu, Gia đình, Giả tưởng', '2026-06-10', 130, 'Tiếng Anh', '13+', 9.1, 130000, 'Hành trình mới của Moana trên đại dương trong phiên bản người đóng.', 'movie12.jpg');

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `payments`
--

CREATE TABLE `payments` (
  `id` int(11) NOT NULL,
  `booking_id` int(11) NOT NULL,
  `amount` int(11) NOT NULL,
  `method` varchar(50) DEFAULT NULL,
  `status` varchar(50) DEFAULT NULL,
  `paid_at` datetime DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `screens`
--

CREATE TABLE `screens` (
  `id` int(11) NOT NULL,
  `cinema_id` int(11) NOT NULL,
  `name` varchar(100) DEFAULT NULL,
  `capacity` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Đang đổ dữ liệu cho bảng `screens`
--

INSERT INTO `screens` (`id`, `cinema_id`, `name`, `capacity`) VALUES
(1, 1, 'Phòng 01', 60),
(2, 2, 'Phòng 02', 60),
(3, 1, 'Phòng 03', 80),
(4, 3, 'Phòng 04', 80),
(5, 4, 'Phòng 05', 100),
(6, 2, 'Phòng 06', 120),
(7, 4, 'Phòng 07', 150),
(8, 3, 'Phòng 08', 150);

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `seats`
--

CREATE TABLE `seats` (
  `id` int(11) NOT NULL,
  `screen_id` int(11) NOT NULL,
  `seat_row` varchar(5) DEFAULT NULL,
  `seat_col` int(11) DEFAULT NULL,
  `label` varchar(10) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Đang đổ dữ liệu cho bảng `seats`
--

INSERT INTO `seats` (`id`, `screen_id`, `seat_row`, `seat_col`, `label`) VALUES
(177, 1, 'A', 1, 'A1'),
(178, 1, 'A', 2, 'A2'),
(179, 1, 'A', 3, 'A3'),
(180, 1, 'A', 4, 'A4'),
(181, 1, 'A', 5, 'A5'),
(182, 1, 'A', 6, 'A6'),
(183, 1, 'A', 7, 'A7'),
(184, 1, 'A', 8, 'A8'),
(185, 1, 'A', 9, 'A9'),
(186, 1, 'A', 10, 'A10'),
(187, 1, 'B', 1, 'B1'),
(188, 1, 'B', 2, 'B2'),
(189, 1, 'B', 3, 'B3'),
(190, 1, 'B', 4, 'B4'),
(191, 1, 'B', 5, 'B5'),
(192, 1, 'B', 6, 'B6'),
(193, 1, 'B', 7, 'B7'),
(194, 1, 'B', 8, 'B8'),
(195, 1, 'B', 9, 'B9'),
(196, 1, 'B', 10, 'B10'),
(197, 1, 'C', 1, 'C1'),
(198, 1, 'C', 2, 'C2'),
(199, 1, 'C', 3, 'C3'),
(200, 1, 'C', 4, 'C4'),
(201, 1, 'C', 5, 'C5'),
(202, 1, 'C', 6, 'C6'),
(203, 1, 'C', 7, 'C7'),
(204, 1, 'C', 8, 'C8'),
(205, 1, 'C', 9, 'C9'),
(206, 1, 'C', 10, 'C10'),
(207, 1, 'D', 1, 'D1'),
(208, 1, 'D', 2, 'D2'),
(209, 1, 'D', 3, 'D3'),
(210, 1, 'D', 4, 'D4'),
(211, 1, 'D', 5, 'D5'),
(212, 1, 'D', 6, 'D6'),
(213, 1, 'D', 7, 'D7'),
(214, 1, 'D', 8, 'D8'),
(215, 1, 'D', 9, 'D9'),
(216, 1, 'D', 10, 'D10'),
(217, 1, 'E', 1, 'E1'),
(218, 1, 'E', 2, 'E2'),
(219, 1, 'E', 3, 'E3'),
(220, 1, 'E', 4, 'E4'),
(221, 1, 'E', 5, 'E5'),
(222, 1, 'F', 1, 'F1'),
(223, 1, 'F', 2, 'F2'),
(224, 1, 'F', 3, 'F3'),
(225, 1, 'F', 4, 'F4'),
(226, 1, 'F', 5, 'F5'),
(227, 2, 'A', 1, 'A1'),
(228, 2, 'A', 2, 'A2'),
(229, 2, 'A', 3, 'A3'),
(230, 2, 'A', 4, 'A4'),
(231, 2, 'A', 5, 'A5'),
(232, 2, 'A', 6, 'A6'),
(233, 2, 'A', 7, 'A7'),
(234, 2, 'A', 8, 'A8'),
(235, 2, 'B', 1, 'B1'),
(236, 2, 'B', 2, 'B2'),
(237, 2, 'B', 3, 'B3'),
(238, 2, 'B', 4, 'B4'),
(239, 2, 'B', 5, 'B5'),
(240, 2, 'B', 6, 'B6'),
(241, 2, 'B', 7, 'B7'),
(242, 2, 'B', 8, 'B8'),
(243, 2, 'C', 1, 'C1'),
(244, 2, 'C', 2, 'C2'),
(245, 2, 'C', 3, 'C3'),
(246, 2, 'C', 4, 'C4'),
(247, 2, 'C', 5, 'C5'),
(248, 2, 'C', 6, 'C6'),
(249, 2, 'C', 7, 'C7'),
(250, 2, 'C', 8, 'C8'),
(251, 2, 'D', 1, 'D1'),
(252, 2, 'D', 2, 'D2'),
(253, 2, 'D', 3, 'D3'),
(254, 2, 'D', 4, 'D4'),
(255, 2, 'D', 5, 'D5'),
(256, 2, 'D', 6, 'D6'),
(257, 2, 'D', 7, 'D7'),
(258, 2, 'D', 8, 'D8'),
(259, 2, 'E', 1, 'E1'),
(260, 2, 'E', 2, 'E2'),
(261, 2, 'E', 3, 'E3'),
(262, 2, 'E', 4, 'E4'),
(263, 2, 'E', 5, 'E5'),
(264, 2, 'E', 6, 'E6'),
(265, 2, 'E', 7, 'E7'),
(266, 2, 'E', 8, 'E8'),
(267, 3, 'A', 1, 'A1'),
(268, 3, 'A', 2, 'A2'),
(269, 3, 'A', 3, 'A3'),
(270, 3, 'A', 4, 'A4'),
(271, 3, 'A', 5, 'A5'),
(272, 3, 'A', 6, 'A6'),
(273, 3, 'A', 7, 'A7'),
(274, 3, 'A', 8, 'A8'),
(275, 3, 'B', 1, 'B1'),
(276, 3, 'B', 2, 'B2'),
(277, 3, 'B', 3, 'B3'),
(278, 3, 'B', 4, 'B4'),
(279, 3, 'B', 5, 'B5'),
(280, 3, 'B', 6, 'B6'),
(281, 3, 'B', 7, 'B7'),
(282, 3, 'B', 8, 'B8'),
(283, 3, 'C', 1, 'C1'),
(284, 3, 'C', 2, 'C2'),
(285, 3, 'C', 3, 'C3'),
(286, 3, 'C', 4, 'C4'),
(287, 3, 'C', 5, 'C5'),
(288, 3, 'C', 6, 'C6'),
(289, 3, 'C', 7, 'C7'),
(290, 3, 'C', 8, 'C8'),
(291, 3, 'D', 1, 'D1'),
(292, 3, 'D', 2, 'D2'),
(293, 3, 'D', 3, 'D3'),
(294, 3, 'D', 4, 'D4'),
(295, 3, 'D', 5, 'D5'),
(296, 3, 'D', 6, 'D6'),
(297, 3, 'D', 7, 'D7'),
(298, 3, 'D', 8, 'D8'),
(299, 3, 'E', 1, 'E1'),
(300, 3, 'E', 2, 'E2'),
(301, 3, 'E', 3, 'E3'),
(302, 3, 'E', 4, 'E4'),
(303, 3, 'E', 5, 'E5'),
(304, 3, 'E', 6, 'E6'),
(305, 3, 'E', 7, 'E7'),
(306, 3, 'E', 8, 'E8'),
(307, 4, 'A', 1, 'A1'),
(308, 4, 'A', 2, 'A2'),
(309, 4, 'A', 3, 'A3'),
(310, 4, 'A', 4, 'A4'),
(311, 4, 'A', 5, 'A5'),
(312, 4, 'A', 6, 'A6'),
(313, 4, 'A', 7, 'A7'),
(314, 4, 'A', 8, 'A8'),
(315, 4, 'B', 1, 'B1'),
(316, 4, 'B', 2, 'B2'),
(317, 4, 'B', 3, 'B3'),
(318, 4, 'B', 4, 'B4'),
(319, 4, 'B', 5, 'B5'),
(320, 4, 'B', 6, 'B6'),
(321, 4, 'B', 7, 'B7'),
(322, 4, 'B', 8, 'B8'),
(323, 4, 'C', 1, 'C1'),
(324, 4, 'C', 2, 'C2'),
(325, 4, 'C', 3, 'C3'),
(326, 4, 'C', 4, 'C4'),
(327, 4, 'C', 5, 'C5'),
(328, 4, 'C', 6, 'C6'),
(329, 4, 'C', 7, 'C7'),
(330, 4, 'C', 8, 'C8'),
(331, 4, 'D', 1, 'D1'),
(332, 4, 'D', 2, 'D2'),
(333, 4, 'D', 3, 'D3'),
(334, 4, 'D', 4, 'D4'),
(335, 4, 'D', 5, 'D5'),
(336, 4, 'D', 6, 'D6'),
(337, 4, 'D', 7, 'D7'),
(338, 4, 'D', 8, 'D8'),
(339, 4, 'E', 1, 'E1'),
(340, 4, 'E', 2, 'E2'),
(341, 4, 'E', 3, 'E3'),
(342, 4, 'E', 4, 'E4'),
(343, 4, 'E', 5, 'E5'),
(344, 4, 'E', 6, 'E6'),
(345, 4, 'E', 7, 'E7'),
(346, 4, 'E', 8, 'E8');

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `showtimes`
--

CREATE TABLE `showtimes` (
  `id` int(11) NOT NULL,
  `movie_id` int(11) NOT NULL,
  `screen_id` int(11) NOT NULL,
  `start_time` datetime NOT NULL,
  `price` int(11) DEFAULT NULL,
  `seats_available` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Đang đổ dữ liệu cho bảng `showtimes`
--

INSERT INTO `showtimes` (`id`, `movie_id`, `screen_id`, `start_time`, `price`, `seats_available`) VALUES
(1, 1, 4, '2025-12-30 14:30:00', 80000, 60),
(2, 2, 1, '2025-12-30 19:00:00', 100000, 60),
(3, 3, 2, '2025-01-20 10:40:00', 110000, 60),
(4, 4, 2, '2025-12-30 16:00:00', 125000, 60),
(5, 5, 2, '2025-12-04 14:55:00', 95000, 60),
(7, 7, 2, '2025-12-30 21:30:00', 100000, 60),
(10, 1, 4, '2025-12-20 14:00:00', 80000, 60),
(12, 2, 4, '2025-12-21 09:30:00', 100000, 60),
(15, 3, 3, '2025-12-22 10:15:00', 110000, 60),
(20, 4, 3, '2025-12-23 20:30:00', 125000, 60),
(21, 5, 1, '2025-12-24 10:00:00', 95000, 60),
(23, 5, 3, '2025-12-24 19:45:00', 95000, 60),
(25, 6, 4, '2025-12-25 15:15:00', 150000, 60),
(27, 7, 1, '2025-12-26 10:30:00', 100000, 60),
(28, 7, 3, '2025-12-26 16:00:00', 100000, 60),
(29, 7, 2, '2025-12-26 20:30:00', 100000, 60),
(30, 8, 1, '2025-12-27 11:00:00', 90000, 60),
(32, 8, 4, '2025-12-27 21:15:00', 90000, 60);

-- --------------------------------------------------------

--
-- Cấu trúc bảng cho bảng `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `username` varchar(100) NOT NULL,
  `email` varchar(255) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `created_at` datetime DEFAULT current_timestamp(),
  `role` enum('user','admin') DEFAULT 'user'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Đang đổ dữ liệu cho bảng `users`
--

INSERT INTO `users` (`id`, `username`, `email`, `password_hash`, `phone`, `created_at`, `role`) VALUES
(3, 'Minh Nam', 'mn@gmail.com', 'scrypt:32768:8:1$aTE6aLDt0aDQR2rJ$28bc0221a485424e2f43f4d9544719dc2729e34d01dc1f70baebd6ed5687e291f2ab8d459ab7d018566a7cf2fa2d395e03bf708930fd167caea5f2a380e0a1c4', '123456', '2026-01-08 11:50:04', 'admin'),
(4, 'Minhnamcun', 'Minhnamcun@gmail.com', 'scrypt:32768:8:1$eeagdjC5CuXA8tWd$ce406ecf69e44e48a1d797617ed98760a199932563687c5fc3763e4d4ce6ae77b0281992d7711681692a0f0382a5960e38355ef98ea8e49edd31ea430a55dd66', '123456', '2026-01-09 09:55:02', 'user');

--
-- Chỉ mục cho các bảng đã đổ
--

--
-- Chỉ mục cho bảng `bookings`
--
ALTER TABLE `bookings`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`),
  ADD KEY `showtime_id` (`showtime_id`);

--
-- Chỉ mục cho bảng `booking_combos`
--
ALTER TABLE `booking_combos`
  ADD PRIMARY KEY (`booking_id`,`combo_id`),
  ADD KEY `combo_id` (`combo_id`);

--
-- Chỉ mục cho bảng `booking_seats`
--
ALTER TABLE `booking_seats`
  ADD PRIMARY KEY (`booking_id`,`seat_id`),
  ADD KEY `seat_id` (`seat_id`);

--
-- Chỉ mục cho bảng `cinemas`
--
ALTER TABLE `cinemas`
  ADD PRIMARY KEY (`id`);

--
-- Chỉ mục cho bảng `combos`
--
ALTER TABLE `combos`
  ADD PRIMARY KEY (`id`);

--
-- Chỉ mục cho bảng `movies`
--
ALTER TABLE `movies`
  ADD PRIMARY KEY (`id`);

--
-- Chỉ mục cho bảng `payments`
--
ALTER TABLE `payments`
  ADD PRIMARY KEY (`id`),
  ADD KEY `booking_id` (`booking_id`);

--
-- Chỉ mục cho bảng `screens`
--
ALTER TABLE `screens`
  ADD PRIMARY KEY (`id`),
  ADD KEY `cinema_id` (`cinema_id`);

--
-- Chỉ mục cho bảng `seats`
--
ALTER TABLE `seats`
  ADD PRIMARY KEY (`id`),
  ADD KEY `screen_id` (`screen_id`);

--
-- Chỉ mục cho bảng `showtimes`
--
ALTER TABLE `showtimes`
  ADD PRIMARY KEY (`id`),
  ADD KEY `movie_id` (`movie_id`),
  ADD KEY `screen_id` (`screen_id`);

--
-- Chỉ mục cho bảng `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`),
  ADD UNIQUE KEY `email` (`email`);

--
-- AUTO_INCREMENT cho các bảng đã đổ
--

--
-- AUTO_INCREMENT cho bảng `bookings`
--
ALTER TABLE `bookings`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT cho bảng `cinemas`
--
ALTER TABLE `cinemas`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- AUTO_INCREMENT cho bảng `combos`
--
ALTER TABLE `combos`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT cho bảng `movies`
--
ALTER TABLE `movies`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=13;

--
-- AUTO_INCREMENT cho bảng `payments`
--
ALTER TABLE `payments`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT cho bảng `screens`
--
ALTER TABLE `screens`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=15;

--
-- AUTO_INCREMENT cho bảng `seats`
--
ALTER TABLE `seats`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=347;

--
-- AUTO_INCREMENT cho bảng `showtimes`
--
ALTER TABLE `showtimes`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=34;

--
-- AUTO_INCREMENT cho bảng `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=5;

--
-- Các ràng buộc cho các bảng đã đổ
--

--
-- Các ràng buộc cho bảng `bookings`
--
ALTER TABLE `bookings`
  ADD CONSTRAINT `bookings_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE SET NULL,
  ADD CONSTRAINT `bookings_ibfk_2` FOREIGN KEY (`showtime_id`) REFERENCES `showtimes` (`id`) ON DELETE CASCADE;

--
-- Các ràng buộc cho bảng `booking_combos`
--
ALTER TABLE `booking_combos`
  ADD CONSTRAINT `booking_combos_ibfk_1` FOREIGN KEY (`booking_id`) REFERENCES `bookings` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `booking_combos_ibfk_2` FOREIGN KEY (`combo_id`) REFERENCES `combos` (`id`) ON DELETE CASCADE;

--
-- Các ràng buộc cho bảng `booking_seats`
--
ALTER TABLE `booking_seats`
  ADD CONSTRAINT `booking_seats_ibfk_1` FOREIGN KEY (`booking_id`) REFERENCES `bookings` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `booking_seats_ibfk_2` FOREIGN KEY (`seat_id`) REFERENCES `seats` (`id`) ON DELETE CASCADE;

--
-- Các ràng buộc cho bảng `payments`
--
ALTER TABLE `payments`
  ADD CONSTRAINT `payments_ibfk_1` FOREIGN KEY (`booking_id`) REFERENCES `bookings` (`id`) ON DELETE CASCADE;

--
-- Các ràng buộc cho bảng `screens`
--
ALTER TABLE `screens`
  ADD CONSTRAINT `screens_ibfk_1` FOREIGN KEY (`cinema_id`) REFERENCES `cinemas` (`id`) ON DELETE CASCADE;

--
-- Các ràng buộc cho bảng `seats`
--
ALTER TABLE `seats`
  ADD CONSTRAINT `seats_ibfk_1` FOREIGN KEY (`screen_id`) REFERENCES `screens` (`id`) ON DELETE CASCADE;

--
-- Các ràng buộc cho bảng `showtimes`
--
ALTER TABLE `showtimes`
  ADD CONSTRAINT `showtimes_ibfk_1` FOREIGN KEY (`movie_id`) REFERENCES `movies` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `showtimes_ibfk_2` FOREIGN KEY (`screen_id`) REFERENCES `screens` (`id`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
