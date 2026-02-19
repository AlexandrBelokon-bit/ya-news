from django.urls import path

from news import views

app_name = 'news'

urlpatterns = [
    path('', views.NewsList.as_view(), name='home'),
    path(
        'delete_comment/<int:pk>/',
        views.CommentDelete.as_view(),
        name='delete'
    ),
    path('news/<int:pk>/', views.NewsDetailView.as_view(), name='detail'),
    path('edit_comment/<int:pk>/', views.CommentUpdate.as_view(), name='edit'),
]
