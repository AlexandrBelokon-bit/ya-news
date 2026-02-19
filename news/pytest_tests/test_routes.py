from http import HTTPStatus

import pytest
from django.conf import settings
from django.urls import reverse


@pytest.mark.django_db
def test_home_available_for_anonymous(client):
    url = reverse('news:home')
    resp = client.get(url)
    assert resp.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_detail_available_for_anonymous(client, news):
    url = reverse('news:detail', args=(news.id,))
    resp = client.get(url)
    assert resp.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_edit_delete_available_for_author(author_client, comment):
    for name in ('news:edit', 'news:delete'):
        url = reverse(name, args=(comment.id,))
        resp = author_client.get(url)
        assert resp.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_anonymous_redirected_from_edit_delete(client, comment):
    login_url = settings.LOGIN_URL
    for name in ('news:edit', 'news:delete'):
        url = reverse(name, args=(comment.id,))
        resp = client.get(url)
        assert resp.status_code == HTTPStatus.FOUND
        assert resp.url == (
            f'{login_url}?next={url}'
        )


@pytest.mark.django_db
def test_user_cannot_open_foreign_edit_delete(not_author_client, comment):
    for name in ('news:edit', 'news:delete'):
        url = reverse(name, args=(comment.id,))
        resp = not_author_client.get(url)
        assert resp.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name',
    ('users:login', 'users:signup', 'users:logout'),
)
def test_auth_pages_available_for_anonymous(client, name):
    url = reverse(name)
    resp = client.get(url)

    if resp.status_code == HTTPStatus.METHOD_NOT_ALLOWED:
        resp = client.post(url)

    assert resp.status_code in (HTTPStatus.OK, HTTPStatus.FOUND)
