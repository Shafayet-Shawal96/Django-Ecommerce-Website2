from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Cart, Order
from App_Shop.models import Product
# Create your views here.

@login_required
def add_to_cart(request, pk):
    item = get_object_or_404(Product, pk=pk)
    order_item = Cart.objects.get_or_create(item=item, user=request.user, purchased=False)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.orderitem.filter(item=item).exists():
            order_item[0].quantity += 1
            order_item[0].save()
            messages.info(request, "This item quantity is updated")
            return redirect("App_Shop:home")
        else:
            order.orderitem.add(order_item[0])
            messages.info(request, "This item was added to your cart")
            return redirect("App_Shop:home")
    else:
        order = Order(user=request.user)
        order.save()
        order.orderitem.add(order_item[0])
        messages.info(request, "This item was added to your cart")
        return redirect("App_Shop:home")

@login_required
def cart_view(request):
    carts = Cart.objects.filter(user=request.user, purchased=False)
    orders = Order.objects.filter(user=request.user, ordered=False)
    if carts.exists() and orders.exists():
        order = orders[0]
        return render(request, 'App_Order/cart.html', context={'carts': carts, 'order':order})
    else:
        messages.warning(request, "You don't have any item in your cart!")
        return redirect("App_Shop:home")