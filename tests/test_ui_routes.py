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
