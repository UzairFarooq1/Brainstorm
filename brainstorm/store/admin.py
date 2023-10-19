from django.contrib import admin

# Register your models here.
from . models import Category, Product, Review
#Code to pre-populate the slug by the category name and product title 
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    
    prepopulated_fields = {'slug':('name',)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    
    prepopulated_fields = {'slug':('title',)}


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'rating', 'comment', 'created_at')
    list_filter = ('product',)
    search_fields = ('user__username', 'product__title', 'comment')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
