from django.shortcuts import render, HttpResponseRedirect

from .models import Restaurant, ServiceTime, RestaurantReview


def restaurant_list(request):
    template_name = 'restaurants/restaurants_list.html'
    if request.is_ajax() and request.method == "POST":
        request_data = int(request.POST['dataNo'])
        restaurants = Restaurant.objects.all().filter(is_active=True)[request_data:(request_data + 10)]
        return render(request, 'restaurants/load_more_restaurant.html', {'restaurants': restaurants})
    restaurants = Restaurant.objects.all().filter(is_active=True)[:20]
    contex = {
        'restaurants': restaurants
    }

    return render(request, template_name, contex)


def restaurant_detail(request, slug):
    try:
        restaurant = Restaurant.objects.get(slug=slug)
    except Restaurant.DoesNotExist:
        return HttpResponseRedirect("/404notfound/")
    service_times = ServiceTime.objects.get(restaurant=restaurant)
    review = RestaurantReview.objects.all().filter(restaurant=restaurant)
    template_name = 'restaurants/detail.html'
    contex = {
        'restaurant': restaurant,
        'service_times': service_times,
        'active_d': 'tab_a_active',
        'foods': restaurant.food_items.all(),
        'review': review,
    }

    return render(request, template_name, contex)
