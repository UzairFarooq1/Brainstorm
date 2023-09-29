from django.contrib import admin

# Register your models here.
from . models import Category, Product
#Code to pre-populate the slug by the category name and product title 
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    
    prepopulated_fields = {'slug':('name',)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    
    prepopulated_fields = {'slug':('title',)}

