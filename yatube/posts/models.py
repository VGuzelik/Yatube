from django.contrib.auth import get_user_model
from django.db import models

from django.db.models.constraints import UniqueConstraint

User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        'Название',
        max_length=200
    )
    slug = models.SlugField(
        'Уникальный адрес',
        unique=True
    )
    description = models.TextField('Описание')

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'

    def __str__(self):
        return self.title


class PostImage(models.Model):
    post = models.ForeignKey(
        'Post',
        on_delete=models.CASCADE,
        related_name='image'
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True,
        null=True,
        help_text='Загрузите картинку'
    )


class Post(models.Model):
    text = models.TextField('Текст поста', help_text='Текст нового поста')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор'
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='posts',
        verbose_name='Группа',
        help_text='Группа, к которой будет относиться пост',
    )
    created = models.DateTimeField(
        'Дата создания',
        auto_now_add=True,
        db_index=True
    )


    class Meta:
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='коментарий к посту',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор коментария'
    )
    text = models.TextField(
        'Текст коментария',
        help_text='Введите текст'
    )
    created = models.DateTimeField(
        'Дата создания',
        auto_now_add=True,
        db_index=True
    )


    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text[:15]


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик'

    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор'
    )

    class Meta:
        verbose_name = 'Подписка на автора'
        verbose_name_plural = 'Подписки на авторов'
        UniqueConstraint(fields=['user', 'author'], name='unique_follower')

    def __str__(self):
        return f'{self.author}'
