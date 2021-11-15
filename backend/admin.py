from django.contrib import admin

from .models import Book, CustomUser

admin.site.register(Book)
admin.site.register(CustomUser)
