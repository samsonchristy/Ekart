from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .models import OrderItem, Order
from .forms import OrderCreateForm
from cart.cart import Cart
from .tasks import order_created
from django.contrib.admin.views.decorators import staff_member_required
from .utils import render_to_pdf
from django.http import HttpResponse
from django.template.loader import get_template


# Create your views here.

def order_create(request):
    cart = Cart(request)
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save()
            for item in cart:
                OrderItem.objects.create(order=order,product=item['product'],price=item['price'],quantity=item['quantity'])
            #clear the cart
            cart.clear()
            # launch asynchronous task (celery -A Ekart worker -l info -P gevent)
            order_created.delay(order.id)
            # set the order in the session
            request.session['order_id'] = order.id
            #redirect for payment
            return redirect(reverse('payment:process'))
            #return render(request,'orders/order/created.html',{'order':order})
    else:
        form = OrderCreateForm()
    return render(request,'orders/order/create.html',{'cart':cart, 'form':form})

@staff_member_required
def admin_order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request,'admin/orders/order/detail.html',{'order':order})

@staff_member_required
def admin_order_pdf(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    context = {
        "order": order
    }
    pdf = render_to_pdf('orders/order/pdf.html', context)
    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'filename="order_{}.pdf"'.format(order.id)
        return response
    return HttpResponse("Not found")