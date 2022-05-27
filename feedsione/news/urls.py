from django.urls import path

from feedsione.news import views


app_name = 'news'
urlpatterns = [
    path(
        'dashboard/',
        views.ArticleListView.as_view(),
        name='dashboard'),   # list of all articles for now, TODO: change this!!!

    #####################################
    #          List of articles
    #####################################
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
    path(
        'feed/<slug:slug>/articles/',
        views.FeedArticlesView.as_view(),
        name='feed_articles'),
    path(
        'folder/<slug:slug>/articles/',
        views.FolderArticlesView.as_view(),
        name='folder_articles'),

    # List feeds
    path(
        'feeds/',
        views.FeedListView.as_view(),
        name='feeds'),   # list feeds

    # Add new feed, folder
    path(
        'folder/create/',
        views.FolderCreateView.as_view(),
        name='folder_create'),
    path(
        'feed/create/',
        views.FeedCreateView.as_view(),
        name='feed_create'),

    # Follow and unfollow feed
    path(
        'feed/follow/',
        views.follow_feed,
        name='follow_feed'),
    path(
        'feed/unfollow/',
        views.unfollow_feed,
        name='unfollow_feed'),

    # Article detail
    path(
        'article/<slug:slug>',
        views.ArticleDetailView.as_view(),
        name='article_detail'),

    path(
        'article/mark-as-read/',
        views.mark_as_read,
        name='article_mark_as_read'),
    path(
        'article/read-later/',
        views.add_readlater,
        name='article_readlater'),
    path(
        'article/save/',
        views.save_article,
        name='article_save'),
]
