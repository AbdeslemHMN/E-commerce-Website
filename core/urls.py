from django.urls import path ,re_path
from .views import (
    HomeView,
    ItemDetailView , 
    add_to_cart ,
    remove_from_cart , 
    OrderSummaryView , 
    delete_item_from_cart ,
    CheckoutView , 
    PaymentView , 
    AddCouponView ,
    DeleteCouponView ,
)



app_name = 'core'

urlpatterns = [
    path('',HomeView.as_view(), name='home'),
    path('product/<slug>/',ItemDetailView.as_view(), name='product'),
    path('add-to_cart/<slug:slug>/',add_to_cart , name='add_to_cart'),
    path('remove_from_cart/<slug:slug>/',remove_from_cart , name='remove_from_cart'),
    path('order_summary/',OrderSummaryView.as_view(), name='order_summary'),
    path('delete_item/<slug:slug>/',delete_item_from_cart , name='delete_item_from_cart'),
    path('add_coupon/',AddCouponView.as_view() , name='add_coupon'),
    path('delete_coupon/',DeleteCouponView.as_view() , name='delete_coupon'),
    path('checkout/',CheckoutView.as_view(), name='checkout'),
    re_path(r'^payment/(?P<payment_option>(stripe|paypal))/$', PaymentView.as_view(), name='payment'),


]