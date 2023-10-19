from django.shortcuts import render

from . models import Category, Product, Review
from .forms import ReviewForm
from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse
from django.db.models import Q




# views.py
def add_review(request, product_slug):
    # Retrieve the product based on the product_slug
    product = get_object_or_404(Product, slug=product_slug)

    if request.method == 'POST':
        if request.user.is_authenticated:
            form = ReviewForm(request.POST)
            if form.is_valid():
                review = form.save(commit=False)
                review.user = request.user
                review.product = product
                review.save()
                # Redirect to the product detail page or display a success message
                return redirect('product-info', product_slug=product.slug)
        else:
            # Handle the case where the user is not authenticated
            return redirect('login')  # You can customize this URL to your login page
    else:
        form = ReviewForm()

    context = {'form': form, 'product': product}

    return render(request, 'store/product-info.html', context)

def search(request):
    query = request.GET.get('q')
    results = Product.objects.filter(Q(title__icontains=query) | Q(description__icontains=query))

    context = {
        'query': query,
        'results': results,
    }

    return render(request, 'store/product_search.html', context)

def store(request):

    all_products = Product.objects.all()

    context = {'my_products' : all_products}
    
    return render(request, 'store/store.html', context)

def categories(request):
    all_categories = Category.objects.all()

    return{'all_categories': all_categories}

def list_category(request, category_slug = None):

    category = get_object_or_404(Category, slug = category_slug)

    products = Product.objects.filter(category=category)

    return render(request, 'store/list-category.html', {'category': category, 'products':products})

from .forms import ReviewForm

def product_info(request, product_slug):
    product = get_object_or_404(Product, slug=product_slug)
    available_quantities = range(1, product.quantity + 1)
    
    review_form = ReviewForm()  # Create an instance of the ReviewForm
    
    reviews = Review.objects.filter(product=product)  # Fetch reviews related to this product

    context = {
        'product': product,
        'available_quantities': available_quantities,
        'review_form': review_form,
        'reviews': reviews,  # Pass reviews to the template
    }

    return render(request, 'store/product-info.html', context)

