from django.contrib import admin
from django.urls import reverse
from django.template.defaultfilters import escape
from django.utils.safestring import mark_safe

from .models import Article, Feed, Topic, Source, UserArticle, Folder, FeedSubscription
import shortuuid

admin.site.register(Topic)
admin.site.register(Source)
admin.site.register(UserArticle)
admin.site.register(FeedSubscription)

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):

    @admin.display(
        description='Date Published'
    )
    def date_display(self, obj):
        return obj.date_published.strftime('%Y-%m-%d %H:%M:%S')

    @admin.display(description='Feed Link')
    @mark_safe
    def feed_link(self, obj):
        return '<a href="%s">%s</a>' % (reverse('admin:news_feed_change', args=(obj.feed.id,)) , escape(obj.feed))


    list_display = ('title', 'feed_link', 'date_display', )
    search_fields = ('title', 'feed__title')
    list_display_links = ('title', )
    list_filter = ('date_published', )


@admin.register(Feed)
class FeedAdmin(admin.ModelAdmin):
    list_display = ('feed_url', 'title', 'date_last_fetch', 'is_active', )
    search_fields = ('title', )
    list_editable = ('is_active', )
    list_display_links = ('feed_url', 'title', )
    list_filter = ('is_active', )


# admin.site.register(Folder)
@admin.register(Folder)
class FolderAdmin(admin.ModelAdmin):
    list_display = ('name', )
