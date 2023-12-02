from django.shortcuts import render

from . models import ShippingAddress, Order, OrderItem

from cart.cart import Cart


from django.http import JsonResponse

from django.core.mail import send_mail

from django.conf import settings

# Create your views here.


def checkout(request):

    # Users with accounts -- Pre-fill the form

    if request.user.is_authenticated:

        try:

            # Authenticated users WITH shipping information 

            shipping_address = ShippingAddress.objects.get(user=request.user.id)

            context = {'shipping': shipping_address}

            


            return render(request, 'payment/checkout.html', context=context)


        except:

            # Authenticated users with NO shipping information

            return render(request, 'payment/checkout.html')

    else:
            
        # Guest users

        return render(request, 'payment/checkout.html')
    


def complete_order(request):
    if request.POST.get('action') == 'post':
        name = request.POST.get('name')
        adminEmail = "uzairf2580@gmail.com"
        email = request.POST.get('email')
        address1 = request.POST.get('address1')
        address2 = request.POST.get('address2')
        city = request.POST.get('city')
        state = request.POST.get('state')
        zipcode = request.POST.get('zipcode')

        # All-in-one shipping address
        shipping_address = (
            address1 + "\n" + address2 + "\n" +
            city + "\n" + state + "\n" + zipcode
        )

        # Shopping cart information
        cart = Cart(request)

        # Get the total price of items
        total_cost = cart.get_total()

        # Order variations
        # Create order -> Account users WITH + WITHOUT shipping information
        if request.user.is_authenticated:
            order = Order.objects.create(
                full_name=name,
                email=email,
                shipping_address=shipping_address,
                amount_paid=total_cost,
                user=request.user
            )
            order_id = order.pk
            product_list = []

            for item in cart:
                product = item['product']
                quantity_ordered = item['qty']

                if product.quantity >= quantity_ordered:
                    product.quantity -= quantity_ordered
                    product.save()
                else:
                    # Handle cases where there's not enough available quantity
                    order_success = False
                    response = JsonResponse({'success': order_success})
                    return response

                OrderItem.objects.create(
                    order_id=order_id,
                    product=product,
                    quantity=quantity_ordered,
                    price=item['price'],
                    user=request.user
                )
                product_list.append(product)

            all_products = product_list

            # Email order
            
            send_mail('Order Placed', 'Hi!' + '\n\n' + 'Thank you for placing your order on Brainstorm Solutions Ecommerce' + '\n\n' +
                      'Please find your order below' + '\n\n' + str(all_products) + 'Quantity: ' + str(quantity_ordered) +'\n\n' + 'Total Paid: $' +
                      str(cart.get_total()), settings.EMAIL_HOST_USER, [email], fail_silently=False)
            send_mail('Order Received', 'Hi!' + '\n\n' + 'An order has been received from : '+ name + '\n\n' +
                      'Find order your order below' + '\n\n' + str(all_products) + 'Quantity: ' + str(quantity_ordered) +'\n\n' + 'Total Paid: $' +
                      str(cart.get_total()), settings.EMAIL_HOST_USER, [adminEmail], fail_silently=False)            
            # Clear shopping cart after successful checkout        
        else:
            # Create order -> Guest users without an account
            order = Order.objects.create(
                full_name=name,
                email=email,
                shipping_address=shipping_address,
                amount_paid=total_cost
            )
            order_id = order.pk
            product_list = []

            for item in cart:
                product = item['product']
                quantity_ordered = item['qty']

                if product.quantity >= quantity_ordered:
                    product.quantity -= quantity_ordered
                    product.save()
                else:
                    # Handle cases where there's not enough available quantity
                    order_success = False
                    response = JsonResponse({'success': order_success})
                    return response

                OrderItem.objects.create(
                    order_id=order_id,
                    product=product,
                    quantity=quantity_ordered,
                    price=item['price']
                )
                product_list.append(product)

            all_products = product_list

            # Email order
            send_mail('Order Placed', 'Hi!' + '\n\n' + 'Thank you for placing your order on Brainstorm Solutions Ecommerce' + '\n\n' +
                      'Please find your order below' + '\n\n' + str(all_products) + '&nbsp'+'Quantity: ' + str(quantity_ordered) +'\n\n' + 'Total Paid: Ksh' +
                      str(cart.get_total()), settings.EMAIL_HOST_USER, [email], fail_silently=False)
            send_mail('Order Received', 'Hi!' + '\n\n' + 'An order has been received from : '+ name + '\n\n' +
                      'Find order your order below' + '\n\n' + str(all_products) + 'Quantity: ' + str(quantity_ordered) +'\n\n' + 'Total Paid: $' +
                      str(cart.get_total()), settings.EMAIL_HOST_USER, [adminEmail], fail_silently=False)   

        order_success = True
        response = JsonResponse({'success': order_success})
        return response


def payment_success(request):


    # Clear shopping cart


    for key in list(request.session.keys()):

        if key == 'session_key':

            del request.session[key]



    return render(request, 'payment/payment-success.html')







def payment_failed(request):

    return render(request, 'payment/payment-failed.html')











