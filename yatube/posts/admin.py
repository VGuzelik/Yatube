from django.contrib import admin

from posts.models import Group, Post, Comment, Follow, PostImage

class PostImageInline(admin.TabularInline):
    model = PostImage

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    # Перечисляем поля, которые должны отображаться в админке
    list_display = (
        'pk',
        'text',
        'author',
        'group',
    )
    list_editable = ('group',)
    search_fields = ('text',)
    empty_value_display = '-пусто-'
    inlines = [
        PostImageInline,
    ]




# проверял  декортатор, тоже самое что
# строка ниже или нет.. оставлю пока строку
# чтоб не потерять, как делать без декортатора)
# admin.site.register(Post, PostAdmin)
admin.site.register(Group)
admin.site.register(Comment)
admin.site.register(Follow)


