from django.contrib import admin

from .models import *

admin.site.register(Book)
admin.site.register(Note)
admin.site.register(StatusLog)

admin.site.register(CustomUser)
