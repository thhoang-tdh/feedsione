from django.urls import path

from feedsione.search import views

app_name = 'search'
urlpatterns = [
    # path(
    #     'dashboard/',
    #     views.ArticleListView.as_view(),
    #     name='dashboard'),   # list of all articles for now
    # path(
    #     'articles',
    #     views.aa),  # power search, search icon, search all articles

    path(
        'feeds/',
        views.SearchFeedResultsView.as_view(),
        name='search_feed'),
    path(
        'articles/subscription/',
        views.SearchArticleResultsView.as_view(),
        name='search_article'),

]


