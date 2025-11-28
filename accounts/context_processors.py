from .forms import NewsletterSubscriptionForm

def newsletter_form(request):
    """
    Adds the newsletter subscription form to all templates via context processors.
    """
    form = NewsletterSubscriptionForm()
    return {'newsletter_form': form}
