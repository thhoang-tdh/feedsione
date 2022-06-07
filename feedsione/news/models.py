from distutils.command.upload import upload
from time import mktime
from unittest.mock import Base
from django.db import models
from datetime import datetime, timezone
from django.utils import timezone as tz
import feedparser
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.template.defaultfilters import slugify, truncatewords_html
from django.urls import reverse
from urllib.parse import urlparse
from django.core.exceptions import ValidationError
import requests
from shortuuid.django_fields import ShortUUIDField
import shortuuid
from django.conf import settings
from feedsione.news.utils import unique_slug_generator

def one_week_hence():
    return timezone.now() + timezone.timedelta(days=7)

def fifteen_hence():
    return timezone.now() + timezone.timedelta(minutes=15)


class BaseModel(models.Model):
    date_created = models.DateTimeField(
        verbose_name=_('date created'),
        auto_now_add=True)
    date_modified = models.DateTimeField(
        verbose_name=_('date of last modified'),
        auto_now=True)

    class Meta:
        abstract = True


class Topic(BaseModel):
    """
    Topic, search keyword, tag, filter,...
    """
    name = models.CharField(
        verbose_name=_('name'),
        max_length=50,
        unique=True)

    class Meta:
        verbose_name = _('Topic')
        verbose_name_plural = _('Topics')
        ordering = ('name',)

    def __str__(self):
        return self.name


class Source(BaseModel):
    """
    Source, group, or website domain of multiple RSS feeds
    """
    site_url = models.URLField(
        verbose_name=_('source site url'),
        max_length=50,
        unique=True)
    # TODO: add source name
    logo_url = models.URLField(
        verbose_name=_('logo url'),
        null=True,
        blank=True)

    def __str__(self):
        return self.site_url

    class Meta:
        verbose_name = 'Source'
        verbose_name_plural = 'Sources'


class Folder(BaseModel):
    """
    User defined folder, buddle or collection of feeds
    """
    name = models.CharField(
        verbose_name=_('folder name'),
        max_length=50,
        blank=False, null=False)
    is_public = models.BooleanField(verbose_name=_('is public'), default=False)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE)

    slug = models.SlugField(max_length=255,
                            unique=True,
                            blank=True,
                            editable=False)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('news:folder_articles', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = unique_slug_generator(self, self.name)
            # self.slug = slugify(shortuuid.ShortUUID().random(length=12) + ' ' + self.name)
        super(Folder, self).save(*args, **kwargs)

    class Meta:
        verbose_name = 'Folder'
        verbose_name_plural = 'Folders'
        ordering = ['name']
        unique_together = ('name', 'user',)


class Feed(BaseModel):
    feed_url = models.URLField(
        verbose_name=_('feed URL'),
        unique=True,
        max_length=255,)
    title = models.CharField(
        verbose_name=_('title'),
        max_length=200,
        blank=True)
    site_url = models.URLField(
        verbose_name=_('site URL'),
        blank=True,
        null=True)

    is_active = models.BooleanField(verbose_name=_('is active'), default=True)
    frequency = models.IntegerField(verbose_name=_('frequency'), default=10)
    date_last_fetch = models.DateTimeField(verbose_name=_('date of last fetch'), auto_now=True)

    source = models.ForeignKey(
        Source,
        blank=True, null=True,
        on_delete=models.CASCADE)
    topics = models.ManyToManyField(Topic, blank=True)
    folders = models.ManyToManyField(
        Folder,
        through='FeedSubscription',
        related_name='feeds',
        blank=True)

    slug = models.SlugField(max_length=255,
                            unique=True,
                            blank=True,
                            editable=False)

    class Meta:
        verbose_name = _('Feed')
        verbose_name_plural = _('Feeds')
        ordering = ('title', )

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('news:feed_articles', kwargs={'slug': self.slug})

    def clean(self):
        parsed_data = feedparser.parse(self.feed_url)
        if not parsed_data or parsed_data.bozo:
            raise ValidationError({'feed_url': 'Invalid RSS feed url'})
        else:
            self.parsed_rss_url = parsed_data

    def save(self, *args, **kwargs):
        if self.parsed_rss_url:
            data = self.parsed_rss_url
        else:
            data = feedparser.parse(self.feed_url)

        if data.feed.title:
            self.title = data.feed.title
        else:
            self.title = 'Undefined'

        if data.feed.link:
            self.site_url = data.feed.link

            # get or create source
            netloc = urlparse(data.feed.link).netloc

            if not self.source and netloc and len(netloc) > 0:
                try:
                    source = Source.objects.get(site_url=netloc)
                except:
                    source = Source.objects.create(site_url=netloc)
                self.source = source

        if not self.id:
            self.slug = unique_slug_generator(self, self.title)

        super(Feed, self).save(*args, **kwargs)

    def download_feed_articles(self):
        """ Download articles from current feed."""
        try:
            # r = requests.get(self.feed_url)
            # data = feedparser.parse(r.content)
            data = feedparser.parse(self.feed_url)
            for entry in data.entries:
                try:
                    article = Article.objects.get(link=entry.link)
                    continue
                except:
                    article = Article()

                article.feed = self
                article.description = entry.description
                article.truncated_description = truncatewords_html(entry.description, 50)
                article.link = entry.link
                article.title = entry.title

                try:
                    date_published = entry.published_parsed
                except:
                    try:
                        date_published = entry.created_parsed
                    except:
                        date_published = entry.updated_parsed

                article.date_published = datetime.fromtimestamp(mktime(date_published), timezone.utc)
                article.save()

            self.date_last_fetch =  tz.now()
            self.save()
        except Exception as e:
            pass


class FeedSubscription(BaseModel):
# class FeedSubscription(models.Model):

    """
    Folder - Feed
    """
    feed = models.ForeignKey(
        Feed,
        on_delete=models.CASCADE)
    folder = models.ForeignKey(
        Folder,
        on_delete=models.CASCADE)

    class Meta:
        unique_together = [['feed', 'folder']]

    def __str__(self):
        return self.folder.name + ' - ' + self.feed.title


class Article(BaseModel):
    title = models.CharField(verbose_name=_('article title'), max_length=255)
    description = models.TextField(verbose_name=_('description'))
    truncated_description = models.TextField(
        verbose_name=_('truncated description'),
        blank=True, null=True)
    link = models.URLField(
        verbose_name=_('article link'),
        unique=True,
        max_length=2048) # link to original article
    date_published = models.DateTimeField(verbose_name=_('date published'))

    feed = models.ForeignKey(
        Feed,
        on_delete=models.CASCADE)
    # topics = models.ManyToManyField(Topic, blank=True)
    users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='UserArticle',
        related_name='articles',
        blank=True)

    slug = models.SlugField(max_length=255,
                            unique=True,
                            blank=True,
                            editable=False)


    class Meta:
        verbose_name = 'Article'
        verbose_name_plural = 'Articles'
        ordering = ['-date_published']
        get_latest_by = ['id']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('news:article_detail', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.id:
            self.slug = unique_slug_generator(self, self.title)

        super(Article, self).save(*args, **kwargs)


class UserArticle(BaseModel):
    """
    Read Later articles
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE)
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE)

    is_saved = models.BooleanField(verbose_name=_('is saved'), default=False)
    is_read_later = models.BooleanField(verbose_name=_('read later'), default=False)
    is_read = models.BooleanField(verbose_name=_('read'), default=False)

    def __str__(self):
        return self.user.username + ' - ' + self.article.title

    class Meta:
        unique_together = ('user', 'article')



