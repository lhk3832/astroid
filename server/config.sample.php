<?php
// 이 파일을 config.php 라는 이름으로 복사해서 값을 채운 뒤, scores.php와 같은 폴더에 올린다.
// config.php는 비밀번호가 들어 있어서 GitHub에는 올리지 않는다 (.gitignore에 들어 있다).

define('DB_HOST', 'localhost');        // 카페24 호스팅 관리의 DB 정보에 적힌 접속 호스트
define('DB_NAME', '');                 // DB 이름
define('DB_USER', '');                 // DB 아이디
define('DB_PASS', '');                 // DB 비밀번호

define('ALLOWED_ORIGIN', 'https://lhk3832.github.io');  // 이 주소의 게임만 순위표를 쓸 수 있다
define('IP_SALT', 'change-this-to-any-long-random-text');  // 아무 긴 글자로 바꾼다
