from django.shortcuts import render

from store.models import Category, Product

from django.shortcuts import get_object_or_404
from . cart import Cart 
from django.core.exceptions import ObjectDoesNotExist  # Import ObjectDoesNotExist
from django.http import JsonResponse
from .models import Rule
from django.db.models import Q


# Create your views here.


def product_info(request, product_slug):
    product = get_object_or_404(Product, slug=product_slug)
    
    available_quantities = range(1, product.quantity + 1)


    context = {'product' : product, 'available_quantities': available_quantities}

    return render(request, 'cart/cart-summary.html', context)

def cart_summary(request):
    cart = Cart(request)
    related_products = []
    frequently_bought_together = {}  # Use a dictionary to store products and their matches

    for cart_item in cart:
        product_name = cart_item['product'].title

        matching_rules = Rule.objects.filter(Q(lhs=product_name) | Q(rhs=product_name))

        frequently_bought_together[product_name] = []  # Initialize an empty list for each product

        for rule in matching_rules:
            if rule.lhs == product_name:
                try:
                    product = Product.objects.get(title=rule.rhs)
                    frequently_bought_together[product_name].append(product)
                except ObjectDoesNotExist:
                    pass
            elif rule.rhs == product_name:
                try:
                    product = Product.objects.get(title=rule.lhs)
                    frequently_bought_together[product_name].append(product)
                except ObjectDoesNotExist:
                    pass
    # Keep track of displayed categories and related products
    displayed_categories = set()

    # Get the categories of products in the cart
    categories = [item['product'].category for item in cart]

    # Loop through the categories and fetch related products
    for category in categories:
        if category not in displayed_categories:
            related_products_from_category = Product.objects.filter(category=category).exclude(id__in=[item['product'].id for item in cart])
            displayed_products_count = 0
            for product in related_products_from_category:
                if displayed_products_count >= 2:
                    break  # Limit to 2 related products per category
                if product.category not in displayed_categories:
                    displayed_categories.add(product.category)
                related_products.append(product)
                displayed_products_count += 1

    context = {
        'related_products': related_products,
        'frequently_bought_together': frequently_bought_together,
    }


    return render(request, 'cart/cart-summary.html', context)
def cart_add(request):
    
    cart = Cart(request)
    
    #return render (request, 'cart/cart-summary.html', {'cart':cart})

    if request.POST.get('action') == 'post':

        product_id = int(request.POST.get('product_id'))
        product_quantity = int(request.POST.get('product_quantity'))# getting product id and quantity from the product info page

        product=get_object_or_404(Product, id=product_id) #getting product which has same product id as the one in the product info

        cart.add(product=product, product_qty=product_quantity)


        cart_quantity = cart.__len__()

        response = JsonResponse({'qty': cart_quantity})

        return response

def cart_delete(request):
    
    cart = Cart(request)
    if request.POST.get('action') == 'post':
        product_id = int(request.POST.get('product_id'))

        cart.delete(product=product_id)

        cart_quantity = cart.__len__()

        cart_total = cart.get_total()

        response = JsonResponse({'qty':cart_quantity, 'total':cart_total})

        return response
        

def cart_update(request):
    cart = Cart(request)
    if request.POST.get('action') == 'post':
        product_id = int(request.POST.get('product_id'))
        product_quantity = int(request.POST.get('product_quantity'))

        cart.update(product=product_id, qty=product_quantity)

        cart_quantity = cart.__len__()

        cart_total = cart.get_total()

        response = JsonResponse({'qty':cart_quantity, 'total':cart_total})

        return response