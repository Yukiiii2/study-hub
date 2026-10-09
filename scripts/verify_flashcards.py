"""Explicit Phase 9 checks using only temporary synthetic accounts/cards/files."""
import argparse
from concurrent.futures import ThreadPoolExecutor
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
from verify_resources import pdf_bytes


def checked(response, expected=200):
    assert response.status_code == expected, 'Unexpected HTTP status'
    assert response.headers.get('access-control-allow-origin') == 'http://localhost:3001'
    return response.json() if expected != 204 else None


def verify(api_url):
    backend = dotenv_values(ROOT / 'backend/.env')
    frontend = dotenv_values(ROOT / 'frontend/.env.local')
    base = backend['SUPABASE_URL'].rstrip('/')
    key = backend['SUPABASE_SECRET_KEY']
    public = frontend['NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY']
    users, clients, resources = [], [], []
    phase = 'temporary authentication'
    with httpx.Client(timeout=45) as provider:
        try:
            assert httpx.get(api_url + '/health', timeout=10).json() == {'status': 'ok'}
            assert httpx.get(api_url + '/api/flashcards/due', timeout=10).status_code == 401
            for _ in range(2):
                email = f'study-hub-recall-verify-{uuid4().hex}@example.com'
                password = secrets.token_urlsafe(32)
                made = provider.post(base + '/auth/v1/admin/users', headers={'apikey': key},
                                     json={'email': email, 'password': password, 'email_confirm': True})
                assert made.status_code in (200, 201)
                users.append(made.json()['id'])
                login = provider.post(base + '/auth/v1/token', params={'grant_type': 'password'}, headers={'apikey': public},
                                      json={'email': email, 'password': password})
                assert login.status_code == 200
                clients.append(httpx.Client(base_url=api_url, timeout=45, headers={
                    'Authorization': 'Bearer ' + login.json()['access_token'], 'Origin': 'http://localhost:3001'}))
            a, b = clients
            checked(a.get('/api/auth/me'))
            subjects = checked(a.get('/api/subjects'))
            far = next(s for s in subjects if s['code'] == 'FAR')
            afar = next(s for s in subjects if s['code'] == 'AFAR')
            topic = checked(a.get(f"/api/subjects/{far['id']}/topics"))[0]
            foreign_topic = checked(a.get(f"/api/subjects/{afar['id']}/topics"))[0]
            source = checked(a.post('/api/resources/upload', files={'file': ('synthetic-recall.pdf', pdf_bytes(), 'application/pdf')}), 201)
            resources.append((a, source['id']))
            foreign_source = checked(b.post('/api/resources/upload', files={'file': ('synthetic-foreign.pdf', pdf_bytes(), 'application/pdf')}), 201)
            resources.append((b, foreign_source['id']))
            phase = 'deck/card CRUD and associations'
            assert checked(a.get('/api/flashcards'))['total'] == 0
            deck = checked(a.post('/api/flashcard-decks', json={'title': 'Synthetic FAR deck', 'subject_id': far['id']}), 201)
            route = '/api/flashcard-decks/' + deck['id']
            checked(b.get(route), 404)
            checked(b.patch(route, json={'title': 'Unauthorized'}), 404)
            checked(b.delete(route), 404)
            deck = checked(a.patch(route, json={'title': 'Synthetic edited deck'}))
            payload = {'deck_id': deck['id'], 'subject_id': far['id'], 'topic_id': topic['id'],
                       'resource_id': source['id'], 'source_page': 1, 'front': 'Synthetic prompt', 'back': 'Synthetic answer'}
            card = checked(a.post('/api/flashcards', json=payload), 201)
            assert card['review_revision'] == 0 and card['interval_days'] == 0
            card_route = '/api/flashcards/' + card['id']
            checked(a.post('/api/flashcards', json={**payload, 'user_id': users[1]}), 422)
            checked(a.post('/api/flashcards', json={**payload, 'topic_id': foreign_topic['id']}), 422)
            checked(a.post('/api/flashcards', json={**payload, 'resource_id': foreign_source['id']}), 422)
            checked(a.post('/api/flashcards', json={**payload, 'subject_id': afar['id'], 'topic_id': foreign_topic['id']}), 422)
            checked(a.post('/api/flashcards', json={**payload, 'source_page': 200}), 422)
            checked(a.patch(card_route, json={'next_review_at': datetime.now(timezone.utc).isoformat()}), 422)
            checked(a.patch(route, json={'subject_id': afar['id']}), 409)
            for suffix in ('', '/reviews'):
                checked(b.get(card_route + suffix), 404)
            checked(b.patch(card_route, json={'front': 'Unauthorized'}), 404)
            checked(b.delete(card_route), 404)
            checked(b.post(card_route + '/review', json={'rating': 'good', 'expected_revision': 0, 'request_id': str(uuid4())}), 404)
            before_due = card['next_review_at']
            card = checked(a.patch(card_route, json={'front': 'Synthetic edited front', 'notes': 'Synthetic note'}))
            assert card['review_revision'] == 1 and card['next_review_at'] == before_due
            print('PASS: owner-scoped deck/card CRUD, source/page/topic/deck validation and server-only state', flush=True)

            phase = 'due queue and dashboard counts'
            queue_cards = []
            for label in ('overdue', 'today', 'future', 'suspended'):
                item = checked(a.post('/api/flashcards', json={'front': 'Synthetic ' + label, 'back': 'Synthetic back'}), 201)
                queue_cards.append(item)
            now = datetime.now(timezone.utc)
            with get_engine().begin() as db:
                # These are only cards created under this invocation's temporary user.
                for item, delta in zip(queue_cards, (timedelta(days=-2), timedelta(minutes=-1), timedelta(days=2), timedelta(days=-2))):
                    db.execute(text('UPDATE public.flashcards SET next_review_at=:due WHERE user_id=:owner AND id=:id'),
                               {'due': now + delta, 'owner': users[0], 'id': item['id']})
            checked(a.patch('/api/flashcards/' + queue_cards[3]['id'], json={'status': 'suspended'}))
            queue = checked(a.get('/api/flashcards/due'))
            due_ids = [item['id'] for item in queue['cards']]
            assert due_ids[0] == queue_cards[0]['id'] and queue_cards[2]['id'] not in due_ids and queue_cards[3]['id'] not in due_ids
            assert queue['summary']['overdue'] == 1 and queue['summary']['due_today'] == 2 and queue['summary']['upcoming'] == 1
            future = checked(a.get('/api/flashcards/due', params={'mode': 'upcoming'}))
            assert [item['id'] for item in future['cards']] == [queue_cards[2]['id']]
            filtered = checked(a.get('/api/flashcards/due', params={'deck_id': deck['id']}))
            assert filtered['total'] == 1
            dashboard = checked(a.get('/api/dashboard'))
            assert dashboard['recall_summary'] == {key: queue['summary'][key] for key in ('overdue', 'due_today')}
            checked(a.post('/api/flashcards/' + queue_cards[2]['id'] + '/review', json={'rating': 'good', 'expected_revision': 0, 'request_id': str(uuid4())}), 409)
            assert checked(b.get('/api/flashcards/due'))['total'] == 0
            print('PASS: overdue-first due queue, future/suspended exclusion, filters and real dashboard summary', flush=True)

            phase = 'ratings, history, snapshot and duplicate protection'
            for rating, interval in (('again', 0), ('hard', 1), ('good', 1), ('easy', 4)):
                item = checked(a.post('/api/flashcards', json={'front': 'Synthetic rating ' + rating, 'back': 'Synthetic answer'}), 201)
                review = checked(a.post('/api/flashcards/' + item['id'] + '/review', json={
                    'rating': rating, 'expected_revision': 0, 'request_id': str(uuid4())}))
                assert review['next_interval_days'] == interval and review['previous_interval_days'] == 0
                elapsed = (datetime.fromisoformat(review['next_review_at']) - datetime.fromisoformat(review['reviewed_at'])).total_seconds()
                assert elapsed == (600 if rating == 'again' else interval * 86400)
            request = {'rating': 'good', 'expected_revision': card['review_revision'], 'request_id': str(uuid4())}
            review = checked(a.post(card_route + '/review', json=request))
            assert review['next_interval_days'] == 1 and review['front_snapshot'] == card['front']
            assert checked(a.post(card_route + '/review', json=request)) == review
            checked(a.post(card_route + '/review', json={**request, 'rating': 'easy'}), 409)
            checked(a.post(card_route + '/review', json={**request, 'request_id': str(uuid4())}), 409)
            checked(a.post(card_route + '/review', json={**request, 'expected_revision': card['review_revision'] + 1, 'request_id': str(uuid4())}), 409)
            card = checked(a.get(card_route))
            assert card['next_review_at'] == review['next_review_at'] and card['review_revision'] == request['expected_revision'] + 1
            for rating, expected in (('good', 3), ('hard', 4), ('easy', 14), ('again', 0)):
                with get_engine().begin() as db:
                    db.execute(text('UPDATE public.flashcards SET next_review_at=:due WHERE user_id=:owner AND id=:id'),
                               {'due': datetime.now(timezone.utc) - timedelta(seconds=1), 'owner': users[0], 'id': card['id']})
                review = checked(a.post(card_route + '/review', json={'rating': rating, 'expected_revision': card['review_revision'], 'request_id': str(uuid4())}))
                assert review['next_interval_days'] == expected
                card = checked(a.get(card_route))
            history = checked(a.get(card_route + '/reviews'))
            assert history['total'] == 5
            checked(a.patch(card_route, json={'back': 'Synthetic changed answer'}))
            assert checked(a.get(card_route + '/reviews')) == history
            print('PASS: four ratings, progression, exact retry, stale/early denial and immutable review history', flush=True)

            phase = 'concurrent review submissions'
            concurrent = checked(a.post('/api/flashcards', json={'front': 'Synthetic concurrent', 'back': 'Synthetic back'}), 201)
            concurrent_route = '/api/flashcards/' + concurrent['id'] + '/review'
            same = {'rating': 'good', 'expected_revision': 0, 'request_id': str(uuid4())}
            with ThreadPoolExecutor(max_workers=2) as pool:
                results = list(pool.map(lambda _: a.post(concurrent_route, json=same), range(2)))
            assert checked(results[0]) == checked(results[1])
            assert checked(a.get('/api/flashcards/' + concurrent['id'] + '/reviews'))['total'] == 1
            concurrent2 = checked(a.post('/api/flashcards', json={'front': 'Synthetic concurrent2', 'back': 'Synthetic back'}), 201)
            different = [{'rating': 'good', 'expected_revision': 0, 'request_id': str(uuid4())} for _ in range(2)]
            with ThreadPoolExecutor(max_workers=2) as pool:
                results = list(pool.map(lambda body: a.post('/api/flashcards/' + concurrent2['id'] + '/review', json=body), different))
            assert sorted(r.status_code for r in results) == [200, 409]
            assert checked(a.get('/api/flashcards/' + concurrent2['id'] + '/reviews'))['total'] == 1
            print('PASS: same-request concurrency is idempotent; differing rapid submissions grade once', flush=True)

            phase = 'explicit quiz mistake conversion'
            question = checked(a.post('/api/questions', json={'question_type': 'single_select', 'prompt': 'Synthetic missed quiz question',
                'options': [{'key': 'A', 'text': 'Synthetic correct text'}, {'key': 'B', 'text': 'Synthetic wrong text'}],
                'correct_keys': ['A'], 'explanation': 'Synthetic explanation', 'subject_id': far['id'], 'topic_id': topic['id']}), 201)
            quiz = checked(a.post('/api/quizzes', json={'title': 'Synthetic mistake quiz', 'question_ids': [question['id']]}), 201)
            attempt = checked(a.post('/api/quizzes/' + quiz['id'] + '/attempts'))
            total = checked(a.get('/api/flashcards'))['total']
            result = checked(a.post('/api/quiz-attempts/' + attempt['id'] + '/complete'))
            assert checked(a.get('/api/flashcards'))['total'] == total
            missed = result['questions'][0]
            assert missed['is_correct'] is False
            answer = '\n'.join(o['text'] for o in missed['options'] if o['key'] in missed['correct_keys']) + '\n\n' + missed['explanation']
            created = checked(a.post('/api/flashcards', json={'front': missed['prompt'], 'back': answer,
                'subject_id': missed['subject_id'], 'topic_id': missed['topic_id']}), 201)
            assert created['front'] == missed['prompt'] and created['back'] == answer
            print('PASS: quiz result creates no cards automatically; explicit edited mistake mapping creates a card', flush=True)

            phase = 'RLS grants, archive/delete and source detachment'
            with get_engine().begin() as db:
                for table in ('flashcard_decks', 'flashcards', 'flashcard_reviews'):
                    assert db.execute(text('SELECT relrowsecurity FROM pg_class WHERE oid=CAST(:name AS regclass)'), {'name': 'public.' + table}).scalar_one()
                    for operation in ('INSERT', 'UPDATE', 'DELETE'):
                        assert not db.execute(text("SELECT has_table_privilege('authenticated', :name, :operation)"), {'name': 'public.' + table, 'operation': operation}).scalar_one()
                db.execute(text('SET LOCAL ROLE authenticated'))
                db.execute(text("SELECT set_config('request.jwt.claim.sub', :owner, true)"), {'owner': users[1]})
                db.execute(text("SELECT set_config('request.jwt.claims', :claims, true)"), {'claims': '{"sub":"' + users[1] + '"}'})
                for table in ('flashcard_decks', 'flashcards', 'flashcard_reviews'):
                    assert db.execute(text(f'SELECT count(*) FROM public.{table} WHERE user_id=:owner'), {'owner': users[0]}).scalar_one() == 0
            checked(a.delete(route), 204)
            detached = checked(a.get(card_route))
            assert detached['deck_id'] is None and detached['next_review_at'] == card['next_review_at']
            checked(a.delete('/api/resources/' + source['id']), 204)
            resources.remove((a, source['id']))
            detached = checked(a.get(card_route))
            assert detached['resource_id'] is None and detached['source_page'] is None
            checked(a.delete(card_route), 204)
            assert checked(a.get(card_route))['status'] == 'archived'
            assert checked(a.get(card_route + '/reviews'))['total'] == 5
            assert card['id'] not in [item['id'] for item in checked(a.get('/api/flashcards/due'))['cards']]
            print('PASS: owner RLS, denied browser mutations, deck/source detachment and archive retaining history', flush=True)
        except Exception:
            print('Flashcard verification failed during ' + phase + '; sensitive details withheld', flush=True)
            raise
        finally:
            cleaned = True
            for client, resource_id in resources:
                try: cleaned = client.delete('/api/resources/' + resource_id).status_code == 204 and cleaned
                except Exception: cleaned = False
            for user_id in users if cleaned else []:
                try: cleaned = provider.delete(base + '/auth/v1/admin/users/' + user_id, headers={'apikey': key}).status_code in (200, 204) and cleaned
                except Exception: cleaned = False
            for client in clients: client.close()
            if cleaned and users:
                try:
                    with get_engine().connect() as db:
                        assert db.execute(text('SELECT count(*) FROM auth.users WHERE id = ANY(CAST(:owners AS uuid[]))'), {'owners': users}).scalar_one() == 0
                        for table in ('flashcard_decks', 'flashcards', 'flashcard_reviews', 'questions', 'question_options', 'quizzes', 'quiz_questions', 'quiz_attempts', 'quiz_answers', 'resources', 'document_sections'):
                            assert db.execute(text(f'SELECT count(*) FROM public.{table} WHERE user_id = ANY(CAST(:owners AS uuid[]))'), {'owners': users}).scalar_one() == 0
                except Exception: cleaned = False
            print('Synthetic flashcard/quiz/resource/account cleanup: ' + ('PASS' if cleaned else 'FAILED'), flush=True)
            assert cleaned


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', action='store_true')
    parser.add_argument('--api-url', default='http://localhost:8001')
    args = parser.parse_args()
    if not args.run: parser.error('Explicit --run is required to create temporary synthetic data')
    try: verify(args.api_url.rstrip('/'))
    except Exception: sys.exit(1)
