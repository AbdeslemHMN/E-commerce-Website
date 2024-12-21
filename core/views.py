from django.shortcuts import render , get_object_or_404
from django.http import Http404
from django.views.generic import DetailView , ListView , View
from django.shortcuts import redirect
from .models import Item , Order , OrderItem , BillingAddress , Payment , Coupon
from .forms import CheckoutForm , CouponForm
from django.utils import timezone
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
import stripe

# cSpell:ignore REFERER


stripe.api_key = settings.STRIPE_SECRET_KEY

# Create your views here.

def products(request):
    context = {
        'items' : Item.objects.all()
    }
    return render(request, 'product.html', context)

class CheckoutView(View):
    def get(self, *args, **kwargs):
        try:
            form = CheckoutForm()
            order = Order.objects.get(user = self.request.user , ordered = False)
            context = {
                'form' : form ,
                'couponform' : CouponForm() ,
                'order' : order , 
                "DISPLAY_COUPON_FORM" : True
            }
            return render(self.request, 'checkout.html', context) 
        except ObjectDoesNotExist:
            messages.warning(self.request, 'You have not placed any order yet')
            return redirect('core:checkout')
        
    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try : 
            order = Order.objects.get(user = self.request.user , ordered = False)
            if form.is_valid():
                street_address = form.cleaned_data.get('street_address')
                apartment_address = form.cleaned_data.get('apartment_address')
                shipping_country = form.cleaned_data.get('shipping_country')
                billing_country = form.cleaned_data.get('billing_country')
                shipping_zip = form.cleaned_data.get('shipping_zip')
                billing_zip = form.cleaned_data.get('billing_zip')
                # same_shipping_address = form.cleaned_data.get('same_billing_address')
                # save_info = form.cleaned_data.get('save_info')
                payment_option = form.cleaned_data.get('payment_option')
                billing_address = BillingAddress(
                    user = self.request.user,
                    street_address = street_address,
                    apartment_address = apartment_address,
                    zip = shipping_zip,
                    country = shipping_country
                    )
                billing_address.save()
                order.billing_address = billing_address
                order.save()
                if (payment_option == 'S'):
                    return redirect('core:payment' , payment_option='stripe')
                elif (payment_option == 'P'):
                    return redirect('core:payment' , payment_option='paypal')
                else :
                    messages.warning(self.request, 'Please select a payment option')
                    context = {
                        'form' : form ,
                        'order' : order
                    }
                    return render(self.request, 'checkout.html', context)
            # handle Form is invalid # 
            else:
                messages.error(self.request, "Invalid form submission. Please try again.")
                context = {
                    'form' : form ,
                    'order' : order
                }
                return render(self.request, 'checkout.html', context)
        except ObjectDoesNotExist:
            messages.error(self.request, 'You have not placed any order yet')
            return redirect('core:checkout')

class HomeView(ListView):
    model = Item
    paginate_by = 10
    template_name = 'home.html'

class ItemDetailView(DetailView):
    model = Item
    template_name = 'product.html'

class PaymentView(View):  
    def get(self , *args , **kwargs):
        order = Order.objects.get(user = self.request.user , ordered = False)
        if order.billing_address:
            context = {
                'order' : order ,
                'STRIPE_PUBLIC_KEY' : settings.STRIPE_PUBLIC_KEY ,
                "DISPLAY_PAYMENT_FORM" : False
            }
            return render(self.request , 'payment.html', context)
        else:
            messages.warning(self.request , 'Please add your billing address')
            return redirect('core:checkout')
    
    def post(self , *args , **kwargs):
        token = self.request.POST.get('stripeToken')
        order = Order.objects.get(user = self.request.user , ordered = False)
        amount=int(order.get_total() * 100)

        try:
            charge = stripe.Charge.create(
            amount=amount, # in cents
            currency="usd",
            source=token,
            )
            #create payment 
            payment = Payment()
            payment.stripe_charge_id = charge['id']
            payment.user = self.request.user
            payment.amount = amount
            payment.save()
            #assign the payment to the order
            order_items = order.items.all()
            order_items.update(ordered=True)
            for item in order_items:
                item.save()
            order.ordered = True
            order.payment = payment
            order.save()
            messages.success(self.request, 'Your order has been placed successfully')
            return redirect('/')
        except stripe.error.CardError as e:
            # Since it's a decline, stripe.error.CardError will be caught
            body = e.json_body
            err  = body['error']['message']
            messages.error(self.request, err)
            return redirect('/')
        except stripe.error.RateLimitError as e:
            # Too many requests made to the API too quickly
            messages.error(self.request, "Rate limit error")
            return redirect('/')
        except stripe.error.InvalidRequestError as e:
            # Invalid parameters were supplied to Stripe's API
            messages.error(self.request, "Invalid parameters")
            return redirect('/')
        except stripe.error.AuthenticationError as e:
            # Authentication with Stripe's API failed
            # (maybe you changed API keys recently)
            messages.error(self.request, "Authentication with Stripe failed")
            return redirect('/')
        except stripe.error.APIConnectionError as e:
            # Network communication with Stripe failed
            messages.error(self.request, "Network error")
        except stripe.error.StripeError as e:
            # Display a very generic error to the user, and maybe send
            # yourself an email
            messages.error(self.request, "Something went wrong , you were not charged , please try again later")
            return redirect('/')
        except Exception as e:
            # send yourself an email
            messages.error(self.request, "a serious error occurred , we have been notified")
            return redirect('/')
        
    
class OrderSummaryView(LoginRequiredMixin,View):
    def get(self , *args , **kwargs):
        try:
            order = Order.objects.get(user = self.request.user , ordered = False)
            context = {
                'object' : order
            }
            return render(self.request , 'order_summary.html' , context)
        except ObjectDoesNotExist:
            messages.warning(self.request , 'You have not placed any order yet')
            return redirect('/')


@login_required
def add_to_cart(request, slug):
    # Get the item to add to the cart
    item = get_object_or_404(Item, slug=slug)

    # Check if an order already exists in the current order
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
    

def get_coupon(code):
    try:
        return Coupon.objects.get(code=code)
    except Coupon.DoesNotExist:
        return None


class AddCouponView(View):
    def post(self , *args , **kwargs):
            form = CouponForm(self.request.POST or None)
            user = self.request.user
            if form.is_valid() and user.is_authenticated:
                try:
                    code = form.cleaned_data.get('code')
                    order = Order.objects.get(user=user, ordered=False)
                    coupon = get_coupon(code)
                    if coupon:
                        if coupon.user == user and coupon.couponUsed:
                            raise ValueError("This coupon has already been used.")
                        coupon.user = user
                        coupon.couponUsed = True
                        coupon.save()
                        order.coupon = coupon
                        order.save()
                        messages.success(self.request, 'Coupon code was added to your cart.')
                    else:
                        raise Http404("This coupon does not exist.")
                    return redirect('core:checkout')
                except ObjectDoesNotExist:
                    messages.warning(self.request, 'You have not placed any order yet.')
                    return redirect('core:checkout')
                except ValueError as e:
                    messages.warning(self.request, str(e))
                    return redirect('core:checkout')
                except Exception as e:
                    messages.error(self.request, f"{str(e)}")
                    return redirect('core:checkout')
            else:
                messages.error(self.request, 'Invalid form submission. Please try again.')
                return redirect('core:checkout')
    
class DeleteCouponView(View):
        def post(self , *args , **kwargs):
            user = self.request.user
            if user.is_authenticated:
                try:
                    order = Order.objects.get(user=user, ordered=False)
                    if not order.coupon:
                        raise ValueError("No coupon is applied to the current order.")
                    coupon = order.coupon
                    if coupon.user == user and coupon.couponUsed:
                        coupon.couponUsed = False
                        coupon.save()
                        order.coupon = None
                        order.save()
                        messages.success(self.request, 'Coupon code was removed.')
                    else:
                        raise ValueError("This coupon is not valid or not used.")
                    return redirect('core:checkout')
                except ObjectDoesNotExist:
                    messages.warning(self.request, 'You have not placed any order yet.')
                    return redirect('core:checkout')
                except ValueError as e:
                    messages.warning(self.request, str(e))
                    return redirect('core:checkout')
                except Exception as e:
                    messages.error(self.request, f"{str(e)}")
                    return redirect('core:checkout')
            else:
                messages.error(self.request, 'You need to be logged in to perform this action.')
                return redirect('core:checkout')
