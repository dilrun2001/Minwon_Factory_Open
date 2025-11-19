-- 데이터베이스가 존재하지 않으면 새로 생성합니다.
-- 문자셋 설정은 그대로 유지합니다.
CREATE DATABASE IF NOT EXISTS minwon CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 'saha'라는 애플리케이션 전용 사용자를 생성합니다.
-- 🔑 비밀번호는 더 안전한 것으로 변경해서 사용하세요.
CREATE USER IF NOT EXISTS 'saha'@'%' IDENTIFIED BY '1234';

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

create table `createcount` (
    `key` tinyint not null primary key,
    `ai_count` int not null default 0, 
    `mf_count` int not null default 0,
    `saha_count` int not null default 0,
    `default_count` int not null default 0,
    `recreate_count` int not null default 0,
    `xlsx` int not null default 0,
    `csv` int not null default 0,
    `total_file` int not null default 0
);
insert into createcount (`key`) values (1);

create view history_grade as
select
	count(*) as total_count,
    sum(if(h.grade = '1', 1,0)) as `1점`,
    sum(if(h.grade = '2', 1,0)) as `2점`,
    sum(if(h.grade = '3', 1,0)) as `3점`,
    sum(if(h.grade = '4', 1,0)) as `4점`,
    sum(if(h.grade = '5', 1,0)) as `5점`,
    
	round((sum(IF(h.grade = '1', 1, 0)) * 1 +
     sum(IF(h.grade = '2', 1, 0)) * 2 +
     sum(IF(h.grade = '3', 1, 0)) * 3 +
     sum(IF(h.grade = '4', 1, 0)) * 4 +
     sum(IF(h.grade = '5', 1, 0)) * 5) / count(*),1) AS `평점 평균`
from
	history as h;     
create view category_static as
with categorycount as(
	select
		sum(if(h.category = '일반', 1,0)) as `일반`,
		sum(if(h.category = '환경', 1,0)) as `환경`,
		sum(if(h.category = '교통', 1,0)) as `교통`,
		sum(if(h.category = '복지', 1,0)) as `복지`,
		sum(if(h.category = '교육', 1,0)) as `교육`,
		sum(if(h.category = '기타', 1,0)) as `기타`
	from
		history h
)
select
	t.*,
    greatest(t.`일반`, t.`환경`, t.`교통`, t.`교육`, t.`기타`) as `최다 카테고리 횟수`,
    concat_ws(', ',
		if(t.`일반` = greatest(t.`일반`, t.`환경`, t.`교통`, t.`복지`, t.`교육`, t.`기타`), '일반', NULL),
        if(t.`환경` = greatest(t.`일반`, t.`환경`, t.`교통`, t.`복지`, t.`교육`, t.`기타`), '환경', NULL),
        if(t.`교통` = greatest(t.`일반`, t.`환경`, t.`교통`, t.`복지`, t.`교육`, t.`기타`), '교통', NULL),
        if(t.`복지` = greatest(t.`일반`, t.`환경`, t.`교통`, t.`복지`, t.`교육`, t.`기타`), '복지', NULL),
        if(t.`교육` = greatest(t.`일반`, t.`환경`, t.`교통`, t.`복지`, t.`교육`, t.`기타`), '교육', NULL),
        if(t.`기타` = greatest(t.`일반`, t.`환경`, t.`교통`, t.`복지`, t.`교육`, t.`기타`), '기타', NULL)
        ) as `최다 카테고리 이름`
	from categorycount t;
    
create view urgency_static as
with categorycount as(
	select
		sum(if(h.urgency = '매우 낮음', 1,0)) as `매우 낮음`,
		sum(if(h.urgency = '낮음', 1,0)) as `낮음`,
		sum(if(h.urgency = '보통', 1,0)) as `보통`,
		sum(if(h.urgency = '높음', 1,0)) as `높음`,
		sum(if(h.urgency = '매우 높음', 1,0)) as `매우 높음`
	from
		history h
)
select
	t.*,
    greatest(t.`매우 낮음`, t.`낮음`, t.`보통`, t.`높음`, t.`매우 높음`) as `최다 긴급도 횟수`,
    concat_ws(', ',
		if(t.`매우 낮음` = greatest(t.`매우 낮음`, t.`낮음`, t.`보통`, t.`높음`, t.`매우 높음`), '매우 낮음', NULL),
        if(t.`낮음` = greatest(t.`매우 낮음`, t.`낮음`, t.`보통`, t.`높음`, t.`매우 높음`), '낮음', NULL),
        if(t.`보통` = greatest(t.`매우 낮음`, t.`낮음`, t.`보통`, t.`높음`, t.`매우 높음`), '보통', NULL),
        if(t.`높음` = greatest(t.`매우 낮음`, t.`낮음`, t.`보통`, t.`높음`, t.`매우 높음`), '높음', NULL),
        if(t.`매우 높음` = greatest(t.`매우 낮음`, t.`낮음`, t.`보통`, t.`높음`, t.`매우 높음`), '매우 높음', NULL)
        ) as `최다 긴급도 이름`
	from categorycount t;
    
create view ai_static as
with aicount as(
select 
	ai_count as `AI 전체 사용 횟수`,
    mf_count as `민원팩토리 모델 횟수`,
    saha_count as `사하아이 요청 횟수`,
	default_count as `기본 모델 횟수`,
    recreate_count as `답변 재생성 횟수`
from createcount
)
select
	t.*,
	greatest(t.`민원팩토리 모델 횟수`, t.`사하아이 요청 횟수`, t.`기본 모델 횟수`) as `최다 생성 횟수`,
	concat_ws(', ',
		if(t.`민원팩토리 모델 횟수` = greatest(t.`민원팩토리 모델 횟수`, t.`사하아이 요청 횟수`, t.`기본 모델 횟수`), '민원팩토리 모델 횟수', NULL),
        if(t.`사하아이 요청 횟수` = greatest(t.`민원팩토리 모델 횟수`, t.`사하아이 요청 횟수`, t.`기본 모델 횟수`), '사하아이 요청 횟수', NULL),
        if(t.`기본 모델 횟수` = greatest(t.`민원팩토리 모델 횟수`, t.`사하아이 요청 횟수`, t.`기본 모델 횟수`), '기본 모델 횟수', NULL)
        ) as `최다 생성 모델 이름`
	from aicount as t;

create view file_static as
select
    xlsx as `엑셀 파일 생성 횟수`,
    csv as `CSV 파일 생성 횟수`,
    total_file as `전체 파일 횟수`
from createcount;