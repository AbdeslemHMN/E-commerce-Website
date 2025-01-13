from django.contrib import admin

# Register your models here.

from .models import Item, Order, OrderItem , Address , Payment , Coupon , Refund

def make_refund_accepted(modeladmin, request, queryset):
        queryset.filter(refund_requested = True).update( refund_requested=False , refund_granted=True )
make_refund_accepted.short_description = "Accept Refund"
class orderAdmin(admin.ModelAdmin):
    list_display = [
        'user', 
        'ordered',
        'being_delivered',
        'received', 
        'refund_requested',
        'refund_granted',
        'shipping_address',
        'billing_address',
        'payment',
        'coupon',
    ]
    list_display_links = ['user','shipping_address','billing_address', 'payment', 'coupon']
    list_filter = ['ordered', 'being_delivered', 'received', 'refund_requested', 'refund_granted']
    search_fields = ['user__username', 'ref_code']
    actions = [make_refund_accepted]

class AddressAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'street_address',
        'apartment_address',
        'zip',
        'country',
        'address_type',
        'default',
    ]
    list_filter = ['default', 'address_type', 'country']
    search_fields = ['user__username' , 'street_address', 'apartment_address', 'zip', 'country']


admin.site.register(Item)
admin.site.register(Order , orderAdmin)
admin.site.register(OrderItem)
admin.site.register(Payment)
admin.site.register(Coupon)
admin.site.register(Address , AddressAdmin)
admin.site.register(Refund)
