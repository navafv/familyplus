from django import forms
from .models import Account, UserProfile, NewsletterSubscriber, ContactMessage

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'w-full p-3 border rounded-md'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'w-full p-3 border rounded-md'}))

    class Meta:
        model = Account
        fields = ['first_name', 'last_name', 'phone_number', 'email', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match!")

class UserForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ('first_name', 'last_name', 'phone_number')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'w-full p-3 border rounded-md focus:outline-none focus:ring-1 focus:ring-primary/50'
            })

class UserProfileForm(forms.ModelForm):
    profile_picture = forms.ImageField(required=False, error_messages={'invalid': "Image files only"}, widget=forms.FileInput)

    class Meta:
        model = UserProfile
        fields = ('address_line_1', 'address_line_2', 'city', 'state', 'country', 'profile_picture')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'w-full p-3 border rounded-md focus:outline-none focus:ring-1 focus:ring-primary/50'
            })

class NewsletterSubscriptionForm(forms.ModelForm):
    class Meta:
        model = NewsletterSubscriber
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-2 text-gray-700 bg-white border-none rounded-l-md focus:outline-none',
                'placeholder': 'your.email@example.com',
                'aria-label': 'Email for newsletter',
                'required': True,
            })
        }
        labels = {'email': ''}  # Hide label

class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full p-3 border rounded-md', 'placeholder': 'John Doe'}),
            'email': forms.EmailInput(attrs={'class': 'w-full p-3 border rounded-md', 'placeholder': 'your.email@example.com'}),
            'subject': forms.TextInput(attrs={'class': 'w-full p-3 border rounded-md', 'placeholder': 'Question about a product'}),
            'message': forms.Textarea(attrs={'class': 'w-full p-3 border rounded-md', 'rows': 5, 'placeholder': 'Your message here...'}),
        }
