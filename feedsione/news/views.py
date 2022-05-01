from django.shortcuts import render

from feedsione.news.models import *
from django.views.generic import ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render

from datetime import timedelta
from django.utils import timezone
from itertools import chain


class ArticleDetailView(DetailView):
    model = Article
    template_name = 'news/article_detail.html'


class ArticleListView(LoginRequiredMixin, ListView):
    model = Article
    template_name = 'news/article_list.html'
    context_object_name = 'articles'
    paginate_by = 50
    ordering = ['-date_published']

    def get_context_data(self, *arg, **kwargs):
        context = super(ArticleListView, self).get_context_data(*arg, **kwargs)
        context['folders'] = Folder.objects.filter(user=self.request.user)
        return context


class AllArticlesView(ArticleListView):
    def get_queryset(self):
        pass
        qs = super().get_queryset()
        articles = qs.filter(
            feed__in=Feed.objects.filter(users=self.request.user).
                                    distinct())
        return articles


class TodayArticlesView(AllArticlesView):
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(date_published__gt=timezone.now()-timedelta(hours=24))


class ReadLaterArticlesView(ArticleListView):
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(userarticle__user=self.request.user,
                        userarticle__is_read_later=True)


class FeedArticlesView(ArticleListView):
    def get_queryset(self):
        qs = super().get_queryset()
        slug = self.kwargs['slug']
        feed = get_object_or_404(Feed, slug=slug)
        articles = qs.filter(feed=feed)
        return articles


class FolderArticlesView(ArticleListView):
    def get_queryset(self):
        qs = super().get_queryset()
        # folder =???
        articles = qs.filter
        return qs.filter(date_published__gt=timezone.now()-timedelta(hours=5))


class FeedListView(ListView):
    model = Feed
    template_name = 'news/feed_list.html'
    context_object_name = 'feeds'
    ordering = ['title']

















































# def test_get_articles_json(request):

#     articles = Article.objects.all()
#     serializer = ArticleSerializer(articles, many=True)
#     return JsonResponse({'articles': serializer.data})



# def article_detail_json(request, uuid):
#     # article = get_object_or_404(Article, uuid=uuid)

#     # article = serializers.serialize('json', article)

#     # if request.headers.get('x-requested-with') == 'XMLHttpRequest':
#     #     return JsonResponse(context)
#     # else:
#     #     return render(request, 'news/article_detail.html', context)



#     return JsonResponse({'test': 'test msg', 'name': 'test msg name'}, safe=False)




# def test_json(request, uuid):
#     return JsonResponse({'test': 'test msg', 'name': 'test msg name'}, safe=False)
