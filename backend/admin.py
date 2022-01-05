from django.contrib import admin

from backend.models import Author, Book, StatusLog, Note, BookAuthorRelation, CustomUser


class BookAuthorRelationInline(admin.TabularInline):
    model = BookAuthorRelation
    extra = 1


class BookAuthorRelationAdmin(admin.ModelAdmin):
    inlines = (BookAuthorRelationInline,)


admin.site.register(Book, BookAuthorRelationAdmin)
admin.site.register(Note)
admin.site.register(StatusLog)
admin.site.register(Author)

admin.site.register(CustomUser)
