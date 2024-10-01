import pytest
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_kitten_list():
    client = APIClient()
    response = client.get('/api/cats/')
    assert response.status_code == 200
