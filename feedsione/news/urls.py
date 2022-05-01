from django.urls import path

from feedsione.news import views


app_name = 'news'
urlpatterns = [
    path(
        'dashboard/',
        views.ArticleListView.as_view(),
        name='dashboard'),   # list of all articles for now
    path(
        'article/<slug:slug>',
        views.ArticleDetailView.as_view(),
        name='article_detail'),

    path(
        'all_articles/',
        views.AllArticlesView.as_view(),
        name='all_articles'),
    path(
        'today/',
        views.TodayArticlesView.as_view(),
        name='today'),
    path(
        'readlater/',
        views.ReadLaterArticlesView.as_view(),
        name='readlater'),
    path(
        'feed/<slug:slug>',
        views.FeedArticlesView.as_view(),
        name='feed_articles'),

    path(
        'folder/<slug:slug>',
        views.FolderArticlesView.as_view(),
        name='folder_articles'),


    # list feeds
    path(
        'feeds/',
        views.FeedListView.as_view(),
        name='feeds')


    # DRAFTING
    # path('test/id/<uuid>', test_json, name='test_json'),
    # path('api/articles/', views.test_get_articles_json, )
    # path('article/id/<uuid>', article_detail_json, name='article_detail_json')
]


# from feedsione.users.views import (
#     user_detail_view,
#     user_redirect_view,
#     user_update_view,
# )

# app_name = "users"
# urlpatterns = [
#     path("~redirect/", view=user_redirect_view, name="redirect"),
#     path("~update/", view=user_update_view, name="update"),
#     path("<str:username>/", view=user_detail_view, name="detail"),
# ]
