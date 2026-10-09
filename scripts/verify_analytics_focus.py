"""Explicit Phase 11 live checks using temporary synthetic users and sessions only."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from pathlib import Path
import secrets
import sys
from uuid import uuid4
from zoneinfo import ZoneInfo

import httpx
from dotenv import dotenv_values
from sqlalchemy import text

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'backend'))
from app.db.connection import get_engine
from app.repositories import analytics as analytics_repo
from app.services.analytics import local_day_range


def checked(response, expected=200):
    assert response.status_code == expected, 'Unexpected HTTP status'
    assert response.headers.get('access-control-allow-origin') == 'http://localhost:3001'
    return response.json() if expected != 204 else None


def verify_sql_arithmetic():
    """Read-only literal SQL fixtures exercise the deployed PostgreSQL arithmetic."""
    expression = analytics_repo.clipped_seconds(
        'GREATEST(started_at, CAST(:lower AS timestamptz))',
        'LEAST(ended_at, CAST(:upper AS timestamptz))')
    query = text('WITH fixture AS (SELECT CAST(:start AS timestamptz) AS started_at, '
        'CAST(:end AS timestamptz) AS ended_at, CAST(:duration AS integer) AS duration_seconds) '
        'SELECT ' + expression + ' AS seconds FROM fixture')
    with get_engine().connect() as db:
        for zone_name, day, expected in (
            ('America/New_York', datetime(2026, 3, 8).date(), 82800),
            ('America/New_York', datetime(2025, 11, 2).date(), 90000),
            ('America/Havana', datetime(2025, 11, 2).date(), 90000),
            ('America/Santiago', datetime(2026, 9, 6).date(), 82800),
        ):
            lower, upper = local_day_range(day, zone_name)
            start, end = lower - timedelta(seconds=1.25), upper + timedelta(seconds=1.75)
            seconds = db.execute(query, {'start': start, 'end': end,
                'duration': int((end - start).total_seconds()), 'lower': lower, 'upper': upper}).scalar_one()
            assert seconds == expected
        day = datetime(2020, 7, 12).date()
        midnight, upper = local_day_range(day, 'Asia/Manila')
        lower, _ = local_day_range(day - timedelta(days=1), 'Asia/Manila')
        params = {'start': midnight - timedelta(seconds=0.2),
            'end': midnight + timedelta(seconds=1.4), 'duration': 1}
        fragments = [db.execute(query, {**params, 'lower': a, 'upper': b}).scalar_one()
            for a, b in ((lower, midnight), (midnight, upper))]
        assert fragments == [0, 1] and sum(fragments) == params['duration']
    print('PASS: read-only PostgreSQL fractional reconciliation and 23/25-hour midnight/DST clipping', flush=True)


def verify(api_url):
    backend = dotenv_values(ROOT / 'backend/.env')
    frontend = dotenv_values(ROOT / 'frontend/.env.local')
    base, key = backend['SUPABASE_URL'].rstrip('/'), backend['SUPABASE_SECRET_KEY']
    public = frontend['NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY']
    users, clients = [], []
    phase = 'temporary authentication'
    with httpx.Client(timeout=45) as provider:
        try:
            assert httpx.get(api_url + '/health', timeout=10).json() == {'status': 'ok'}
            for route in ('/api/focus', '/api/analytics/summary', '/api/analytics/sessions'):
                assert httpx.get(api_url + route, timeout=10).status_code == 401
            for _ in range(2):
                email = f'study-hub-focus-verify-{uuid4().hex}@example.com'
                password = secrets.token_urlsafe(32)
                result = provider.post(base + '/auth/v1/admin/users', headers={'apikey': key},
                    json={'email': email, 'password': password, 'email_confirm': True})
                assert result.status_code in (200, 201)
                users.append(result.json()['id'])
                login = provider.post(base + '/auth/v1/token', params={'grant_type': 'password'},
                    headers={'apikey': public}, json={'email': email, 'password': password})
                assert login.status_code == 200
                clients.append(httpx.Client(base_url=api_url, timeout=45, headers={
                    'Authorization': 'Bearer ' + login.json()['access_token'], 'Origin': 'http://localhost:3001'}))
            a, b = clients
            with get_engine().begin() as db:
                db.execute(text("UPDATE public.profiles SET timezone='Asia/Manila' WHERE id = ANY(CAST(:owners AS uuid[]))"), {'owners': users})
            subjects = checked(a.get('/api/subjects'))
            far = next(s for s in subjects if s['code'] == 'FAR')
            mas = next(s for s in subjects if s['code'] == 'MAS')
            with get_engine().connect() as db:
                topic = str(db.execute(text('SELECT id FROM public.topics WHERE subject_id=:subject ORDER BY display_order,id LIMIT 1'), {'subject': far['id']}).scalar_one())
            phase = 'timer ownership, validation and concurrency'
            empty = checked(a.get('/api/focus'))
            assert empty['active_session'] is None and empty['today_seconds'] == 0
            assert checked(a.get('/api/analytics/summary'))['summary']['total_seconds'] == 0
            for payload in ({'duration_seconds': 20}, {'started_at': datetime.now(timezone.utc).isoformat()},
                            {'user_id': users[1]}, {'activity_type': 'invented'},
                            {'subject_id': mas['id'], 'topic_id': topic}):
                checked(a.post('/api/study-sessions', json=payload), 422)
            start_body = {'subject_id': far['id'], 'topic_id': topic, 'activity_type': 'practice'}
            # The existing database partial unique index must arbitrate parallel starts.
            with ThreadPoolExecutor(max_workers=2) as pool:
                responses = list(pool.map(lambda _: a.post('/api/study-sessions', json=start_body), range(2)))
            assert sorted(r.status_code for r in responses) == [201, 409]
            active = checked(next(r for r in responses if r.status_code == 201), 201)
            assert active['activity_type'] == 'practice' and active['duration_seconds'] is None
            restored = checked(a.get('/api/focus'))
            assert restored['active_session']['id'] == active['id'] and restored['server_now']
            assert checked(a.get('/api/focus'))['active_session']['id'] == active['id']
            assert checked(b.get('/api/focus'))['active_session'] is None
            checked(b.patch('/api/study-sessions/' + active['id'], json={'action': 'stop'}), 404)
            checked(a.patch('/api/study-sessions/' + active['id'], json={'action': 'stop', 'duration_seconds': 999}), 422)
            with get_engine().begin() as db:
                db.execute(text("UPDATE public.study_sessions SET started_at=clock_timestamp()-interval '75 seconds' WHERE id=:id AND user_id=:owner"), {'id': active['id'], 'owner': users[0]})
            stopped = checked(a.patch('/api/study-sessions/' + active['id'], json={'action': 'stop'}))
            seconds = int((datetime.fromisoformat(stopped['ended_at']) - datetime.fromisoformat(stopped['started_at'])).total_seconds())
            assert stopped['duration_seconds'] == seconds and seconds >= 75
            again = checked(a.patch('/api/study-sessions/' + active['id'], json={'action': 'stop'}))
            assert again['duration_seconds'] == seconds and again['ended_at'] == stopped['ended_at']
            assert checked(a.get('/api/focus'))['active_session'] is None
            print('PASS: start/restore, concurrent single-active rule, owner isolation, authoritative duration and retry-safe finish', flush=True)

            phase = 'exact analytics fixtures and planner comparison'
            zone = ZoneInfo('Asia/Manila')
            today = datetime.now(zone).replace(hour=0, minute=0, second=0, microsecond=0)
            yesterday = today - timedelta(days=1)
            fixtures = [
                (far['id'], topic, 'lecture', yesterday + timedelta(hours=9), 3600),
                (far['id'], topic, 'practice', yesterday - timedelta(minutes=30), 3600),
                (mas['id'], None, 'reading', yesterday + timedelta(hours=10), 1800),
                (None, None, 'recall', today, 120),
                (None, None, 'general', today - timedelta(days=100), 600),
            ]
            with get_engine().begin() as db:
                # Remove this verifier's prior synthetic finished session, never real history.
                db.execute(text('DELETE FROM public.study_sessions WHERE user_id=:owner'), {'owner': users[0]})
                for subject, topic_id, activity, start, duration in fixtures:
                    db.execute(text('INSERT INTO public.study_sessions(user_id,subject_id,topic_id,activity_type,started_at,ended_at,duration_seconds) '
                        'VALUES (:owner,:subject,:topic,:activity,:start,:end,:duration)'),
                        {'owner': users[0], 'subject': subject, 'topic': topic_id, 'activity': activity,
                         'start': start, 'end': start + timedelta(seconds=duration), 'duration': duration})
                db.execute(text("INSERT INTO public.study_sessions(user_id,activity_type,started_at,ended_at,duration_seconds) VALUES (:owner,'general',:start,:end,18000)"),
                    {'owner': users[1], 'start': yesterday + timedelta(hours=1), 'end': yesterday + timedelta(hours=6)})
            def event(title, subject, start, minutes, **extra):
                return checked(a.post('/api/study-events', json={
                    'title': title, 'subject_id': subject, 'start_at': start.isoformat(),
                    'end_at': (start + timedelta(minutes=minutes)).isoformat(), 'timezone': 'Asia/Manila', **extra}), 201)
            event('Synthetic planned FAR', far['id'], yesterday + timedelta(hours=9), 120)
            event('Synthetic cancelled plan', far['id'], yesterday + timedelta(hours=12), 60, status='cancelled')
            event('Synthetic skipped plan', mas['id'], today + timedelta(hours=9), 30, status='skipped')
            anchor = yesterday - timedelta(days=7) + timedelta(hours=15)
            day_codes = ('MO', 'TU', 'WE', 'TH', 'FR', 'SA', 'SU')
            recurring = event('Synthetic weekly plan', mas['id'], anchor, 60,
                recurrence_rule='FREQ=WEEKLY;BYDAY=' + day_codes[anchor.weekday()] + ';UNTIL=' + yesterday.strftime('%Y%m%d'))
            moved_start = yesterday - timedelta(days=1) + timedelta(hours=15)
            checked(a.patch('/api/study-events/' + recurring['id'] + '/occurrences/' + yesterday.date().isoformat(), json={
                'start_at': moved_start.isoformat(), 'end_at': (moved_start + timedelta(minutes=30)).isoformat()}))
            # An open session must not inflate completed study metrics.
            opened = checked(a.post('/api/study-sessions', json={'activity_type': 'quiz'}), 201)
            for period in (7, 30, 90):
                data = checked(a.get('/api/analytics/summary', params={'period': period}))
                metrics = data['summary']
                assert metrics['total_seconds'] == 9120 and metrics['session_count'] == 4
                assert metrics['active_days'] == 3 and metrics['longest_session_seconds'] == 3600
                assert metrics['average_session_seconds'] == 2280
                assert metrics['planned_seconds'] == (10800 if period == 7 else 14400)
                assert len(data['daily']) == period and sum(d['duration_seconds'] for d in data['daily']) == 9120
                subject_totals = {s['subject_code']: s for s in data['subjects']}
                assert subject_totals['FAR']['duration_seconds'] == 7200 and subject_totals['MAS']['duration_seconds'] == 1800
                assert subject_totals['FAR']['planned_seconds'] == 7200
                assert sum(s['duration_seconds'] for s in data['subjects']) == 9120
                activity = {s['activity_type']: s['duration_seconds'] for s in data['activities']}
                assert activity['lecture'] == 3600 and activity['practice'] == 3600 and activity['reading'] == 1800 and activity['recall'] == 120
                assert activity.get('quiz', 0) == 0
            custom = {'start_date': yesterday.date().isoformat(), 'end_date': yesterday.date().isoformat()}
            assert checked(a.get('/api/analytics/summary', params=custom))['summary']['total_seconds'] == 7200
            pages = [checked(a.get('/api/analytics/sessions', params={'period': 7, 'limit': 2, 'offset': offset})) for offset in (0, 2)]
            assert all(p['total'] == 4 for p in pages)
            assert len({s['id'] for p in pages for s in p['sessions']}) == 4
            assert all('activity_type' in s and 'subject_code' in s and 'topic_title' in s for p in pages for s in p['sessions'])
            own_focus = checked(a.get('/api/focus'))
            assert own_focus['today_seconds'] == 120 and own_focus['today_session_count'] == 1
            assert own_focus['active_session']['id'] == opened['id'] and len(own_focus['recent_sessions']) == 5
            assert checked(b.get('/api/analytics/summary'))['summary']['total_seconds'] == 18000
            for params in ({'period': 8}, {'start_date': yesterday.date().isoformat()},
                           {'start_date': today.date().isoformat(), 'end_date': yesterday.date().isoformat()},
                           {'start_date': (today - timedelta(days=90)).date().isoformat(), 'end_date': today.date().isoformat()},
                           {'start_date': today.date().isoformat(), 'end_date': (today + timedelta(days=1)).date().isoformat()},
                           {'limit': 101}, {'offset': -1}):
                checked(a.get('/api/analytics/sessions', params=params), 422)
            print('PASS: 7/30/90/custom ranges, midnight splits, exact subject/activity aggregates, recurrence edits and bounded history', flush=True)

            phase = 'database RLS and focus event association'
            with get_engine().begin() as db:
                assert db.execute(text("SELECT relrowsecurity FROM pg_class WHERE oid='public.study_sessions'::regclass")).scalar_one()
                for operation in ('INSERT', 'UPDATE', 'DELETE'):
                    assert not db.execute(text("SELECT has_table_privilege('authenticated','public.study_sessions',:operation)"), {'operation': operation}).scalar_one()
                db.execute(text('SET LOCAL ROLE authenticated'))
                db.execute(text("SELECT set_config('request.jwt.claim.sub',:owner,true)"), {'owner': users[1]})
                db.execute(text("SELECT set_config('request.jwt.claims',:claims,true)"), {'claims': '{"sub":"' + users[1] + '"}'})
                assert db.execute(text('SELECT count(*) FROM public.study_sessions WHERE user_id=:owner'), {'owner': users[0]}).scalar_one() == 0
                assert db.execute(text('SELECT count(*) FROM public.study_sessions WHERE user_id=:owner'), {'owner': users[1]}).scalar_one() == 1
            checked(a.patch('/api/study-sessions/' + opened['id'], json={'action': 'stop'}))
            linked = checked(a.post('/api/study-sessions', json={'study_event_id': recurring['id'],
                'occurrence_date': yesterday.date().isoformat(), 'activity_type': 'reading'}), 201)
            assert linked['subject_id'] == mas['id'] and linked['occurrence_id'] is not None
            checked(b.post('/api/study-sessions', json={'study_event_id': recurring['id']}), 404)
            checked(a.patch('/api/study-sessions/' + linked['id'], json={'action': 'stop'}))
            print('PASS: owner SELECT RLS, denied browser mutations and valid event/occurrence linkage', flush=True)
            phase = 'live SQL fractional clipping and DST boundaries'
            verify_sql_arithmetic()
        except Exception:
            print('Phase 11 verification failed during ' + phase + '; sensitive details withheld', flush=True)
            raise
        finally:
            cleaned = True
            for owner in users:
                try:
                    cleaned = provider.delete(base + '/auth/v1/admin/users/' + owner, headers={'apikey': key}).status_code in (200, 204) and cleaned
                except Exception:
                    cleaned = False
            for client in clients:
                client.close()
            if users and cleaned:
                try:
                    with get_engine().connect() as db:
                        assert db.execute(text('SELECT count(*) FROM auth.users WHERE id = ANY(CAST(:owners AS uuid[]))'), {'owners': users}).scalar_one() == 0
                        for table in ('study_sessions', 'study_events', 'study_event_occurrences'):
                            assert db.execute(text(f'SELECT count(*) FROM public.{table} WHERE user_id = ANY(CAST(:owners AS uuid[]))'), {'owners': users}).scalar_one() == 0
                except Exception:
                    cleaned = False
            print('Temporary Phase 11 account/data cleanup: ' + ('PASS' if cleaned else 'FAILED'), flush=True)
            assert cleaned


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', action='store_true')
    parser.add_argument('--sql-only', action='store_true', help='Read-only literal PostgreSQL duration checks; no users or records created')
    parser.add_argument('--api-url', default='http://localhost:8001')
    args = parser.parse_args()
    if not args.run and not args.sql_only:
        parser.error('Explicit --run is required to create temporary synthetic data')
    try:
        if args.sql_only:
            verify_sql_arithmetic()
        else:
            verify(args.api_url.rstrip('/'))
    except Exception:
        sys.exit(1)
