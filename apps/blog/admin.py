from django.contrib import admin
from .models import Post,Category
# Register your models here.


@admin.register(Post)
class AdminPost(admin.ModelAdmin):
    prepopulated_fields = {'slug':('title',)}
    ordering = ['-published']


admin.site.register(Category)


