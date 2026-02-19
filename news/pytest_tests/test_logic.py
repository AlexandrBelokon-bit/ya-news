from http import HTTPStatus

import pytest
from django.urls import reverse

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


@pytest.mark.django_db
def test_anonymous_cannot_create_comment(client, news):
    url = reverse('news:detail', args=(news.id,))
    before = Comment.objects.count()

    resp = client.post(url, data={'text': 'Текст комментария'})
    assert resp.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == before


@pytest.mark.django_db
def test_authorized_can_create_comment(author_client, author, news):
    url = reverse('news:detail', args=(news.id,))
    before = Comment.objects.count()

    resp = author_client.post(
        url,
        data={'text': 'Текст комментария'},
    )
    assert resp.status_code == HTTPStatus.FOUND
    assert resp.url.endswith('#comments')
    assert Comment.objects.count() == before + 1

    comment = Comment.objects.latest('id')
    assert comment.text == 'Текст комментария'
    assert comment.author == author
    assert comment.news == news


@pytest.mark.django_db
def test_bad_words_not_allowed(author_client, news):
    url = reverse('news:detail', args=(news.id,))
    bad_text = (
        f'Какой-то текст, {BAD_WORDS[0]}, ещё текст'
    )

    resp = author_client.post(url, data={'text': bad_text})
    assert resp.status_code == HTTPStatus.OK

    form = resp.context['form']
    assert form.errors['text'][0] == WARNING
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_author_can_edit_comment(author_client, comment):
    url = reverse('news:edit', args=(comment.id,))
    resp = author_client.post(
        url,
        data={'text': 'Обновлённый комментарий'},
    )
    assert resp.status_code == HTTPStatus.FOUND
    assert resp.url.endswith('#comments')

    comment.refresh_from_db()
    assert comment.text == 'Обновлённый комментарий'


@pytest.mark.django_db
def test_author_can_delete_comment(author_client, comment):
    url = reverse('news:delete', args=(comment.id,))
    before = Comment.objects.count()

    resp = author_client.post(url)
    assert resp.status_code == HTTPStatus.FOUND
    assert resp.url.endswith('#comments')
    assert Comment.objects.count() == before - 1


@pytest.mark.django_db
def test_user_cannot_edit_foreign_comment(not_author_client, comment):
    url = reverse('news:edit', args=(comment.id,))
    resp = not_author_client.get(url)
    assert resp.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.django_db
def test_user_cannot_delete_foreign_comment(not_author_client, comment):
    url = reverse('news:delete', args=(comment.id,))
    resp = not_author_client.get(url)
    assert resp.status_code == HTTPStatus.NOT_FOUND
