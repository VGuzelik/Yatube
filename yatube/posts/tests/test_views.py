# deals/tests/test_views.py
import shutil
import tempfile
from django.core.cache import cache

from django import forms
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.models import Group, Post, User, Comment
from posts.utils import POSTS_PER_PAGE

POSTS_FOR_PAGINATOR_TEST = 13
POSTS_PER_PAGE_SECOND = 3
NUMBER_OF_TEMPLATES = 2

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Thank_you')
        cls.group = Group.objects.create(
            title='Группа',
            slug='slug',
            description='Тестовая группа'
        )
        cls.group_test = Group.objects.create(
            title='Группа без постов',
            slug='any_slug',
            description='Тестовая группа для дополнительного задания'
        )
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=cls.user,
            group=cls.group,
            image=uploaded
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='Тестовый комментарий',
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': self.group.slug}): (
                'posts/group_list.html'
            ),
            reverse('posts:profile', kwargs={'username': self.post.author}): (
                'posts/profile.html'
            ),
            reverse('posts:post_detail', kwargs={'post_id': self.post.pk}): (
                'posts/post_detail.html'
            ),
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}): (
                'posts/create_post.html'
            ),
        }

        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    # Дополнительная проверка при создании поста - в этой функции
    def test_correct_working_context(self):
        """Шаблон index, group_list, profile
        сформированы с правильным контекстом.
        При создании поста, он появляется на этих страницах."""
        list_of_templates = [
            self.authorized_client.get(reverse('posts:index')),
            self.authorized_client.get(
                reverse('posts:group_list', kwargs={'slug': self.group.slug})
            ),
            self.authorized_client.get(
                reverse('posts:profile', kwargs={'username': self.post.author})
            ),
        ]
        for templates in list_of_templates:
            response = templates
            first_object = response.context['page_obj'][0]
            self.assertEqual(first_object.text, self.post.text)
            self.assertEqual(first_object.author, self.post.author)
            self.assertEqual(first_object.group, self.post.group)
            self.assertEqual(first_object.image, self.post.image)

    def test_additional_verification_when_creating_a_post(self):
        """Пост не попадает в группу, для которой не был предназначен."""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group_test.slug})
        )
        post_test_group = response.context.get('page_obj').object_list
        self.assertEqual(post_test_group.count(), 0)

    def test_correct_working_post_detail_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.pk})
        )
        response_context = response.context.get('post')
        self.assertEqual(response_context.text, self.post.text)
        self.assertEqual(response_context.author, self.post.author)
        self.assertEqual(response_context.group, self.post.group)
        self.assertEqual(response_context.image, self.post.image)
        response_context = response.context.get('comments').first()
        self.assertEqual(response_context.id, self.post.pk)
        self.assertEqual(response_context.text, self.comment.text)

    def test_post_create_and_edit_correct_context(self):
        """Шаблоны post_create, post_edit сформированы
        с правильным контекстом."""
        list_of_templates = [
            self.authorized_client.get(reverse('posts:post_create')),
            self.authorized_client.get(
                reverse('posts:post_edit', kwargs={'post_id': self.post.pk})
            )
        ]
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        for templates in list_of_templates:
            response = templates
            for value, expected in form_fields.items():
                with self.subTest(value=value):
                    form_field = response.context.get('form').fields.get(value)
                    self.assertIsInstance(form_field, expected)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Thank_you')
        cls.group = Group.objects.create(
            title='Группа',
            slug='slug',
            description='Тестовая группа'
        )
        cls.posts = [
            Post.objects.bulk_create(
                [
                    Post(
                        text=f'Тестовый пост № {post_number}',
                        author=cls.user,
                        group=cls.group,
                    )
                ]
            ) for post_number in range(POSTS_FOR_PAGINATOR_TEST)
        ]

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_page_contains_ten_records(self):
        list_of_templates = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': self.group.slug}),
            reverse(
                'posts:profile', kwargs={'username': self.user.username}
            ),
        ]
        for template in list_of_templates:
            response = self.authorized_client.get(template)
            self.assertEqual(len(response.context['page_obj']), POSTS_PER_PAGE)
            response = self.authorized_client.get(template + '?page=2')
            self.assertEqual(
                len(response.context['page_obj']), POSTS_PER_PAGE_SECOND
            )


class CacheViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Thank_you')

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.post = Post.objects.create(
            text='Тестовый пост',
            author=self.user
        )
        cache.clear()

    def test_cache(self):
        """Проверка кэша для index."""
        response = self.authorized_client.get(reverse('posts:index'))
        index_hashed = response.content
        Post.objects.all().delete()
        response_hashed = self.authorized_client.get(reverse('posts:index'))
        index_comparison = response_hashed.content
        self.assertEqual(index_hashed, index_comparison)
        cache.clear()
        response = self.authorized_client.get(reverse('posts:index'))
        index_updated = response.content
        self.assertNotEqual(index_comparison, index_updated)


class FollowViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.first_user = User.objects.create_user(username='first_user')
        cls.second_user = User.objects.create_user(username='second_user')
        cls.third_user = User.objects.create_user(username='third_user')
        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=cls.second_user
        )

    def setUp(self):
        self.authorized_client_1 = Client()
        self.authorized_client_2 = Client()
        self.authorized_client_3 = Client()
        self.guest_client = Client()
        self.authorized_client_1.force_login(self.first_user)
        self.authorized_client_2.force_login(self.second_user)
        self.authorized_client_3.force_login(self.third_user)

    def test_subscribe_to_other_users_and_remove_them(self):
        """Авторизованный пользователь может подписаться на автора
        и отписаться от него."""
        count_follow = self.second_user.following.count()
        response = self.authorized_client_1.get(
            reverse(
                'posts:profile_follow', kwargs={'username': self.second_user}
            )
        )
        self.assertRedirects(
            response,
            reverse('posts:profile', kwargs={'username': self.second_user})
        )
        self.assertEqual(
            self.second_user.following.count(), count_follow + 1)

        response = self.authorized_client_1.get(
            reverse(
                'posts:profile_unfollow', kwargs={'username': self.second_user}
            )
        )
        self.assertRedirects(
            response,
            reverse('posts:profile', kwargs={'username': self.second_user})
        )
        self.assertEqual(self.second_user.following.count(), count_follow)

    def test_subscribe_to_other_users_not_authorized_client(self):
        """Не авторизованный пользователь не может
        подписаться на автора поста."""
        count_follow = self.second_user.following.count()
        self.guest_client.get(
            reverse(
                'posts:profile_follow', kwargs={'username': self.second_user}
            )
        )
        self.assertEqual(self.second_user.following.count(), count_follow)

    def test_follow_index(self):
        """Новая запись пользователя появляется в ленте тех,
        кто на него подписан и не появляется в ленте тех, кто не подписан."""
        count_post_first_user_before = Post.objects.filter(
            author__following__user=self.first_user
        ).count()
        count_post_third_user_before = Post.objects.filter(
            author__following__user=self.third_user
        ).count()
        self.authorized_client_1.get(
            reverse(
                'posts:profile_follow', kwargs={'username': self.second_user}
            )
        )
        count_post_first_user_after = Post.objects.filter(
            author__following__user=self.first_user
        ).count()
        count_post_third_user_after = Post.objects.filter(
            author__following__user=self.third_user
        ).count()
        self.assertEqual(
            count_post_first_user_after, count_post_first_user_before + 1
        )
        self.assertEqual(
            count_post_third_user_after, count_post_third_user_before
        )
