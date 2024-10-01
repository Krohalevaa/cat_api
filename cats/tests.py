import pytest

from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

from .models import Cat, Breed

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    return User.objects.create_user(username='testuser', password='testpass')


@pytest.fixture
def auth_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def breed(db):
    return Breed.objects.create(name='Siamese')


@pytest.fixture
def cat(db, user, breed):
    return Cat.objects.create(
        name='Fluffy',
        color='White',
        age=12,
        owner=user,
        description='A fluffy cat',
        breed=breed
    )


def test_get_breeds(api_client):
    # Проверяем, что получение списка пород работает
    response = api_client.get('/api/breeds/')
    assert response.status_code == status.HTTP_200_OK


def test_get_cats(api_client):
    # Проверяем, что получение списка котят работает
    response = api_client.get('/api/cats/')
    assert response.status_code == status.HTTP_200_OK


def test_create_cat(auth_client, breed):
    # Проверяем, что котенок может быть создан
    data = {
        'name': 'Mittens',
        'color': 'Black',
        'age': 6,
        'description': 'A cute black cat',
        'breed': breed.id,
    }
    response = auth_client.post('/api/cats/', data)
    assert response.status_code == status.HTTP_201_CREATED
    assert Cat.objects.count() == 1


def test_update_cat(auth_client, cat):
    # Проверяем, что котенок может быть обновлен
    data = {
        'name': 'Mittens',
        'color': 'Black',
        'age': 7,
        'description': 'An updated description',
        'breed': cat.breed.id,
    }
    response = auth_client.put(f'/api/cats/{cat.id}/', data)
    assert response.status_code == status.HTTP_200_OK
    cat.refresh_from_db()
    assert cat.age == 7
    assert cat.description == 'An updated description'


def test_delete_cat(auth_client, cat):
    # Проверяем, что котенок может быть удален
    response = auth_client.delete(f'/api/cats/{cat.id}/')
    assert response.status_code == status.HTTP_204_NO_CONTENT
    assert Cat.objects.count() == 0


def test_cat_creation_without_auth(api_client, breed):
    # Проверяем, что котенок не может быть создан без авторизации
    data = {
        'name': 'Mittens',
        'color': 'Black',
        'age': 6,
        'description': 'A cute black cat',
        'breed': breed.id,
    }
    response = api_client.post('/api/cats/', data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


def test_get_cat_detail(api_client, cat):
    # Проверяем, что получение подробной информации о котенке работает
    response = api_client.get(f'/api/cats/{cat.id}/')
    assert response.status_code == status.HTTP_200_OK
    assert response.data['name'] == cat.name


def test_rating_cat(auth_client, cat):
    # Проверяем возможность добавления рейтинга котенка
    response = auth_client.post(
        '/api/ratings/', {'kitten': cat.id, 'score': 5})
    assert response.status_code == status.HTTP_201_CREATED
