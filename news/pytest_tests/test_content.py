from datetime import datetime, timedelta
from http import HTTPStatus

import pytest
from django.conf import settings
from django.urls import reverse

from news.models import News, Comment


@pytest.mark.django_db
def test_news_count_on_home_page(client):
    for i in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1):
        News.objects.create(title=f'Новость {i}', text='Текст')

    url = reverse('news:home')
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK

    news_feed = response.context['news_feed']
    assert len(news_feed) == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_sorted_from_newest_to_oldest(client):
    today = datetime.today().date()

    for i in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1):
        News.objects.create(
            title=f'Новость {i}',
            text='Текст',
            date=today - timedelta(days=i),
        )

    url = reverse('news:home')
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK

    news_feed = response.context['news_feed']
    dates = [n.date for n in news_feed]
    assert dates == sorted(dates, reverse=True)


@pytest.mark.django_db
def test_comments_sorted_old_to_new(client, author, news):
    Comment.objects.create(news=news, author=author, text='Старый')
    Comment.objects.create(news=news, author=author, text='Новый')

    url = reverse('news:detail', args=(news.id,))
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK

    obj = response.context['object']
    comments = list(obj.comment_set.all())
    created_list = [c.created for c in comments]

    assert created_list == sorted(created_list)


@pytest.mark.django_db
def test_anonymous_has_no_comment_form_on_detail(client, news):
    url = reverse('news:detail', args=(news.id,))
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK
    assert 'form' not in response.context


@pytest.mark.django_db
def test_authorized_has_comment_form_on_detail(author_client, news):
    url = reverse('news:detail', args=(news.id,))
    response = author_client.get(url)
    assert response.status_code == HTTPStatus.OK
    assert 'form' in response.context
