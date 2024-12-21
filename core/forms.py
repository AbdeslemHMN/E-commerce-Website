from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget

PAYMENT_CHOICES = (
    ('S', 'Stripe'),
    ('P', 'PayPal')
)

class CheckoutForm(forms.Form):
    street_address = forms.CharField(
        widget=forms.TextInput(attrs={
            'placeholder': '1234 Main St'
                                        }))
    apartment_address = forms.CharField(required=False ,
                                            widget=forms.TextInput(attrs={
                                                'placeholder': 'Apartment or suite'
                                                                            }))
    shipping_country = CountryField(blank_label='(select country)').formfield(
        required=False,
        widget=CountrySelectWidget(
            attrs = { 'class' : 'custom-select d-block w-100' }
        )
    )
    billing_country = CountryField(blank_label='(select country)').formfield(
        required=False,
        widget=CountrySelectWidget(
            attrs = { 'class' : 'custom-select d-block w-100' }
        )
    )
    shipping_zip = forms.CharField()
    billing_zip = forms.CharField()
    same_shipping_address = forms.BooleanField(widget=forms.CheckboxInput())
    save_info = forms.BooleanField(widget=forms.CheckboxInput())
    payment_option = forms.ChoiceField(widget=forms.RadioSelect, choices=PAYMENT_CHOICES)



class CouponForm(forms.Form):
    code = forms.CharField(widget=forms.TextInput(
        attrs={
            'class' : 'form-control',
            'placeholder' : 'Coupon code' ,
            'aria-label': 'Recipient\'s username',
            'aria-describedby': 'basic-addon2'
        }
    ))