from django.contrib import messages
from django.shortcuts import HttpResponseRedirect
from django.contrib.auth.decorators import login_required

from .models import Review
from src.restaurants.models import Restaurant
from src.general.functions import get_review_status, get_stars
from src.general.utils import update_restaurant_review


@login_required
def delete_view(request, pk):
    try:
        review = Review.objects.get(pk=pk)
    except Review.DoesNotExist:
        return HttpResponseRedirect('/404notfound/')

    if not request.method == "POST" or review.account.user != request.user:
        messages.warning(request, 'Unauthorized request!')
        return HttpResponseRedirect("/restaurants/" + review.restaurant.slug + '/review/')

    review.delete()
    messages.success(request, 'Review has been deleted.')
    return HttpResponseRedirect("/restaurants/" + review.restaurant.slug + '/review/')


def create_view(request):
    next_url = request.GET.get('next', '/')
    if request.user.is_authenticated:
        if request.method == "POST":
            review = Review()
            review.account = request.user
            review.restaurant = Restaurant.objects.get(pk=int(request.POST['restaurant']))
            review.title = request.POST['title']
            review.content = request.POST['review']
            review.food = int(request.POST['food'])
            review.price = int(request.POST['price'])
            review.service = int(request.POST['service'])
            review.environment = int(request.POST['environment'])
            result = sum([review.food, review.price, review.service, review.environment]) / 4.0
            review.average = round(result, 1)
            review.status = get_review_status(review.average)
            stars = get_stars(review.average)
            review.star1 = stars[0]
            review.star2 = stars[1]
            review.star3 = stars[2]
            review.star4 = stars[3]
            review.star5 = stars[4]
            if review.title == '':
                msg = "Title field is required."
            else:
                ck = update_restaurant_review(review.restaurant, review)
                if ck:
                    msg = 'Review has been saved.'
                    review.save()
                else:
                    msg = 'Something went wrong'
        else:
            msg = 'Bad request.'
    else:
        messages.success(request, "You need to login first to write a review.")
        return HttpResponseRedirect("/accounts/login/?next=" + next_url)

    if msg != '':
        messages.success(request, msg)
    return HttpResponseRedirect('/restaurants/' + review.restaurant.slug + "/review/")
