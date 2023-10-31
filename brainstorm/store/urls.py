from django.urls import path, include

from . import views

urlpatterns = [

    path('', views.store, name='store'),

    path('product/<slug:product_slug>/', views.product_info, name='product-info'),

    path('search/<slug:category_slug>/', views.list_category, name='list-category'),

    path('search/', views.search, name='product-search'),
    
    path('add_review/<slug:product_slug>/', views.add_review, name='add_review'),

    path('store/', views.store, name='store'),

]