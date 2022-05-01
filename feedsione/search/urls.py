from django.urls import path

# from feedsione.news.views import ArticleDetailView, ArticleListView

app_name = 'search'
urlpatterns = [
    # path('article/<slug:slug>', ArticleDetailView.as_view(), name='article_detail'),
    # path('dashboard/', ArticleListView.as_view(), name='article_list')
    # path('feeds/')
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
