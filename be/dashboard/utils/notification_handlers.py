from dashboard.models import Notification


def make_notification_seen(notification_pk):
    """
    This function simply just make a notification seen and returns its link
    """
    selected_notification = Notification.objects.get(pk=notification_pk)
    selected_notification.seen = True
    selected_notification.save()

    return selected_notification.link


def get_notification_of_user(request):
    page_notification = Notification.objects.filter(target=request.user)
    if 'filter' in request.GET:
        request_filter = request.GET.get('filter')
        if request_filter == 'unseen':
            page_notification = page_notification.filter(seen=False)

    return page_notification
