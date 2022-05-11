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
        'read_later/',
        views.ReadLaterArticlesView.as_view(),
        name='articles_readlater'),
    # path(
    #     'feed/articles/<slug:slug>/',
    #     views.FeedArticlesView.as_view(),
    #     name='feed_articles'),
    # path(
    #     'folder/articles/<slug:slug>/',
    #     views.FolderArticlesView.as_view(),
    #     name='folder_articles'),
    path(
        'feed/<slug:slug>/articles/',
        views.FeedArticlesView.as_view(),
        name='feed_articles'),
    path(
        'folder/<slug:slug>/articles/',
        views.FolderArticlesView.as_view(),
        name='folder_articles'),


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

    path(
        'feed/follow/',
        views.follow_feed,
        name='follow_feed'),
    path(
        '/feed/unfollow/',
        views.unfollow_feed,
        name='unfollow_feed'),
]
