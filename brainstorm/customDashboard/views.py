# Create your views here.
from django.contrib.admin.views.decorators import staff_member_required

from django.shortcuts import render
from django.db.models import Sum, Count
from django.db.models.functions import TruncDay
from django.db.models.functions import TruncMonth
from payment.models import Order, OrderItem
from store.models import Product, Review 
from django.shortcuts import redirect
from django.contrib.auth.models import User
from django.db.models import Avg





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
    product_ratings.append({'product': product.title, 'rating': avg_rating})

   
   context = {
        'labels': labels,
        'data': data,

        'status_distribution': status_distribution,

        'staff_count': staff_count,
        'non_staff_count': non_staff_count,

        'labelsaov': labelsaov,
        'dataaov': dataaov,

        'product_ratings': product_ratings,
    }
   
   return render(request, 'customDashboard/admin_dashboard.html', context)

