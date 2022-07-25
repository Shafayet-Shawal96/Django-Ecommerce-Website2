from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from App_Order.models import Order 
from App_Payment.models import BillingAddress
from App_Payment.forms import BillingForm

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
    return render(request, 'App_Payment/checkout.html', context={'form':form, "order_items":order_items, "order_total":order_total})
