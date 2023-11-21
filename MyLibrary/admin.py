from django.contrib import admin

from MyLibrary.models import CustomUser, Book


# Register your models here.
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'bio')


class BookAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'author', 'isbn', 'publication_date')


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Book, BookAdmin)
