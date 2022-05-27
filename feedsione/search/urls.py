from django.urls import path

from feedsione.search import views

app_name = 'search'
urlpatterns = [
    path(
        'feeds/',
        views.SearchFeedResultsView.as_view(),
        name='search_feeds'),
    path(
        'articles/subscription/',
        views.SearchArticleResultsView.as_view(),
        name='search_articles'),


]


