from django import forms

from feedsione.news.models import *
from feedsione.users.models import *

class FolderCreateForm(forms.ModelForm):
    class Meta:
        model = Folder
        fields = ['name', ]
        exclude = ('user', )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(FolderCreateForm, self).__init__(*args, **kwargs)

    def clean_name(self):
        name = self.cleaned_data['name']
        if Folder.objects.filter(user=self.user, name=name).exists():
            raise forms.ValidationError("You have aldready created a folder with same name.")
        return name


class FeedCreateForm(forms.ModelForm):
    class Meta:
        model = Feed
        fields = [
            'feed_url',
            'title',
            'frequency',
        ]

    def clean_frequency(self):
        frequency = self.cleaned_data['frequency']
        if frequency < 10:
            raise forms.ValidationError('Frequency has to be equal or greater than 10 minutes')
        return frequency

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(FeedCreateForm, self).__init__(*args, **kwargs)
        self.fields['folders'] = forms.ModelMultipleChoiceField(queryset=Folder.objects.filter(user=self.user), required=False, widget=forms.CheckboxSelectMultiple)
        # self.fields['folders'].error_message = {'required': 'Feed need to be added into at least one folder.'}

    def save(self, commit=True):
        feed = super(FeedCreateForm, self).save()
        folders = self.cleaned_data.get('folders')

        for folder in folders:
            FeedSubscription.objects.create(feed=feed, folder=folder)

        return feed


# class FollowFeedForm(forms.ModelForm):
#     class Meta:
#         model = FeedSubscription
#         fields = [
#             ''
#         ]
