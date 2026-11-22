-- Astroid 공용 순위표 보호 설정 (Supabase SQL Editor에서 한 번 실행한다. 여러 번 실행해도 된다).
-- 1) 이름 규칙  2) 점수 상한(플레이 시간에 묶음)  3) 금칙어 + 접속자별 속도 제한  4) 관리용 숨김 칸
-- 규칙은 "새로 들어오는 점수"에만 적용된다 (이미 있는 점수는 그대로).

-- ── 칸 추가 ─────────────────────────────────────────────
alter table scores add column if not exists hidden boolean not null default false;  -- true면 순위표에서 빠진다 (Table Editor에서 직접 켠다)
alter table scores add column if not exists ip_hash text;                           -- 속도 제한용 (접속 주소를 섞어서 줄인 값만 저장)

-- ── 값 규칙 ─────────────────────────────────────────────
-- 이름: 앞뒤 공백 없이 영문, 숫자, 한글, 공백, _ . - 만 (길이 1~10은 기존 규칙)
alter table scores drop constraint if exists scores_player_chars;
alter table scores add constraint scores_player_chars
  check (player = btrim(player) and player ~ '^[A-Za-z0-9가-힣 _.-]+$') not valid;

-- 전투기 이름
alter table scores drop constraint if exists scores_ship_ok;
alter table scores add constraint scores_ship_ok
  check (ship is null or ship in ('Normal', 'Tanker', 'Attack')) not valid;

-- 레벨: 1 이상, 점수로 나올 수 있는 레벨 이하 (게임은 150점마다 1레벨)
alter table scores drop constraint if exists scores_level_ok;
alter table scores add constraint scores_level_ok
  check (level is null or (level >= 1 and level <= score / 150 + 1)) not valid;

-- 점수 상한: 플레이 시간(초) 1~86400, 점수는 시간 x 100 + 1000 이하 (진짜 플레이는 이보다 훨씬 낮다)
alter table scores drop constraint if exists scores_time_ok;
alter table scores add constraint scores_time_ok
  check (play_time is not null and play_time between 1 and 86400 and score <= play_time * 100 + 1000) not valid;

-- ── 금칙어와 속도 제한 (점수가 들어오기 직전에 검사) ──────────────
create or replace function scores_guard() returns trigger
language plpgsql security definer set search_path = public as $$
declare
  banned text[] := array['시발','씨발','병신','지랄','좆','개새','엿먹','fuck','shit','nigg','porn','http','www'];
  w text;
  low text := lower(replace(new.player, ' ', ''));
  ip text;
begin
  foreach w in array banned loop
    if position(w in low) > 0 then
      raise exception 'name not allowed';
    end if;
  end loop;

  -- 같은 접속자는 1분에 5번까지 (접속 주소는 요청 머리글에서 읽고, 섞어서 줄인 값만 저장)
  ip := split_part(coalesce(current_setting('request.headers', true)::json->>'x-forwarded-for', ''), ',', 1);
  if ip <> '' then
    new.ip_hash := md5(ip || 'astroid-ip-salt');
    if (select count(*) from scores
        where ip_hash = new.ip_hash and created_at > now() - interval '60 seconds') >= 5 then
      raise exception 'too many scores';
    end if;
  end if;

  new.hidden := false;  -- 숨김은 관리자만 켠다
  return new;
end $$;

drop trigger if exists scores_guard_trg on scores;
create trigger scores_guard_trg before insert on scores
  for each row execute function scores_guard();

-- ── 읽기/쓰기 권한 ───────────────────────────────────────
-- 숨긴 행은 안 보이고, 공개 키로는 ip_hash/hidden 칸을 읽거나 쓸 수 없다
drop policy if exists "anyone can read" on scores;
create policy "anyone can read" on scores for select using (hidden = false);

revoke select, insert on public.scores from anon;
grant select (id, mode, score, player, ship, level, play_time, created_at) on public.scores to anon;
grant insert (mode, score, player, ship, level, play_time) on public.scores to anon;
