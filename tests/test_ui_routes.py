"""
ProjectFlow Comprehensive UI & Route Integration Tests
Verifies 100% error-free navigation, valid HTTP 200 responses,
template rendering without Jinja errors, and proper Kanban card delivery.
"""


def test_public_routes(client):
    """Test landing and favicon public accessibility."""
    res = client.get('/', follow_redirects=True)
    assert res.status_code == 200

    res_fav = client.get('/favicon.ico')
    assert res_fav.status_code == 200
    assert 'image/svg+xml' in res_fav.content_type


def test_authenticated_core_routes(client, auth_user, test_project, test_issue):
    """Test standard developer pages with valid session."""
    with client.session_transaction() as sess:
        sess['user_id'] = auth_user.id
        sess['role'] = auth_user.role
        sess['username'] = auth_user.username
        sess['_fresh'] = True

    routes = [
        '/dashboard',
        '/board',
        '/backlog',
        '/issues',
        '/timeline',
        '/calendar',
        '/reports',
        '/analytics',
        '/service-desk',
        '/automation',
        '/search',
        '/settings',
        '/profile',
        '/change-calendar',
        f'/project/{test_project.id}/board',
        f'/project/{test_project.id}/kanban',
        f'/project/{test_project.id}/backlog',
        f'/project/{test_project.id}/issues',
        f'/project/{test_project.id}/timeline',
        f'/project/{test_project.id}/reports',
        f'/project/{test_project.id}/settings',
        f'/project/{test_project.id}/issue/{test_issue.id}',
    ]

    for route in routes:
        res = client.get(route, follow_redirects=True)
        assert res.status_code == 200, f"Route {route} failed with status {res.status_code}"


def test_admin_routes(client, admin_user, test_project):
    """Test administration routes for authorized admin user."""
    with client.session_transaction() as sess:
        sess['user_id'] = admin_user.id
        sess['role'] = admin_user.role
        sess['username'] = admin_user.username
        sess['_fresh'] = True

    admin_routes = [
        '/admin/',
        '/admin/projects',
        '/admin/users',
        '/admin/teams',
        '/admin/tools',
        '/admin/analytics',
        '/admin/automation',
        '/admin/security',
        '/admin/database',
        '/admin/settings',
        '/admin/backup',
    ]

    for route in admin_routes:
        res = client.get(route, follow_redirects=True)
        assert res.status_code == 200, f"Admin route {route} failed with status {res.status_code}"


def test_board_issue_rendering(client, auth_user, test_project, test_issue):
    """Verify that issues are properly rendered inside the kanban board."""
    with client.session_transaction() as sess:
        sess['user_id'] = auth_user.id
        sess['role'] = auth_user.role
        sess['username'] = auth_user.username
        sess['_fresh'] = True

    res = client.get(f'/project/{test_project.id}/kanban')
    assert res.status_code == 200
    html = res.data.decode('utf-8')
    assert test_issue.key in html
    assert test_issue.title in html


def test_direct_issue_routes(client, auth_user, test_project, test_issue):
    """Verify that direct /issue/<id> and /issue/<key> redirect to issue view."""
    with client.session_transaction() as sess:
        sess['user_id'] = auth_user.id
        sess['role'] = auth_user.role
        sess['username'] = auth_user.username
        sess['_fresh'] = True

    # By ID
    res1 = client.get(f'/issue/{test_issue.id}', follow_redirects=True)
    assert res1.status_code == 200
    assert test_issue.title in res1.data.decode('utf-8')

    res2 = client.get(f'/issues/{test_issue.id}', follow_redirects=True)
    assert res2.status_code == 200

    # By Key (e.g. PF-1)
    res3 = client.get(f'/issue/{test_issue.key}', follow_redirects=True)
    assert res3.status_code == 200

    res4 = client.get(f'/issues/{test_issue.key.lower()}', follow_redirects=True)
    assert res4.status_code == 200


def test_user_profile_route(client, auth_user, admin_user):
    """Verify that /profile/<user_id> loads the user's profile view."""
    with client.session_transaction() as sess:
        sess['user_id'] = auth_user.id
        sess['role'] = auth_user.role
        sess['username'] = auth_user.username
        sess['_fresh'] = True

    res = client.get(f'/profile/{admin_user.id}', follow_redirects=True)
    assert res.status_code == 200
    assert admin_user.username in res.data.decode('utf-8')
