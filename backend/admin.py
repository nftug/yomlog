from django.contrib import admin

from .models import *

admin.site.register(BookOrigin)
admin.site.register(BookCopy)
admin.site.register(Note)
admin.site.register(StatusLog)

admin.site.register(CustomUser)
