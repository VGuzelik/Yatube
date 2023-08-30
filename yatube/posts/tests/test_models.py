from django.test import TestCase

from ..models import Comment, Follow, Group, Post, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=cls.user
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        group = self.group
        post = self.post
        expected_object_name_group = group.title
        expected_object_name_post = post.text[:15]
        self.assertEqual(expected_object_name_group, str(group))
        self.assertEqual(expected_object_name_post, str(post))

    def test_verbose_name_group(self):
        """verbose_name в полях совпадает с ожидаемым."""
        group = self.group
        field_verboses = {
            'title': 'Название',
            'slug': 'Уникальный адрес',
            'description': 'Описание',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    group._meta.get_field(value).verbose_name, expected)

    def test_verbose_name_post(self):
        """verbose_name в полях совпадает с ожидаемым."""
        post = self.post
        field_verboses = {
            'text': 'Текст поста',
            'author': 'Автор',
            'group': 'Группа',
            'image': 'Картинка'
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).verbose_name, expected)

    def test_help_text_post(self):
        post = self.post
        field_help_text = {
            'text': 'Текст нового поста',
            'group': 'Группа, к которой будет относиться пост',
            'image': 'Загрузите картинку'
        }
        for value, expected in field_help_text.items():
            with self.subTest(value=value):
                self.assertEqual(
                    post._meta.get_field(value).help_text, expected)


class CommentModelTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='1')
        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=cls.user
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            text='Тестовый комментарий',
            author=cls.user
        )

    def test_help_text(self):
        comment = self.comment
        help_text = comment._meta.get_field('text').help_text
        self.assertEqual(help_text, 'Введите текст')


class FollowModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='first')
        cls.user_second = User.objects.create_user(username='second')
        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=cls.user
        )
        cls.follow = Follow.objects.create(
            user=cls.user_second,
            author=cls.post.author
        )

    def test_verbose_name_follow(self):
        """verbose_name в полях совпадает с ожидаемым."""
        follow = self.follow
        field_verboses = {
            'user': 'Подписчик',
            'author': 'Автор',
        }
        for value, expected in field_verboses.items():
            with self.subTest(value=value):
                self.assertEqual(
                    follow._meta.get_field(value).verbose_name, expected)
