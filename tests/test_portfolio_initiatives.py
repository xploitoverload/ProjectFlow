import pytest
from datetime import date, datetime
from models import db, User, Project, Team, Issue, Initiative


@pytest.fixture
def test_setup(app):
    """Setup test users, teams, projects, and issues."""
    with app.app_context():
        # Ensure clean state
        Initiative.query.delete()
        Issue.query.delete()
        Project.query.delete()
        Team.query.delete()
        User.query.delete()
        db.session.commit()

        user = User(username='portfolio_admin', password='password123', role='admin', email='portfolio_admin@example.com')
        db.session.add(user)
        db.session.commit()

        team = Team(name='Core Engineering')
        db.session.add(team)
        db.session.commit()

        proj1 = Project(name='Cloud Infrastructure', key='INF', status='active', team_id=team.id, lead_id=user.id)
        proj2 = Project(name='Data Analytics Engine', key='DAT', status='active', team_id=team.id, lead_id=user.id)
        db.session.add_all([proj1, proj2])
        db.session.commit()

        # Add issues to calculate progress
        # proj1: 1 done, 1 in_progress -> 50%
        i1 = Issue(project_id=proj1.id, key='INF-1', title='Deploy K8s Cluster', status='done', reporter_id=user.id)
        i2 = Issue(project_id=proj1.id, key='INF-2', title='Setup Service Mesh', status='in_progress', reporter_id=user.id)
        # proj2: 2 done -> 100%
        i3 = Issue(project_id=proj2.id, key='DAT-1', title='Setup ClickHouse', status='done', reporter_id=user.id)
        i4 = Issue(project_id=proj2.id, key='DAT-2', title='Stream Processing', status='done', reporter_id=user.id)
        db.session.add_all([i1, i2, i3, i4])
        db.session.commit()

        yield {
            'user': user,
            'team': team,
            'proj1': proj1,
            'proj2': proj2
        }


def test_initiative_model_and_aggregated_progress(app, test_setup):
    """Test Initiative model creation, project linking, and progress computation."""
    with app.app_context():
        user = User.query.filter_by(username='portfolio_admin').first()
        proj1 = Project.query.filter_by(key='INF').first()
        proj2 = Project.query.filter_by(key='DAT').first()

        init = Initiative(
            title='Next-Gen Scalable Architecture',
            description='Upgrade infrastructure and stream processing pipeline',
            status='active',
            target_quarter='2026-Q4',
            start_date=date(2026, 10, 1),
            target_date=date(2026, 12, 31),
            owner_id=user.id
        )
        init.projects = [proj1, proj2]
        db.session.add(init)
        db.session.commit()

        fetched = Initiative.query.filter_by(title='Next-Gen Scalable Architecture').first()
        assert fetched is not None
        assert fetched.target_quarter == '2026-Q4'
        assert len(fetched.projects) == 2

        # proj1 is 50%, proj2 is 100% -> expected aggregate = (50 + 100) / 2 = 75%
        assert proj1.progress == 50
        assert proj2.progress == 100
        assert fetched.progress == 75

        d = fetched.to_dict()
        assert d['title'] == 'Next-Gen Scalable Architecture'
        assert d['progress'] == 75
        assert d['project_count'] == 2


def test_initiative_api_lifecycle(client, test_setup):
    """Test REST API CRUD lifecycle for initiatives."""
    with client.session_transaction() as sess:
        sess['user_id'] = test_setup['user'].id

    # 1. Create Initiative
    res = client.post('/api/v1/initiatives', json={
        'title': 'Global Cloud Expansion',
        'description': 'Deploy across 3 new cloud regions',
        'status': 'planned',
        'target_quarter': '2027-Q1',
        'start_date': '2027-01-01',
        'target_date': '2027-03-31',
        'project_ids': [test_setup['proj1'].id]
    })
    assert res.status_code == 201
    data = res.get_json()
    assert data['success'] is True
    init_id = data['initiative']['id']
    assert data['initiative']['title'] == 'Global Cloud Expansion'
    assert data['initiative']['project_count'] == 1

    # 2. Get Initiative Details
    res_get = client.get(f'/api/v1/initiatives/{init_id}')
    assert res_get.status_code == 200
    assert res_get.get_json()['initiative']['target_quarter'] == '2027-Q1'

    # 3. Link Another Project
    res_link = client.post(f'/api/v1/initiatives/{init_id}/projects', json={
        'project_id': test_setup['proj2'].id
    })
    assert res_link.status_code == 200
    assert res_link.get_json()['initiative']['project_count'] == 2

    # 4. Update Initiative
    res_up = client.put(f'/api/v1/initiatives/{init_id}', json={
        'status': 'active',
        'target_quarter': '2027-Q2'
    })
    assert res_up.status_code == 200
    assert res_up.get_json()['initiative']['status'] == 'active'
    assert res_up.get_json()['initiative']['target_quarter'] == '2027-Q2'

    # 5. List Initiatives
    res_list = client.get('/api/v1/initiatives')
    assert res_list.status_code == 200
    assert len(res_list.get_json()['initiatives']) >= 1

    # 6. Unlink Project
    res_unlink = client.delete(f'/api/v1/initiatives/{init_id}/projects/{test_setup["proj2"].id}')
    assert res_unlink.status_code == 200
    assert res_unlink.get_json()['initiative']['project_count'] == 1

    # 7. Delete Initiative
    res_del = client.delete(f'/api/v1/initiatives/{init_id}')
    assert res_del.status_code == 200
    assert res_del.get_json()['success'] is True


def test_portfolio_roadmap_data_api(client, test_setup):
    """Test /api/v1/portfolio/roadmap_data cross-project aggregation."""
    with client.session_transaction() as sess:
        sess['user_id'] = test_setup['user'].id

    res = client.get('/api/v1/portfolio/roadmap_data')
    assert res.status_code == 200
    data = res.get_json()
    assert data['success'] is True
    assert 'projects' in data
    assert 'initiatives' in data
    assert 'milestones' in data
    assert len(data['projects']) == 2


def test_portfolio_web_route(client, test_setup):
    """Test /portfolio template view returns 200 OK."""
    with client.session_transaction() as sess:
        sess['user_id'] = test_setup['user'].id

    res = client.get('/portfolio')
    assert res.status_code == 200
    assert b'Portfolio &amp; Strategic Initiatives' in res.data or b'Strategic Portfolio' in res.data
    assert b'Multi-Project Roadmap' in res.data
