from django import forms
from .models import Order


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [
            'first_name', 'last_name', 'phone', 'email',
            'address_line_1', 'address_line_2',
            'country', 'state', 'city', 'order_note'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={
                'placeholder': 'First Name', 'class': 'form-control'
            }),
            'last_name': forms.TextInput(attrs={
                'placeholder': 'Last Name', 'class': 'form-control'
            }),
            'phone': forms.TextInput(attrs={
                'placeholder': 'Phone Number', 'class': 'form-control'
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'Email Address', 'class': 'form-control'
            }),
            'address_line_1': forms.TextInput(attrs={
                'placeholder': 'Address Line 1', 'class': 'form-control'
            }),
            'address_line_2': forms.TextInput(attrs={
                'placeholder': 'Address Line 2', 'class': 'form-control'
            }),
            'country': forms.TextInput(attrs={
                'placeholder': 'Country', 'class': 'form-control'
            }),
            'state': forms.TextInput(attrs={
                'placeholder': 'State', 'class': 'form-control'
            }),
            'city': forms.TextInput(attrs={
                'placeholder': 'City', 'class': 'form-control'
            }),
            'order_note': forms.Textarea(attrs={
                'placeholder': 'Order Note (optional)', 'rows': 3, 'class': 'form-control'
            }),
        }

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone and not phone.isdigit():
            raise forms.ValidationError("Phone number should contain only digits.")
        if phone and len(phone) < 10:
            raise forms.ValidationError("Enter a valid 10-digit phone number.")
        return phone
