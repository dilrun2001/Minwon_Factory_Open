-- init.sql

-- 데이터베이스가 존재하지 않으면 새로 생성합니다.
-- 문자셋 설정을 utf8mb4로 하여 한글 및 이모티콘이 깨지지 않도록 합니다.
CREATE DATABASE IF NOT EXISTS minwon CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 애플리케이션 전용 사용자를 생성합니다.
-- 'app_user'@'%' : '%'는 어떤 IP 주소(호스트)에서든 접속을 허용하겠다는 의미입니다.
-- IDENTIFIED BY : 사용자의 비밀번호를 설정합니다.
CREATE USER IF NOT EXISTS 'root'@'%' IDENTIFIED BY '1234';

-- 생성한 사용자에게 'minwon' 데이터베이스에 대한 모든 권한을 부여합니다.
-- 이 사용자는 다른 데이터베이스에는 접근할 수 없습니다.
GRANT ALL PRIVILEGES ON minwon.* TO 'root'@'%';

-- 변경된 권한 설정을 즉시 시스템에 적용합니다.
FLUSH PRIVILEGES;

USE minwon;

CREATE TABLE `task_queue` (  `id` int NOT NULL AUTO_INCREMENT,  `user_id` varchar(64) DEFAULT NULL,  `status` enum('waiting','processing','done') DEFAULT 'waiting',  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,  PRIMARY KEY (`id`)) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
CREATE TABLE `history` (  `timestamp` datetime DEFAULT NULL,  `name` varchar(100) DEFAULT NULL,  `category` varchar(100) DEFAULT NULL,  `urgency` varchar(100) DEFAULT NULL,  `minwon` text,  `response` text,  `grade` int DEFAULT NULL,  `answer_yogi` text) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;