from .utils import *


def test_return_health_check():
    response = client.get('/healthy')
    assert response.status_code == 200
    assert response.json() == {
        'status': 'Healthy'
    }