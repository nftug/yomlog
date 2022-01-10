from rest_framework_simplejwt import token_blacklist
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

# Social Login経由で作ったOutstanding Tokenも削除できるようにする
# (https://github.com/jazzband/djangorestframework-simplejwt/issues/266#issuecomment-820745103)


class OutstandingTokenAdmin(token_blacklist.admin.OutstandingTokenAdmin):

    def has_delete_permission(self, *args, **kwargs):
        return True  # or whatever logic you want


admin.site.unregister(token_blacklist.models.OutstandingToken)
admin.site.register(token_blacklist.models.OutstandingToken, OutstandingTokenAdmin)
