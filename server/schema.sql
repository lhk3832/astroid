-- Astroid 공용 순위표 표 (MariaDB / MySQL). phpMyAdmin의 SQL 탭에 붙여 넣고 실행한다.
CREATE TABLE IF NOT EXISTS scores (
  id INT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  mode VARCHAR(10) NOT NULL,
  score INT UNSIGNED NOT NULL,
  player VARCHAR(40) NOT NULL,
  ship VARCHAR(20) NOT NULL DEFAULT '',
  level INT NOT NULL DEFAULT 0,
  play_time INT NOT NULL DEFAULT 0,
  ip_hash CHAR(40) NOT NULL DEFAULT '',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  KEY idx_mode_score (mode, score),
  KEY idx_ip_time (ip_hash, created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
