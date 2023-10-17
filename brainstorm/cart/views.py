from django.shortcuts import render

from store.models import Category, Product

from django.shortcuts import get_object_or_404
from . cart import Cart 

from django.http import JsonResponse

# Create your views here.


def product_info(request, product_slug):
    product = get_object_or_404(Product, slug=product_slug)
    
    available_quantities = range(1, product.quantity + 1)


    context = {'product' : product, 'available_quantities': available_quantities}

    return render(request, 'cart/cart-summary.html', context)

def cart_summary(request):

    return render(request, 'cart/cart-summary.html')

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