from django.urls import path
from .views import (
    HomeView,
    ItemDetailView , 
    add_to_cart ,
    remove_from_cart , 
    OrderSummaryView , 
    delete_item_from_cart ,
)



app_name = 'core'

urlpatterns = [
    path('',HomeView.as_view(), name='home'),
    path('product/<slug>/',ItemDetailView.as_view(), name='product'),
    path('add_to_cart/<slug:slug>/',add_to_cart , name='add_to_cart'),
    path('remove_from_cart/<slug:slug>/',remove_from_cart , name='remove_from_cart'),
    path('order_summary/',OrderSummaryView.as_view(), name='order_summary'),
    path('delete_item/<slug:slug>/',delete_item_from_cart , name='delete_item_from_cart'),
]