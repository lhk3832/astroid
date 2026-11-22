<?php
// Astroid 공용 순위표 서버 (PHP + MariaDB/MySQL)
//   GET  scores.php?mode=Normal&limit=10  -> 그 모드의 1~10위 (JSON 배열)
//   POST scores.php  (본문: JSON {mode, score, player, ship, level, play_time}) -> 점수 한 개 추가
// 같은 폴더의 config.php(config.sample.php를 복사해서 만든다)에 DB 정보가 있다.

mysqli_report(MYSQLI_REPORT_OFF);  // PHP 8.1 이상에서 오류를 예외로 던지지 않게
require __DIR__ . '/config.php';

header('Content-Type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: ' . ALLOWED_ORIGIN);
header('Access-Control-Allow-Methods: GET, POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');
header('Cache-Control: no-store');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(204);
    exit;
}

$MODES = array('Easy', 'Normal', 'Hard');
$SHIPS = array('Normal', 'Tanker', 'Attack');
$MAX_NAME = 10;        // 이름 최대 글자 수
$POSTS_PER_MIN = 6;    // 같은 접속자가 1분에 올릴 수 있는 점수 수

function fail($code, $msg) {
    http_response_code($code);
    echo json_encode(array('error' => $msg));
    exit;
}

// 글자 수 기준으로 자르기 (한글도 1글자). mbstring이 없는 호스팅도 있어서 정규식으로 대신한다
function cut_text($s, $n) {
    if (function_exists('mb_substr')) {
        return mb_substr($s, 0, $n, 'UTF-8');
    }
    $chars = preg_split('//u', $s, -1, PREG_SPLIT_NO_EMPTY);
    return $chars ? implode('', array_slice($chars, 0, $n)) : '';
}

$db = new mysqli(DB_HOST, DB_USER, DB_PASS, DB_NAME);
if ($db->connect_errno) {
    fail(500, 'db');
}
$db->set_charset('utf8');

if ($_SERVER['REQUEST_METHOD'] === 'GET') {
    $mode = isset($_GET['mode']) ? $_GET['mode'] : '';
    if (!in_array($mode, $MODES, true)) {
        fail(400, 'mode');
    }
    $limit = isset($_GET['limit']) ? (int)$_GET['limit'] : 10;
    if ($limit < 1 || $limit > 50) {
        $limit = 10;
    }
    $stmt = $db->prepare('SELECT score, player, ship, level, play_time, created_at FROM scores WHERE mode = ? ORDER BY score DESC, id ASC LIMIT ?');
    if (!$stmt) {
        fail(500, 'query');
    }
    $stmt->bind_param('si', $mode, $limit);
    $stmt->execute();
    $stmt->bind_result($score, $player, $ship, $level, $play_time, $created_at);
    $rows = array();
    while ($stmt->fetch()) {
        $rows[] = array(
            'score' => (int)$score, 'player' => $player, 'ship' => $ship,
            'level' => (int)$level, 'play_time' => (int)$play_time, 'created_at' => $created_at,
        );
    }
    echo json_encode($rows);
    exit;
}

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $data = json_decode(file_get_contents('php://input'), true);
    if (!is_array($data)) {
        fail(400, 'json');
    }
    $mode = isset($data['mode']) ? $data['mode'] : '';
    $score = isset($data['score']) ? (int)$data['score'] : 0;
    $player = isset($data['player']) ? trim((string)$data['player']) : '';
    $ship = isset($data['ship']) ? (string)$data['ship'] : '';
    $level = isset($data['level']) ? (int)$data['level'] : 0;
    $play_time = isset($data['play_time']) ? (int)$data['play_time'] : 0;

    if (!in_array($mode, $MODES, true)) {
        fail(400, 'mode');
    }
    if ($score < 1 || $score > 1000000) {
        fail(400, 'score');
    }
    $player = cut_text($player, $MAX_NAME);
    if ($player === '') {
        $player = 'Guest';
    }
    if (!in_array($ship, $SHIPS, true)) {
        $ship = '';
    }
    $level = max(0, min(9999, $level));
    $play_time = max(0, min(86400, $play_time));

    // 같은 접속자가 너무 자주 올리지 못하게 한다 (접속 주소는 그대로 저장하지 않고 섞어서 줄인 값만 쓴다)
    $ip_hash = sha1((isset($_SERVER['REMOTE_ADDR']) ? $_SERVER['REMOTE_ADDR'] : '') . IP_SALT);
    $stmt = $db->prepare('SELECT COUNT(*) FROM scores WHERE ip_hash = ? AND created_at > (NOW() - INTERVAL 60 SECOND)');
    if (!$stmt) {
        fail(500, 'query');
    }
    $stmt->bind_param('s', $ip_hash);
    $stmt->execute();
    $stmt->bind_result($recent);
    $stmt->fetch();
    $stmt->close();
    if ($recent >= $POSTS_PER_MIN) {
        fail(429, 'too many');
    }

    $stmt = $db->prepare('INSERT INTO scores (mode, score, player, ship, level, play_time, ip_hash) VALUES (?, ?, ?, ?, ?, ?, ?)');
    if (!$stmt) {
        fail(500, 'query');
    }
    $stmt->bind_param('sissiis', $mode, $score, $player, $ship, $level, $play_time, $ip_hash);
    if (!$stmt->execute()) {
        fail(500, 'insert');
    }
    http_response_code(201);
    echo json_encode(array('ok' => true));
    exit;
}

fail(405, 'method');
