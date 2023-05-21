from django.shortcuts import render, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import HttpResponse

from .models import Notification
from src.accounts.models import Account


@login_required
def notification_list_view(request):
    template_name = 'notifications.html'
    account = Account.objects.get(username=request.user.username)
    notif_list = Notification.objects.all().filter(account=account)
    page = request.GET.get('page', 1)
    paginator = Paginator(notif_list, 10)
    try:
        notifications = paginator.page(page)
    except PageNotAnInteger:
        notifications = paginator.page(1)
    except EmptyPage:
        notifications = paginator.page(paginator.num_pages)

    return render(request, template_name, {'notifications': notifications})


@login_required
def seen_status_view(request):
    if not request.is_ajax() or request.method != "POST":
        return HttpResponseRedirect('/404notfound/')
    if request.is_ajax():
        pk = request.POST['pk']
        try:
            notif = Notification.objects.get(pk=pk)
        except Notification.DoesNotExist:
            return HttpResponseRedirect('/404notfound/')
        if not notif.is_seen:
            notif.is_seen = True
            notif.save()
        return HttpResponse()
