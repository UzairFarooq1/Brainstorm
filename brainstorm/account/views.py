from django.shortcuts import redirect, render

from .forms import CreateUserForm, LoginForm, UpdateUserForm

from payment.forms import ShippingForm
from payment.models import ShippingAddress

from payment.models import Order, OrderItem


from django.contrib.auth.models import User

from django.contrib.sites.shortcuts import get_current_site
from . token import user_tokenizer_generate

from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from django.contrib.auth.models import auth
from django.contrib.auth import authenticate, login, logout

from django.db.models import Q
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from io import BytesIO
from reportlab.lib import styles
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph

from django.db.models import Sum


import pandas as pd
import matplotlib.pyplot as plt
import base64
from django.db.models import Count



from django.contrib.auth.decorators import login_required


from django.contrib import messages
# Create your views here.

def register(request):

    form = CreateUserForm()

    if request.method == 'POST':

        form = CreateUserForm(request.POST)

        if form.is_valid(): 

            user = form.save()

            user.is_active = False

            user.save()

            # Email verification setup (template)

            current_site = get_current_site(request)

            subject = 'Account verification email'

            message = render_to_string('account/registration/email-verification.html', {
            
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': user_tokenizer_generate.make_token(user),
            
            })

            user.email_user(subject=subject, message=message)


            return redirect('email-verification-sent')



    context = {'form':form}


    return render(request, 'account/registration/register.html', context=context)


def email_verification(request, uidb64, token):

    # uniqueid

    unique_id = force_str(urlsafe_base64_decode(uidb64))

    user = User.objects.get(pk=unique_id)
    
    # Success

    if user and user_tokenizer_generate.check_token(user, token):

        user.is_active = True

        user.save()

        return redirect('email-verification-success')


    # Failed 

    else:

        return redirect('email-verification-failed')
    


def email_verification_sent(request):

    return render(request, 'account/registration/email-verification-sent.html')


def email_verification_success(request):

    return render(request, 'account/registration/email-verification-success.html')

def email_verification_failed(request):

    return render(request, 'account/registration/email-verification-failed.html')

#login view

def my_login(request):

    form = LoginForm()

    if request.method == 'POST':

        form = LoginForm(request, data=request.POST)

        if form.is_valid():

            username = request.POST.get('username')
            password = request.POST.get('password')

            user = authenticate(request, username=username, password=password)

            if user is not None:

                auth.login(request, user)

                return redirect("store")


    context = {'form':form}

    return render(request, 'account/my-login.html', context=context)


# logout

def user_logout(request):

    try:

        for key in list(request.session.keys()):

            if key == 'session_key':

                continue

            else:

                del request.session[key]


    except KeyError:

        pass


    messages.success(request, "Logout success")

    return redirect("store")


@login_required(login_url='my-login')
def profile_management(request):    

    # Updating our user's username and email

    user_form = UpdateUserForm(instance=request.user)

    if request.method == 'POST':

        user_form = UpdateUserForm(request.POST, instance=request.user)

        if user_form.is_valid():

            user_form.save()

            messages.info(request, "Update success!")

            return redirect('dashboard')

   

    context = {'user_form':user_form}

    return render(request, 'account/profile-management.html', context=context)


@login_required(login_url='my-login')
def delete_account(request):

    user = User.objects.get(id=request.user.id)

    if request.method == 'POST':

        user.delete()


        messages.error(request, "Account deleted")


        return redirect('store')


    return render(request, 'account/delete-account.html')

@login_required(login_url='my-login')
def dashboard(request):


    return render(request, 'account/dashboard.html')


# Shipping view
@login_required(login_url='my-login')
def manage_shipping(request):

    try:

        # Account user with shipment information

        shipping = ShippingAddress.objects.get(user=request.user.id)


    except ShippingAddress.DoesNotExist:

        # Account user with no shipment information

        shipping = None


    form = ShippingForm(instance=shipping)


    if request.method == 'POST':

        form = ShippingForm(request.POST, instance=shipping)

        if form.is_valid():

            # Assign the user FK on the object

            shipping_user = form.save(commit=False)

            # Adding the FK itself

            shipping_user.user = request.user


            shipping_user.save()

            messages.info(request, "Update success!")

            return redirect('dashboard')


    context = {'form':form}

    return render(request, 'account/manage-shipping.html', context=context)


@login_required(login_url='my-login')
def track_orders(request):
    try:
        orders = OrderItem.objects.filter(user=request.user)
        context = {'orders': orders}
        return render(request, 'account/track-orders.html', context=context)
    except:
        return render(request, 'account/track-orders.html')


def update_status(request, order_item_id):
    if request.method == 'POST':
        status = request.POST.get('status')
        order_item = OrderItem.objects.get(pk=order_item_id)
        order_item.status = status
        order_item.save()
    return redirect('track_order')


def generate_invoice_pdf(request, order_id):
    # Retrieve order details and customer information based on the order_id
    # You can use your models to fetch the data

    # Create a BytesIO buffer to receive the PDF data
    buffer = BytesIO()

    # Create the PDF object, using the BytesIO buffer as its "file"
    p = canvas.Canvas(buffer, pagesize=letter)

    p.drawImage('static/images/favicon.png', 50, 720, width=100, height=50)  # logo

    #thank you message
    p.setFont("Helvetica-Bold", 14)
    p.drawString(100, 500, "Thank You for Your Order!")


    # Set up the content of the invoice
    p.drawString(100, 700, f"Invoice Number/Order ID: #{order_id}")

    # Draw the table headers
    p.setFont("Helvetica-Bold", 12)
    p.drawString(100, 650, "Product Description")
    p.drawString(300, 650, "Price")
    p.drawString(380, 650, "Qty.")
    p.drawString(430, 650, "Total")
    p.drawString(500, 650, "Status")

    # Get all items associated with this order
    orderitems = OrderItem.objects.get(pk=order_id)


    product = orderitems.product
    price = orderitems.price  # Use the price from OrderItem
    quantity = orderitems.quantity
    status = orderitems.status
    total = price * quantity


    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    style = styles["Normal"]
    style.wordWrap = 'CJK'
    product_name = str(product)

    # Initialize the y-coordinate for the table
    y = 630

    # Calculate the maximum number of characters to display on one line
    # Print the total price, quantity, and total in the last row
    p.setFont("Helvetica", 12)
    p.drawString(300, y, f"${price:.2f}")
    p.drawString(380, y, str(quantity))
    p.drawString(430, y, f"${total:.2f}")
    p.drawString(500, y, str(status))
    
# Split the product name into lines with a maximum number of characters per line
    product_name = str(orderitems.product)
    max_chars_per_line = 30  # Adjust this value as needed
    product_lines = [product_name[i:i+max_chars_per_line] for i in range(0, len(product_name), max_chars_per_line)]


    # Iterate through each line of the product name
    for line in product_lines:
        # Print the product details in the table
        p.setFont("Helvetica", 12)
        p.drawString(100, y, line)

        # Move to the next row in the table
        y -= 15

    

    # Add more details here...

    # Save the PDF to the buffer
    p.showPage()
    p.save()


    # Rewind the buffer
    buffer.seek(0)


    # Create an HTTP response with the PDF file
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename=invoice_{order_id}.pdf'
    response.write(buffer.read())

    return response

@login_required(login_url='my-login')
def charts(request):
    if request.user.is_authenticated:

        top_products = (
        OrderItem.objects.values('product__title').annotate(total_quantity=Sum('quantity'))
        .order_by('-total_quantity')[:10]  # Adjust the number as needed
    )

        productnames = [item['product__title'] for item in top_products]
        productquantities = [item['total_quantity'] for item in top_products]

        # Filter OrderItem objects for the logged-in user
        orders = OrderItem.objects.filter(user=request.user)

        # Aggregate the quantity of each product for the filtered orders
        product_quantities = orders.values('product__title').annotate(total_quantity=Sum('quantity'))

        # Extract product names and quantities
        product_names = [item['product__title'] for item in product_quantities]
        quantities = [item['total_quantity'] for item in product_quantities]
        # Get the count of orders in different statuses
        order_statuses = orders.values('status').annotate(status_count=Count('status'))

        context = {
            'product_names': product_names,
            'quantities': quantities,
            'order_status_data': [item['status_count'] for item in order_statuses],
            'productnames': productnames,
            'productquantities': productquantities,
        }

        return render(request, 'account/charts.html', context)
    else:
        # Handle the case where the user is not authenticated, e.g., display an error message or redirect
        # to a login page.
        # You can customize this part based on your application's requirements.
        return render(request, 'account/charts.html')
  