from django.shortcuts import render , get_object_or_404
from django.views.generic import DetailView , ListView , View
from django.shortcuts import redirect
from .models import Item , Order , OrderItem
from .forms import CheckoutForm
from django.utils import timezone
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

# Create your views here.


def products(request):
    context = {
        'items' : Item.objects.all()
    }
    return render(request, 'product.html', context)

class CheckoutView(View):
    def get(self, *args, **kwargs):
        pass
        
    def post(self, *args, **kwargs):
        pass
        

class HomeView(ListView):
    model = Item
    paginate_by = 10
    template_name = 'home.html'

class ItemDetailView(DetailView):
    model = Item
    template_name = 'product.html'


class OrderSummaryView(LoginRequiredMixin,View):
    def get(self , *args , **kwargs):
        try:
            order = Order.objects.get(user = self.request.user , ordered = False)
            context = {
                'object' : order
            }
            return render(self.request , 'order_summary.html' , context)
        except ObjectDoesNotExist:
            messages.error(self.request , 'You have not placed any order yet')
            return redirect('/')


@login_required
def add_to_cart(request, slug):
    # Get the item to add to the cart
    item = get_object_or_404(Item, slug=slug)

    # Check if an order item for this item already exists in the current order
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]

        # Check if the item is already in the order
        order_item_qs = OrderItem.objects.filter(order=order, item=item)
        if order_item_qs.exists():
            # If the item is already in the order, increase its quantity
            order_item = order_item_qs.first()
            order_item.quantity += 1
            order_item.save()
            messages.info(request, 'This item quantity was updated')
        else:
            # If the item is not in the order, create a new order item and add it to the order
            order_item = OrderItem.objects.create(item=item , user=request.user)
            order.items.add(order_item)
            messages.info(request, 'This item was added to your cart')
    else:
        # If no order exists, create a new order and add the item
        order_date = timezone.now()
        order = Order.objects.create(user=request.user, ordered_date=order_date)
        order_item = OrderItem.objects.create(item=item)
        order.items.add(order_item)
        messages.info(request, 'This item was added to your cart')

    return redirect(request.META.get('HTTP_REFERER', '/'))

@login_required
def remove_from_cart(request, slug):
    # Get the item to remove from the cart
    item = get_object_or_404(Item, slug=slug)

    # Check if an order item for this item exists in the current order
    order_qs = Order.objects.filter(user = request.user , ordered = False )
    if order_qs.exists():
        order = order_qs[0]
        order_item_qs = OrderItem.objects.filter(order = order , item = item , ordered = False)
        if order_item_qs.exists():
            # If the item is in the order, remove it and decrement its quantity
            order_item = order_item_qs.first()
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save() 
                messages.info(request, 'Item removed from cart')
                return redirect(request.META.get('HTTP_REFERER', '/'))
            else:
                order_item.delete()  # Delete the specific OrderItem instance
                messages.info(request, 'This item is not in your cart now')
                return redirect(request.META.get('HTTP.REFERER', '/'))
        else: 
            # If the item is not in the order, display a message
            messages.info(request, 'This item is not in your cart')
            return redirect(request.META.get('HTTP.REFERER', '/'))
    else :
        # if no order exists, display a message
        messages.info(request, 'You have no order')
        return redirect(request.META.get('HTTP_REFERER', '/'))
    
@login_required
def delete_item_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    # Check if an order item for this item already exists in the current order
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]

        # Check if the item is already in the order
        order_item_qs = OrderItem.objects.filter(order=order, item=item)
        if order_item_qs.exists():
            # If the item is already in the order, increase its quantity
            order_item = order_item_qs.first()
            order_item.delete()
            messages.info(request, 'This item is removed from your cart')
        else:
            messages.info(request, 'This item isn\'t in your cart')
    else:
        messages.info(request, 'You have no order')

    return redirect(request.META.get('HTTP_REFERER', '/'))
    
