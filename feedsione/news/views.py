from dataclasses import fields
import enum
import json
from django.shortcuts import render, redirect

from feedsione.news.models import *
from feedsione.news.forms import *
from django.views.generic import ListView, DetailView, CreateView
from django.views.generic.edit import UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy

from datetime import timedelta
from django.utils import timezone
from itertools import chain
from django.http import HttpResponseRedirect, JsonResponse, HttpResponseBadRequest, Http404
from django.contrib.auth.decorators import login_required
from django.db.models import F

from django_celery_beat.models import PeriodicTask, IntervalSchedule
import json



def home(request):
    return redirect('account_login')


class ArticleDetailView(DetailView):
    model = Article
    template_name = 'news/article_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:
            ua = UserArticle.objects.get(user=self.request.user,
                                         article=context['article'])
        except:
            ua = None

        context['ua'] = ua

        return context



class ArticleListType(enum.Enum):
    DEFAULT = 0
    TODAY = 1
    READ_LATER = 2
    SAVED = 3
    ALL = 4
    FOLDER = 5
    FEED = 6


class ArticleListView(LoginRequiredMixin, ListView):

    model = Article
    template_name = 'news/article_list.html'
    context_object_name = 'articles'
    paginate_by = 50

    def get_queryset(self):
        qs = super().get_queryset()
        is_unread = self.request.GET.get('unread')

        qs = qs.prefetch_related(
            models.Prefetch('userarticle_set',
                            queryset=UserArticle.objects.filter(user=self.request.user),
                            to_attr='ua_records')
            )

        if is_unread is not None:
            if is_unread == '0': # return all articles (includes read and unread)
                return qs
        return qs.exclude(userarticle__user=self.request.user, userarticle__is_read=True)


    def get_context_data(self, *arg, **kwargs):
        context = super(ArticleListView, self).get_context_data(*arg, **kwargs)
        context['page_header'] = 'Articles'
        context['list_type'] = ArticleListType.DEFAULT
        context['alt'] = ArticleListType(0)
        context['from_single_feed'] = False
        return context

    def get_ordering(self):
        self.ordering = '-date_published'

        ordering = self.request.GET.get('o')
        if ordering is not None:
            field_names = [a.name for a in Article._meta.fields]
            ordering_opts = tuple(set(ordering.split(',')) & set(field_names))
            if ordering_opts:
                self.ordering = ordering_opts

        return self.ordering


    def post(self, *args, **kwargs):
        markread_form = MarkReadForm(self.request.POST or None)
        if markread_form.is_valid():
            day = markread_form.cleaned_data.get('day')
            articles = self.get_queryset()
            if day > 0:
                articles = articles.filter(date_published__lt=timezone.now()-timedelta(days=day))
            for article in articles:
                UserArticle.objects.update_or_create(user=self.request.user,
                                                        article=article,
                                                        is_read=True)
            return HttpResponseRedirect(self.request.path_info + '?unread=1')
        return HttpResponseRedirect(self.request.path_info)


class AllArticlesView(ArticleListView):
    def get_queryset(self):
        qs = super().get_queryset()
        subscripted_feeds = Feed.objects.filter(folders__user=self.request.user).distinct()
        qs = qs.filter(feed__in=subscripted_feeds)

        return qs

    def get_context_data(self, *arg, **kwargs):
        context = super(AllArticlesView, self).get_context_data(*arg, **kwargs)
        context['page_header'] = 'All articles'
        context['list_type'] = ArticleListType.ALL
        return context


class TodayArticlesView(AllArticlesView):
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(date_published__gt=timezone.now()-timedelta(hours=24))

        return qs

    def get_context_data(self, *arg, **kwargs):
        context = super(TodayArticlesView, self).get_context_data(*arg, **kwargs)
        context['page_header'] = 'Today'
        context['list_type'] = ArticleListType.TODAY
        return context

class ReadLaterArticlesView(ArticleListView):
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(userarticle__user=self.request.user,
                       userarticle__is_read_later=True)

        return qs

    def get_context_data(self, *arg, **kwargs):
        context = super(ReadLaterArticlesView, self).get_context_data(*arg, **kwargs)
        context['page_header'] = 'Read later'
        context['list_type'] = ArticleListType.READ_LATER
        return context

class SavedArticlesView(ArticleListView):
    def get_queryset(self):
        qs = super().get_queryset()
        qs = qs.filter(userarticle__user=self.request.user,
                       userarticle__is_saved=True)
        return qs

    def get_context_data(self, *arg, **kwargs):
        context = super(SavedArticlesView, self).get_context_data(*arg, **kwargs)
        context['page_header'] = 'Saved'
        context['list_type'] = ArticleListType.SAVED
        return context


class FeedArticlesView(ArticleListView):
    def get_queryset(self):
        qs = super().get_queryset()
        slug = self.kwargs['slug']
        self.feed = get_object_or_404(Feed, slug=slug)
        qs = qs.filter(feed=self.feed)

        return qs

    def get_context_data(self, *arg, **kwargs):
        context = super(FeedArticlesView, self).get_context_data(*arg, **kwargs)
        context['page_header'] = self.feed.title
        context['from_single_feed'] = True
        context['feed'] = self.feed
        context['followed_in_folders'] = self.feed.folders.filter(user=self.request.user)

        context['list_type'] = ArticleListType.FEED
        return context


class FolderArticlesView(ArticleListView):
    def get_queryset(self):
        qs = super().get_queryset()
        slug = self.kwargs['slug']
        self.folder = get_object_or_404(Folder, slug=slug, user=self.request.user)
        qs = qs.filter(feed__in=self.folder.feeds.all())

        return qs

    def get_context_data(self, *arg, **kwargs):
        context = super(FolderArticlesView, self).get_context_data(*arg, **kwargs)
        context['page_header'] = self.folder.name
        context['list_type'] = ArticleListType.FOLDER
        context['folder'] = self.folder

        return context


class FeedListView(ListView):
    model = Feed
    template_name = 'news/feed_list.html'
    context_object_name = 'feeds'
    ordering = ['title']


class FolderCreateView(LoginRequiredMixin, CreateView):
    # model = Folder
    template_name = 'news/create_folder.html'
    form_class = FolderCreateForm

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.user = self.request.user
        self.object.save()
        return HttpResponseRedirect(self.object.get_absolute_url())

    def get_initial(self, *args, **kwargs):
        initial = super(FolderCreateView, self).get_initial(**kwargs)
        # initial['name'] = 'My folder'
        return initial

    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super(FolderCreateView, self).get_form_kwargs(*args, **kwargs)
        kwargs['user'] = self.request.user
        return kwargs


class FolderUpdateView(LoginRequiredMixin, UpdateView):
    model = Folder
    form_class = FolderCreateForm
    template_name = 'news/folder_update.html'

    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super(FolderUpdateView, self).get_form_kwargs(*args, **kwargs)
        kwargs['user'] = self.request.user
        return kwargs


class FolderDeleteView(LoginRequiredMixin, DeleteView):
    model = Folder
    success_url = reverse_lazy('news:articles_today')

    def get_queryset(self):
        qs = super(FolderDeleteView, self).get_queryset()
        return qs.filter(user=self.request.user)



class FeedCreateView(LoginRequiredMixin, CreateView):
    template_name = 'news/create_feed.html'
    form_class = FeedCreateForm

    def form_valid(self, form):
        feed = form.save()
        feed.download_feed_articles()

        # create period task
        schedule, created = IntervalSchedule.objects.get_or_create(
            every=feed.frequency*5,
            period=IntervalSchedule.MINUTES
        )

        PeriodicTask.objects.create(
            interval=schedule,
            name="Fetch " + feed.title,
            task="feedsione.news.tasks.get_articles",
            kwargs=json.dumps({'feed_id': feed.id})
        )

        return HttpResponseRedirect(feed.get_absolute_url())

    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super(FeedCreateView, self).get_form_kwargs(*args, **kwargs)
        kwargs['user'] = self.request.user
        return kwargs


class FolderManageView(LoginRequiredMixin, ListView):
    model = Feed
    template_name = 'news/folder_manage_feeds.html'
    context_object_name = 'feeds'

    def get_queryset(self):
        self.folder = get_object_or_404(Folder, slug=self.kwargs['slug'], user=self.request.user)

        try:
            feeds = Feed.objects.filter(folders__in=[self.folder])
        except:
            raise Http404("User does not exist")

        return feeds

    def get_context_data(self, *arg, **kwargs):
        context = super(FolderManageView, self).get_context_data(*arg, **kwargs)
        context['folders'] = Folder.objects.filter(user=self.request.user)
        context['current_folder'] = self.folder
        return context




@login_required
def follow_feed(request):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    if is_ajax:
        if request.method == 'POST':
            data = request.POST
            user = request.user
            feed = get_object_or_404(Feed, slug=data['feed_slug'])
            folder = Folder.objects.filter(user=user,
                                           slug=data['folder_slug']).first()

            if feed is None or folder is None:
                return JsonResponse({'msg': 'Invalid request 1'}, status=400)

            obj, created = FeedSubscription.objects.update_or_create(feed=feed,
                                                                     folder=folder)
            return JsonResponse({'msg': 'OK!'})

        return JsonResponse({'msg': 'Invalid request 3'}, status=400)
    else:
        return HttpResponseBadRequest('Invalid request 4')


@login_required
def unfollow_feed(request):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    if is_ajax:
        if request.method == 'POST':
            data = request.POST
            user = request.user
            feed = get_object_or_404(Feed, slug=data['feed_slug'])
            folder = Folder.objects.filter(user=user,
                                           slug=data['folder_slug']).first()

            if feed is None or folder is None:
                return JsonResponse({'msg': 'Invalid request 1'}, status=400)

            fs = FeedSubscription.objects.filter(feed=feed, folder=folder).first()
            if fs is not None:
                fs.delete()

            return JsonResponse({'msg': 'OK!'})

        return JsonResponse({'msg': 'Invalid request 1'}, status=400)
    else:
        return HttpResponseBadRequest('Invalid request 2')


@login_required
def mark_as_read(request):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    if is_ajax:
        if request.method == 'POST':
            form = MarkAsReadArticleForm(request.POST)
            if form.is_valid():
                article = Article.objects.get(slug=form.cleaned_data.get('article_slug'))

                try:
                    ua = UserArticle.objects.get(user=request.user, article=article)
                    ua.is_read = form.cleaned_data.get('is_read')
                except UserArticle.DoesNotExist:
                    ua = UserArticle.objects.create(user=request.user,
                                                    article=article,
                                                    is_read=form.cleaned_data.get('is_read'))
                ua.save()
                return JsonResponse({'msg': 'OK'})

            return JsonResponse({'msg': 'Invalid form', 'data': str(form.cleaned_data)}, status=400)

        return JsonResponse({'msg': 'Invalid request'}, status=400)
    else:
        return HttpResponseBadRequest('Invalid request')


@login_required
def add_readlater(request):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    if is_ajax:
        if request.method == 'POST':
            form = ReadLaterArticleForm(request.POST)
            if form.is_valid():
                article = Article.objects.get(slug=form.cleaned_data.get('article_slug'))

                try:
                    ua = UserArticle.objects.get(user=request.user, article=article)
                    ua.is_read_later = form.cleaned_data.get('is_read_later')
                except UserArticle.DoesNotExist:
                    ua = UserArticle.objects.create(user=request.user,
                                                    article=article,
                                                    is_read_later=form.cleaned_data.get('is_read_later'))
                ua.save()

                return JsonResponse({'msg': 'OK'})
            return JsonResponse({'msg': 'Invalid form', 'data': str(form.cleaned_data)}, status=400)

        return JsonResponse({'msg': 'Invalid request'}, status=400)
    else:
        return HttpResponseBadRequest('Invalid request')



@login_required
def save_article(request):
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    if is_ajax:
        if request.method == 'POST':
            form = SaveArticleForm(request.POST)
            if form.is_valid():
                article = Article.objects.get(slug=form.cleaned_data.get('article_slug'))

                try:
                    ua = UserArticle.objects.get(user=request.user, article=article)
                    ua.is_saved = form.cleaned_data.get('is_saved')
                except UserArticle.DoesNotExist:
                    ua = UserArticle.objects.create(user=request.user,
                                                    article=article,
                                                    is_saved=form.cleaned_data.get('is_saved'))
                ua.save()

                return JsonResponse({'msg': 'OK'})
            return JsonResponse({'msg': 'Invalid form', 'data': str(form.cleaned_data)}, status=400)

        return JsonResponse({'msg': 'Invalid request'}, status=400)
    else:
        return HttpResponseBadRequest('Invalid request')
