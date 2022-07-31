from django.shortcuts import render, HttpResponseRedirect, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from App_Order.models import Cart, Order 
from App_Payment.models import BillingAddress
from App_Payment.forms import BillingForm

import requests
import socket
import string
import random
from decimal import Decimal
from sslcommerz_sdk.enums import TransactionStatus
from .payment_handler import payment_handler, store

# Create your views here.
@login_required
def checkout(request):
    saved_address = BillingAddress.objects.get_or_create(user=request.user)
    saved_address = saved_address[0]
    form = BillingForm(instance=saved_address)
    if request.method=="POST":
        form = BillingForm(request.POST, instance=saved_address)
        if form.is_valid():
            form.save()
            messages.success(request, "Shipping Address Saved!")
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    order_items = order_qs[0].orderitem.all()
    order_total = order_qs[0].get_totals()
    return render(request, 'App_Payment/checkout.html', context={'form':form, 
    "order_items":order_items, "order_total":order_total, "saved_address":saved_address})

@login_required
def payment(request):
    saved_address = BillingAddress.objects.get_or_create(user=request.user)
    if not saved_address[0].is_fully_filled():
        messages.info(request, "Please complete shipping adress!")
        return redirect("App_Payment:checkout")
    
    if not request.user.profile.is_fully_filled():
        messages.info(request, "Please complete profile details")
        return redirect("App_Login:profile")
    
    order_qs = Order.objects.filter(user = request.user, ordered=False)
    order_items = order_qs[0].orderitem.all()
    order_items_count = order_qs[0].orderitem.count()
    order_total = order_qs[0].get_totals()

    tran_id =  ''.join(random.choice(string.ascii_lowercase+string.ascii_uppercase+string.ascii_letters+string.digits) for i in range(16))
    print(tran_id)
    session, created = payment_handler.get_or_create_session(
        store=store,
        tran_id=tran_id,
        currency="BDT",
        total_amount=Decimal(order_total),
        cus_name=request.user.profile.full_name,
        cus_email=request.user.email,
        cus_add1=request.user.profile.address_1,
        cus_city=request.user.profile.city,
        cus_postcode=request.user.profile.zipcode,
        cus_country=request.user.profile.country,
        cus_phone=request.user.profile.phone,
        success_url=request.build_absolute_uri(reverse("App_Payment:complete")),
        fail_url=request.build_absolute_uri(reverse("App_Payment:complete")),
        cancel_url=request.build_absolute_uri(reverse("App_Payment:complete")),
        ipn_url=request.build_absolute_uri(reverse("App_Payment:complete")),
    )

    # ipn_view(session.id)

    return redirect(session.redirect_url)

# def ipn_view():
#     # TODO: Make this URL public, i.e accessible without logging in
#     # TODO: Disable CSRF protection for this view
#     # TODO: post_dict = {dict of request POST values}
#     session, verified_right_now = payment_handler.verify_transaction(
#         payload=post_dict,
#     )
#     if verified_right_now:
#         if session.status == TransactionStatus.VALID:
#             print(f"Tran ID: {session.tran_id} successful...")
#             # TODO: Update order payment status in your database
#         else:
#             print("Transaction failed/cancelled!")
#             # TODO: Unfreeze the cart sothat customer can modify/delete the cart

@csrf_exempt
def complete(request):
    if request.method=='POST' or request.method=='post':
        payment_data=request.POST
        status = payment_data['status']
        
        if status == 'VALID':
            val_id = payment_data['val_id']
            tran_id = payment_data['tran_id']
            messages.success(request, "Your Payment Completed Successfully! Page will be redirected in 5 seconds")
            return HttpResponseRedirect(reverse("App_Payment:purchase", kwargs={'val_id': val_id, 'tran_id':tran_id,}))
        elif status == 'FAILED':
            messages.warning(request, "Your Payment Failed! Please Try Again! Page will be redirected in 5 seconds")
    return render(request, "App_Payment/complete.html", context={})

@login_required
def purchase(request, val_id, tran_id):
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    order = order_qs[0]
    orderId = tran_id
    order.ordered = True
    order.orderId = orderId 
    order.payment_Id = val_id 
    order.save()
    cart_items = Cart.objects.filter(user=request.user, purchased=False)
    for item in cart_items:
        item.puchased = True
        item.save()
    return HttpResponseRedirect(reverse("App_Shop:home"))

@login_required
def order_view(request):
    try:
        orders = Order.objects.filter(user=request.user, ordered=True)
        context = {"orders": orders}
    except:
        messages.warning(request, "You do not have an active order")
        return redirect("App_Shop:home")
    
    return render(request, "App_Payment/order.html", context=context)