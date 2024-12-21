from django.contrib import admin

# Register your models here.

from .models import Item, Order, OrderItem , BillingAddress , Payment , Coupon

class orderAdmin(admin.ModelAdmin):
    list_display = ['user', 'ordered']

admin.site.register(Item)
admin.site.register(Order , orderAdmin)
admin.site.register(OrderItem)
admin.site.register(Payment)
admin.site.register(Coupon)
admin.site.register(BillingAddress)
