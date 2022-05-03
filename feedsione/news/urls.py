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
        'all/',
        views.AllArticlesView.as_view(),
        name='articles_all'),
    path(
        'today/',
        views.TodayArticlesView.as_view(),
        name='articles_today'),
    path(
        'readlater/',
        views.ReadLaterArticlesView.as_view(),
        name='articles_readlater'),
    path(
        'feed/<slug:slug>',
        views.FeedArticlesView.as_view(),
        name='articles_feed'),
    path(
        'folder/<slug:slug>',
        views.FolderArticlesView.as_view(),
        name='articles_folder'),


    # list feeds
    path(
        'feeds/',
        views.FeedListView.as_view(),
        name='feeds'),

    # add new
    path(
        'folder/create/',
        views.FolderCreateView.as_view(),
        name='folder_create'),
    path(
        'feed/create/',
        views.FeedCreateView.as_view(),
        name='feed_create'),

    # path(
    #     'feed/<slug:slug>/follow/',
    #     views.FeedFollowView.views(),
    #     name='feed_follow'),
]
