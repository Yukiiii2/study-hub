"""Explicit Phase 10 API/RLS checks; only temporary synthetic accounts/data."""
import argparse
from datetime import datetime, timedelta, timezone
from pathlib import Path
import secrets
import sys
from uuid import uuid4

import httpx
from dotenv import dotenv_values
from sqlalchemy import text

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'backend'))
from app.db.connection import get_engine


def checked(response, expected=200):
    assert response.status_code == expected, 'Unexpected HTTP status'
    assert response.headers.get('access-control-allow-origin') == 'http://localhost:3001'
    return response.json() if expected != 204 else None


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
            assert httpx.get(api_url + '/api/assessments', timeout=10).status_code == 401
            for _ in range(2):
                email = f'study-hub-assessment-verify-{uuid4().hex}@example.com'
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
            subjects = checked(a.get('/api/subjects'))
            far = next(s for s in subjects if s['code'] == 'FAR')
            with get_engine().connect() as db:
                topic_id = str(db.execute(text('SELECT t.id FROM public.topics t JOIN public.videos v ON v.topic_id=t.id '
                                              'WHERE t.subject_id=:subject ORDER BY t.display_order,t.id LIMIT 1'),
                                         {'subject': far['id']}).scalar_one())
            videos = checked(a.get('/api/topics/' + topic_id + '/videos'))
            now = datetime.now(timezone.utc)
            phase = 'assessment CRUD and coverage'
            item = checked(a.post('/api/assessments', json={'title': 'Synthetic assessment',
                'topic_ids': [topic_id], 'scheduled_at': (now + timedelta(days=1)).isoformat()}), 201)
            route = '/api/assessments/' + item['id']
            assert item['topic_count'] == 1 and item['topic_ids'] == [topic_id]
            assert len(item['coverage_subjects']) == 1
            empty = checked(a.post('/api/assessments', json={'title': 'Synthetic empty definition'}), 201)
            assert checked(a.get('/api/assessments/' + empty['id']))['readiness']['video_completion_percentage'] is None
            assert checked(a.get('/api/assessments/' + empty['id']))['readiness']['quiz_accuracy_percentage'] is None
            checked(a.post('/api/assessments', json={'title': 'Invalid overlap', 'topic_ids': [topic_id], 'subject_ids': [far['id']]}), 422)
            checked(a.post('/api/assessments', json={'title': 'Invalid curriculum', 'topic_ids': [str(uuid4())]}), 422)
            checked(a.post('/api/assessments', json={'title': 'Invalid owner', 'user_id': users[1]}), 422)
            for method in ('get','delete'):
                checked(getattr(b, method)(route), 404)
            checked(b.patch(route, json={'title': 'Unauthorized'}), 404)
            checked(b.get(route + '/attempts'), 404)
            checked(b.post(route + '/attempts', json={}), 404)
            item = checked(a.patch(route, json={'title': 'Synthetic edited assessment', 'description': 'Synthetic description'}))
            assert item['topic_ids'] == [topic_id]
            checked(a.patch(route, json={'subject_ids': [far['id']]}), 422)
            whole = checked(a.patch('/api/assessments/' + empty['id'], json={'subject_ids': [far['id']]}))
            assert whole['topic_count'] == len(checked(a.get('/api/subjects/' + far['id'] + '/topics')))
            print('PASS: assessment CRUD, exact/whole-subject coverage, invalid overlap and ownership', flush=True)

            phase = 'manual attempt validation and persistence'
            attempt = checked(a.post(route + '/attempts', json={}), 201)
            attempt_route = '/api/assessment-attempts/' + attempt['id']
            assert attempt['percentage'] is None and attempt['score'] is None
            checked(b.patch(attempt_route, json={'notes': 'Unauthorized'}), 404)
            for payload in ({'score': 1}, {'score': 2, 'max_score': 0}, {'score': 4, 'max_score': 3},
                            {'score': -1, 'max_score': 3}, {'score': 1, 'max_score': 3},
                            {'percentage': 100}, {'user_id': users[1]},
                            {'started_at': now.isoformat(), 'completed_at': (now - timedelta(hours=1)).isoformat()}):
                checked(a.patch(attempt_route, json=payload), 422)
            recorded = checked(a.patch(attempt_route, json={'started_at': (now - timedelta(hours=1)).isoformat(),
                'completed_at': now.isoformat(), 'score': 1, 'max_score': 3, 'notes': 'Synthetic result'}))
            assert abs(recorded['percentage'] - 33.3333) < 0.00001
            assert checked(a.get(route + '/attempts'))['attempts'][0]['id'] == attempt['id']
            corrected = checked(a.patch(attempt_route, json={'score': 2}))
            assert abs(corrected['percentage'] - 66.6667) < 0.00001
            print('PASS: nullable results, server-derived percentages, partial correction and attempt history', flush=True)

            phase = 'readiness from real canonical progress'
            checked(a.patch('/api/videos/' + videos[0]['id'] + '/progress', json={'status': 'completed'}))
            card = checked(a.post('/api/flashcards', json={'front': 'Synthetic recall', 'back': 'Synthetic answer',
                'subject_id': far['id'], 'topic_id': topic_id}), 201)
            checked(a.post('/api/flashcards/' + card['id'] + '/review', json={'rating': 'good',
                'expected_revision': 0, 'request_id': str(uuid4())}))
            overdue = checked(a.post('/api/flashcards', json={'front': 'Synthetic overdue', 'back': 'Synthetic answer',
                'subject_id': far['id'], 'topic_id': topic_id}), 201)
            with get_engine().begin() as db:
                db.execute(text('UPDATE public.flashcards SET next_review_at=:due WHERE user_id=:owner AND id=:id'),
                           {'due': now - timedelta(days=2), 'owner': users[0], 'id': overdue['id']})
            questions = []
            for index in range(2):
                questions.append(checked(a.post('/api/questions', json={'question_type': 'single_select',
                    'prompt': 'Synthetic readiness ' + str(index), 'options': [{'key': 'A', 'text': 'Correct'}, {'key': 'B', 'text': 'Wrong'}],
                    'correct_keys': ['A'], 'subject_id': far['id'], 'topic_id': topic_id}), 201))
            quiz = checked(a.post('/api/quizzes', json={'title': 'Synthetic coverage quiz', 'question_ids': [q['id'] for q in questions]}), 201)
            quiz_attempt = checked(a.post('/api/quizzes/' + quiz['id'] + '/attempts'))
            checked(a.post('/api/quiz-attempts/' + quiz_attempt['id'] + '/answers', json={'question_id': questions[0]['id'], 'selected_keys': ['A']}))
            checked(a.post('/api/quiz-attempts/' + quiz_attempt['id'] + '/complete'))
            # Mutating today's author definition must not alter historical snapshot coverage.
            changed_question = {field: questions[0][field] for field in ('subject_id','topic_id','resource_id','source_page','question_type','prompt','explanation','options','correct_keys')}
            changed_question.update(subject_id=None, topic_id=None)
            checked(a.patch('/api/questions/' + questions[0]['id'], json=changed_question))
            readiness = checked(a.get(route))['readiness']
            assert readiness['total_videos'] == len(videos) and readiness['completed_videos'] == 1
            assert abs(readiness['video_completion_percentage'] - 100 / len(videos)) < 0.001
            assert readiness['quiz_graded_answers'] == 2 and readiness['quiz_correct_answers'] == 1
            assert readiness['quiz_accuracy_percentage'] == 50
            assert readiness['active_flashcards'] == 2 and readiness['reviewed_flashcards'] == 1
            assert readiness['due_flashcards'] == 1 and readiness['overdue_flashcards'] == 1
            foreign = checked(b.post('/api/assessments', json={'title': 'Synthetic isolated readiness', 'topic_ids': [topic_id]}), 201)
            isolated = checked(b.get('/api/assessments/' + foreign['id']))['readiness']
            assert isolated['completed_videos'] == isolated['quiz_graded_answers'] == isolated['active_flashcards'] == 0
            print('PASS: owner-specific video/quiz/recall components, immutable quiz coverage and empty denominators', flush=True)

            phase = 'RLS grants and non-destructive archive'
            with get_engine().begin() as db:
                for table in ('assessments','assessment_topics','assessment_subjects','assessment_attempts'):
                    assert db.execute(text('SELECT relrowsecurity FROM pg_class WHERE oid=CAST(:name AS regclass)'), {'name': 'public.' + table}).scalar_one()
                    for operation in ('INSERT','UPDATE','DELETE'):
                        assert not db.execute(text("SELECT has_table_privilege('authenticated',:name,:operation)"), {'name': 'public.' + table, 'operation': operation}).scalar_one()
                db.execute(text('SET LOCAL ROLE authenticated'))
                db.execute(text("SELECT set_config('request.jwt.claim.sub',:owner,true)"), {'owner': users[1]})
                db.execute(text("SELECT set_config('request.jwt.claims',:claims,true)"), {'claims': '{"sub":"' + users[1] + '"}'})
                for table in ('assessments','assessment_topics','assessment_subjects','assessment_attempts'):
                    assert db.execute(text(f'SELECT count(*) FROM public.{table} WHERE user_id=:owner'), {'owner': users[0]}).scalar_one() == 0
            checked(a.delete(route), 204)
            assert checked(a.get(route))['status'] == 'archived'
            assert checked(a.get(route + '/attempts'))['total'] == 1
            checked(a.post(route + '/attempts', json={}), 409)
            checked(a.patch(attempt_route, json={'notes': 'Archived definition'}), 409)
            assert item['id'] not in [i['id'] for i in checked(a.get('/api/assessments'))['assessments']]
            print('PASS: owner RLS, denied browser mutations and archive preserving coverage/results', flush=True)
        except Exception:
            print('Assessment verification failed during ' + phase + '; sensitive details withheld', flush=True)
            raise
        finally:
            cleaned = True
            for owner in users:
                try: cleaned = provider.delete(base + '/auth/v1/admin/users/' + owner, headers={'apikey': key}).status_code in (200,204) and cleaned
                except Exception: cleaned = False
            for client in clients: client.close()
            if users and cleaned:
                try:
                    with get_engine().connect() as db:
                        assert db.execute(text('SELECT count(*) FROM auth.users WHERE id = ANY(CAST(:owners AS uuid[]))'), {'owners': users}).scalar_one() == 0
                        for table in ('assessments','assessment_topics','assessment_subjects','assessment_attempts','flashcards','flashcard_reviews','questions','quizzes','quiz_attempts','user_video_progress'):
                            assert db.execute(text(f'SELECT count(*) FROM public.{table} WHERE user_id = ANY(CAST(:owners AS uuid[]))'), {'owners': users}).scalar_one() == 0
                except Exception: cleaned = False
            print('Temporary Phase 10 account/data cleanup: ' + ('PASS' if cleaned else 'FAILED'), flush=True)
            assert cleaned


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', action='store_true')
    parser.add_argument('--api-url', default='http://localhost:8001')
    args = parser.parse_args()
    if not args.run: parser.error('Explicit --run is required to create temporary synthetic data')
    try: verify(args.api_url.rstrip('/'))
    except Exception: sys.exit(1)
