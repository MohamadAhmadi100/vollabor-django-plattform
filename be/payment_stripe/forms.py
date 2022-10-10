from django import forms

class PymentForm(forms.Form):
	country = forms.CharField()
	# amount = forms.CharField()
	gateway = forms.CharField(
	)
	
class PaymentMethodForm(forms.Form):
	payment_method = forms.CharField()