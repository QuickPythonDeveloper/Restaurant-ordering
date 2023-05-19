from django.shortcuts import render, HttpResponseRedirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from src.restaurants.models import Restaurant
from .models import Cart, Order, Discount
from src.foods.models import Food
from src.accounts.models import Account
from src.notifications.models import Notification


@login_required
def my_orders_view(request):
    orders = Order.objects.all().filter(account=request.user).filter(is_active=True)
    template_name = 'orders/myorders_list.html'
    contex = {
        'orders': orders
    }
    return render(request, template_name, contex)


@login_required
def order_manage_view(request):
    template_name = 'orders/management_index.html'
    if not request.user.is_staff or not request.user.is_superuser:
        return HttpResponseRedirect('/404notfound/')

    orders = Order.objects.all()
    contex = {
        'orders': orders
    }
    return render(request, template_name, contex)


def order_detail_view(request, order_id):
    template_name = 'orders/detail.html'
    try:
        order = Order.objects.get(order_id=order_id)
        cart = order.cart
        products = Food.objects.all().filter(cart=cart)
        quantities = cart.quantities.split(',')
        pro_quantities = zip(products, quantities)
        quantities.remove('')
        if not order.is_active:
            return HttpResponseRedirect('/404notfound/')
    except Order.DoesNotExist:
        return HttpResponseRedirect('/404notfound/')
    contex = {
        'restaurant': cart.restaurant,
        'proQuantities': pro_quantities,
        'order': order,
    }
    return render(request, template_name, contex)


def add_to_cart_view(request):
    template_name = 'orders/confirm-order.html'
    if request.is_ajax():
        restaurant = Restaurant.objects.get(pk=request.POST['restaurant'])
        subtotal = request.POST['totalCost']
        quantity = request.POST['totalquantity']
        slugs = request.POST['slugs'].split(',')
        slugs.remove('')
        grand_total = float(subtotal) + restaurant.service_charge + restaurant.vat_tax
        quantities = request.POST['quantities']
        products = []
        for slug in slugs:
            try:
                food_obj = Food.objects.get(slug=slug)
                products.append(food_obj)
            except Food.DoesNotExist:
                pass

        cart = Cart()
        cart.restaurant = restaurant
        cart.save()
        for product in products:
            cart.products.add(product)
        cart.subtotal = subtotal
        cart.total = grand_total
        cart.quantities = quantities
        cart.save()

    contex = {
        'subtotal': subtotal,
        'quantity': quantity,
        'restaurant': restaurant,
        'grandtotal': grand_total,
        'cart': cart
    }
    return render(request, template_name, contex)


def new_order_view(request):
    template_name = 'orders/confirmed-page.html'
    if request.method == "POST":
        cart_key = request.POST['cart']
        phone = request.POST['cell']
        order_type = request.POST['orderType']
        account = None
        if request.user.is_authenticated:
            account = Account.objects.get(username=request.user.username)
        else:
            qs = Account.objects.filter(phone=phone).exists()
            if qs:
                account = Account.objects.get(phone=phone)
        order = Order()
        order.account = account
        try:
            cart = Cart.objects.get(key=cart_key)
            cart.is_active = True
            cart.save()
            order.cart = cart
        except Cart.DoesNotExist:
            messages.warning(request, "Order request failed! Please try again.")
            return HttpResponseRedirect('/restaurants/' + cart.restaurant.slug + '/')
        _discount = 0.00
        try:
            d_obj = Discount.objects.get(key=request.POST['promoCode'])
            if not d_obj.used:
                _discount = int(float(cart.subtotal * d_obj.percentage) / 100.00)
                d_obj.used = True
                d_obj.save()
        except Discount.DoesNotExist:
            pass
        order.name = request.POST['name']
        order.phone = phone
        order.shipping_address = request.POST['location']
        order.order_type = order_type
        order.payment_method = request.POST['paymentMethod']
        order.expected_time = request.POST['time']

        if order_type == 'home':
            order.cost = cart.total - _discount + 30.00  # Shipping cost
        else:
            order.cost = cart.total - _discount
        order.discount = _discount
        order.save()
        # SEND NOTIFICATION
        if account is not None:
            notification = Notification()
            notification.account = account
            notification.content = "You order <span class='font-weight-bold'>#" + str(
                order.order_no) + "</span> has been added. We will confirm it in minutes."
            notification.link = '/orders/' + order.order_id + '/'
            notification.save()
        return HttpResponseRedirect('/orders/' + order.order_id + '/')
    messages.warning(request, "Something went wrong. Please try again.")
    return HttpResponseRedirect('/restaurants/')


def check_discount_code_view(request):
    if request.is_ajax():
        qs = Discount.objects.filter(key=request.POST['promoCode'])
        if qs.exists():
            obj = Discount.objects.get(key=request.POST['promoCode'])
            if obj.used:
                msg = '<span class="text-warning">Sorry! This code was used before.</span>'
            else:
                msg = '<span class="text-success">Congrats! You will enjoy ' + str(
                    obj.percentage) + "% discount.</span>"
        else:
            msg = '<span class="text-warning">Sorry! No offer for this code.</span>'
        return HttpResponse(msg)
    return HttpResponse("Bad request!")


# UPDATE VISIBILITY STATUS
@login_required
def update_visibility_view(request, order_id):
    try:
        order = Order.objects.get(order_id=order_id)
    except Order.DoesNotExist:
        return HttpResponseRedirect('/404notfound/')
    if not request.user.is_staff or not request.user.is_superuser:
        if request.user != order.account.user or request.method != "POST":
            return HttpResponseRedirect('/404notfound/')
    try:
        if order.is_active:
            order.is_active = False
        else:
            order.is_active = True
        order.save()
    except Exception:
        messages.success(request, "Couldn't execute the request.")

    if request.user.is_staff or request.user.is_superuser:
        return HttpResponseRedirect('/orders/management/')
    messages.success(request, "Order has been removed from your list.")
    return HttpResponseRedirect('/orders/mylist/')


# UPDATE PAYMENT STATUS
@login_required
def update_payment_status_view(request, order_id):
    if not request.user.is_staff or not request.user.is_superuser or request.method != "POST":
        return HttpResponseRedirect('/404notfound/')
    try:
        order = Order.objects.get(order_id=order_id)
        if order.payment_status:
            order.payment_status = False
            notif = "Payment for your order #" + str(order.order_no) + " is pending."
        else:
            order.payment_status = True
            notif = "Payment for your order #" + str(order.order_no) + " is accepted."
        order.save()
    except Order.DoesNotExist:
        messages.success(request, "Couldn't change payment status.")
        notif = ''

    # SEND NOTIFICATION
    if order.account is not None:
        notification = Notification()
        notification.account = order.account
        notification.content = notif
        notification.link = '/orders/' + order.order_id + '/'
        notification.save()
    return HttpResponseRedirect('/orders/management/')


# UPDATE STATUS
@login_required
def update_status_view(request, order_id):
    if not request.user.is_staff or not request.user.is_superuser or request.method != "POST":
        return HttpResponseRedirect('/404notfound/')
    try:
        order = Order.objects.get(order_id=order_id)
        if order.status:
            order.status = False
            notif = "Order #" + str(order.order_no) + " is pending."
        else:
            order.status = True
            notif = "Order #" + str(order.order_no) + " is accepted."
        order.save()
    except Order.DoesNotExist:
        messages.success(request, "Couldn't change status.")

    # SEND NOTIFICATION
    if order.account is not None:
        notification = Notification()
        notification.account = order.account
        notification.content = notif
        notification.link = '/orders/' + order.order_id + '/'
        notification.save()

    return HttpResponseRedirect('/orders/management/')


# DELETE ORDER
@login_required
def delete_order_view(request, order_id):
    if not request.user.is_staff or not request.user.is_superuser or request.method != "POST":
        return HttpResponseRedirect('/404notfound/')
    try:
        order = Order.objects.get(order_id=order_id)
        # SEND NOTIFICATION
        if order.account is not None:
            notification = Notification()
            notification.account = order.account
            notification.content = "Order #" + str(order.order_no) + " has been deleted."
            notification.link = '/orders/' + order.order_id + '/'
            notification.save()
        order.delete()
    except Order.DoesNotExist:
        messages.success(request, "Couldn't change status.")
        pass

    return HttpResponseRedirect('/orders/management/')
