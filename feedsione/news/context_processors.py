from feedsione.news.models import Folder


def side_menu(request):
    folders = []
    if request.user.is_authenticated:
        folders = Folder.objects.filter(user=request.user).prefetch_related('feeds')

    return {'folders': folders}



