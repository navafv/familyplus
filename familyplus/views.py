from django.shortcuts import render, redirect
from store.models import Product
from category.models import Category
from accounts.forms import ContactForm
from accounts.models import ContactMessage
from django.contrib import messages

def home(request):  
    products = Product.objects.all().filter(is_available=True).order_by('-created_date')[:12]
    categories = Category.objects.all()[:4]
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
        form = ContactForm()

    context = {
        'form': form,
    }
    return render(request, 'contact.html', context)