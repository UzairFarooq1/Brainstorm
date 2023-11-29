# Create your views here.
from django.contrib.admin.views.decorators import staff_member_required

from django.shortcuts import render
from django.db.models import Sum, Count
from django.db.models.functions import TruncDay
from django.db.models.functions import TruncMonth
from payment.models import Order, OrderItem
from store.models import Product, Review , Category
from cart.models import Rule
from django.shortcuts import redirect
from django.contrib.auth.models import User
from django.db.models import Avg, Max
import json
from django.db.models import F, ExpressionWrapper, FloatField





def admin_dashboard(request):
    # Add any code for your admin dashboard here
    return redirect('admin:index') 

@staff_member_required
def admin_dashboard(request):
   #sales trends
   daily_sales = Order.objects.annotate(day=TruncDay('date_ordered')).values('day').annotate(total_sales=Sum('amount_paid')).order_by('day')
   labels = [order['day'].strftime('%Y-%m-%d') for order in daily_sales]
   data = [float(order['total_sales']) for order in daily_sales]


   #delivery status       
   status_distribution = OrderItem.objects.values('status').annotate(order_count=Count('status'))

   #user
   staff_count = User.objects.filter(is_staff=True).count()
   non_staff_count = User.objects.filter(is_staff=False).count()

   #avg order value
   aov_data = Order.objects.annotate(month=TruncMonth('date_ordered')).values('month').annotate(aov=Avg('amount_paid')).order_by('month')
   labelsaov = [order['month'].strftime('%b %Y') for order in aov_data]
   dataaov = [order['aov'] for order in aov_data]


   #avg review
   products = Product.objects.all()
   
   product_ratings = []
   for product in products:
    avg_rating = Review.objects.filter(product=product).aggregate(avg_rating=Avg('rating'))['avg_rating']
    if avg_rating is not None:
       product_ratings.append({'product': product.title, 'rating': avg_rating})
    else:
       product_ratings.append({'product': product.title, 'rating': 0})

    #category sales
    categories = Category.objects.all()
    category_data = []

    for category in categories:
        total_products = Product.objects.filter(category=category).count()
        category_data.append({
            'name': category.name,
            'total_products': total_products,
        })


    #product price vs revenue
    product_data = (
    OrderItem.objects
    .values('product__title', 'product__price')
    .annotate(total_revenue=Sum(F('product__price') * F('quantity')))
    .order_by('product__title')
)

# Convert Decimal values to float
    product_data = [
    {
        'product_name': item['product__title'],
        'product_price': float(item['product__price']),
        'total_revenue': float(item['total_revenue'])
    }
    for item in product_data
]

    product_data_json = json.dumps(list(product_data))

    total_sales = Order.objects.aggregate(total_sales=Sum('amount_paid'))['total_sales']
    total_sales = round(total_sales, -2)
    total_orders = Order.objects.count()
    average_reviews = Review.objects.aggregate(avg_reviews=Avg('rating'))['avg_reviews']
    total_users = User.objects.count()


   
   context = {
        'labels': labels,
        'data': data,

        'status_distribution': status_distribution,

        'staff_count': staff_count,
        'non_staff_count': non_staff_count,

        'labelsaov': labelsaov,
        'dataaov': dataaov,

        'product_ratings': product_ratings,

        'category_data': category_data,

        'product_data_json': product_data_json,
        'total_sales': total_sales,
        'total_orders': total_orders,
        'average_reviews': average_reviews,
        'total_users': total_users,

    }
   
   return render(request, 'customDashboard/admin_dashboard.html', context)

