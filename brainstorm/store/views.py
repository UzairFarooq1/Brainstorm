from django.shortcuts import render

from . models import Category, Product, Review 
from payment.models import OrderItem
from .forms import ReviewForm
from django.shortcuts import get_object_or_404, redirect
from django.http import JsonResponse
from django.db.models import Q
from django.db.models import Sum, Avg
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import random
from django.contrib import messages






# views.py
def add_review(request, product_slug):
    # Retrieve the product based on the product_slug
    product = get_object_or_404(Product, slug=product_slug)

    if request.method == 'POST':
        if request.user.is_authenticated:
            # Check if the user has already reviewed the product
            if Review.objects.filter(product=product, user=request.user).exists():
                messages.error(request, "You have already reviewed this product.")
                return redirect('product-info', product_slug=product.slug)
            
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

    context = {'form': form,
            'product': product,
            }

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
# Number of products to display per page
    per_page = 10

    paginator = Paginator(all_products, per_page)

    # Get the current page number from the URL parameter
    page = request.GET.get('page')

    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver the first page.
        products = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g., 9999), deliver the last page of results.
        products = paginator.page(paginator.num_pages)

    top_selling_products = (
        OrderItem.objects
        .values('product__title')
        .annotate(total_quantity=Sum('quantity'))
        .order_by('-total_quantity')  # Order by total_quantity in descending order
    )[:4] # Limit to the top 4 selling products

    # Retrieve the corresponding product information from the Product model
    top_products_data = [
        {
            'title': item['product__title'],
            'quantity': item['total_quantity'],
        }
        for item in top_selling_products
    ]

    # Combine product data with quantities
    top_products_with_quantity = [
        {
            'product': Product.objects.get(title=item['title']),
            'quantity': item['quantity'],
        }
        for item in top_products_data
    ]

    # Calculate the average rating for each product using the Review table
    top_rated_products = []

    for product in all_products:
        avg_rating = Review.objects.filter(product=product).aggregate(avg_rating=Avg('rating'))['avg_rating']
        num_reviews = Review.objects.filter(product=product).count()
        if avg_rating is not None and avg_rating >= 4.0:
            top_rated_products.append({
                'product': product,
                'num_reviews' : num_reviews,
                'avg_rating': avg_rating,
            })

    if request.user.is_authenticated:
     # Get the user's order history
        user_orders = OrderItem.objects.filter(order__user=request.user)

    # Extract product IDs from the user's order history
        ordered_product_ids = [order.product.id for order in user_orders]

    # Retrieve products from the same category as those previously ordered
        recommended_products = Product.objects.exclude(id__in=ordered_product_ids).filter(
            category__in=Product.objects.filter(id__in=ordered_product_ids).values('category'))[:5]
    else:
        # User is not authenticated, provide an alternative for anonymous users
        all_products = Product.objects.all()
        recommended_products = random.sample(list(all_products), min(5, len(all_products)))



    context = {'my_products' : products, 
               'top_products_with_quantity': top_products_with_quantity, 
               'top_rated_products': top_rated_products,
               'recommended_products': recommended_products} #'top_products' :top_products, 'top_product_quantity' : top_product_quantity}
    
    return render(request, 'store/store.html', context)

def categories(request):
    all_categories = Category.objects.all()

    return{'all_categories': all_categories}

def list_category(request, category_slug = None):

    category = get_object_or_404(Category, slug = category_slug)

    products = Product.objects.filter(category=category)

    return render(request, 'store/list-category.html', {'category': category, 'products':products})


def product_info(request, product_slug):
    product = get_object_or_404(Product, slug=product_slug)
    available_quantities = range(1, product.quantity + 1)
    
    review_form = ReviewForm()
    reviews = Review.objects.filter(product=product)

    # Get related products from the same category
    related_products = Product.objects.filter(category=product.category).exclude(slug=product_slug)

    context = {
        'product': product,
        'available_quantities': available_quantities,
        'review_form': review_form,
        'reviews': reviews,
        'related_products': related_products, 
        
          # Add related products to the context
    }

    return render(request, 'store/product-info.html', context)
