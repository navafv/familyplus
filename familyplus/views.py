from django.shortcuts import render, redirect
from django.contrib import messages
from store.models import Product
from category.models import Category
from accounts.forms import ContactForm

def home(request):
    try:
        products = Product.objects.filter(is_available=True).order_by('-created_date')[:12]
        categories = Category.objects.all()[:4]
    except Exception:
        products = []
        categories = []

    context = {
        'products': products,
        'categories': categories,
    }
    return render(request, 'home.html', context)

def about(request):
    return render(request, 'about.html')

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Thank you for your message! We will get back to you shortly.')
            return redirect('contact')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ContactForm()

    context = {'form': form}
    return render(request, 'contact.html', context)

def error_404(request, exception=None):
    return render(request, 'errors/404.html', status=404)

def error_500(request):
    return render(request, 'errors/500.html', status=500)
