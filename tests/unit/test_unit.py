from api import create_app


def test_home_page(client):
    response = client.get('/')
    assert response.status_code == 200 and b'Messaging System - REST API!' in response.data
