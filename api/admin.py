from django.contrib import admin
from .models import Book, Order, BookImage


# Register your models here.
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'author_name', 'hello', 'ID']


# Register your models here.
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'ordered_price', 'hello']


@admin.register(BookImage)
class BookImageAdmin(admin.ModelAdmin):
    list_display = ['__str__']
