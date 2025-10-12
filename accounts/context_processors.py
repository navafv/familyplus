
from .forms import NewsletterSubscriptionForm

def newsletter_form(request):
    """Makes the newsletter form available in all templates."""
    return {'newsletter_form': NewsletterSubscriptionForm()}