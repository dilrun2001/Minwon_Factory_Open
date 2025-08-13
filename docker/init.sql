-- 데이터베이스가 존재하지 않으면 새로 생성합니다.
-- 문자셋 설정은 그대로 유지합니다.
CREATE DATABASE IF NOT EXISTS minwon CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 'saha'라는 애플리케이션 전용 사용자를 생성합니다.
-- 🔑 비밀번호는 더 안전한 것으로 변경해서 사용하세요.
CREATE USER IF NOT EXISTS 'saha'@'%' IDENTIFIED BY 'rlghlr0133!';

-- 생성한 'saha' 사용자에게 'minwon' 데이터베이스에 대한 모든 권한만 부여합니다.
GRANT ALL PRIVILEGES ON minwon.* TO 'saha'@'%';

-- 변경된 권한 설정을 즉시 시스템에 적용합니다.
FLUSH PRIVILEGES;

-- 이 아래 테이블 생성 구문은 그대로 사용하시면 됩니다.
USE minwon;

CREATE TABLE `task_queue` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` varchar(64) DEFAULT NULL,
  `status` enum('waiting','processing','done') DEFAULT 'waiting',
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

CREATE TABLE `history` (
  `timestamp` datetime DEFAULT NULL,
  `name` varchar(100) DEFAULT NULL,
  `category` varchar(100) DEFAULT NULL,
  `urgency` varchar(100) DEFAULT NULL,
  `minwon` text,
  `response` text,
  `grade` int DEFAULT NULL,
  `answer_yogi` text
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;