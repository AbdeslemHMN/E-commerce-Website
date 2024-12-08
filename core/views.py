from django.shortcuts import render , get_object_or_404
from django.views.generic import DetailView , ListView
from django.shortcuts import redirect
from .models import Item , Order , OrderItem
from django.utils import timezone
from django.contrib import messages

# Create your views here.


def products(request):
    context = {
        'items' : Item.objects.all()
    }
    return render(request, 'product.html', context)

def checkout(request):
    return render(request, 'checkout.html')

class HomeView(ListView):
    model = Item
    template_name = 'home.html'

class ItemDetailView(DetailView):
    model = Item
    template_name = 'product.html'



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

    return redirect('core:product', slug=slug)


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
                return redirect('core:product', slug=slug)
            else:
                order_item.delete()  # Delete the specific OrderItem instance
                messages.info(request, 'This item is not in your cart')
                return redirect('core:product', slug=slug)
        else: 
            # If the item is not in the order, display a message
            messages.info(request, 'This item is not in your cart')
            return redirect('core:product', slug=slug)
    else :
        # if no order exists, display a message
        messages.info(request, 'You have no order')
        return redirect('core:product', slug=slug)
