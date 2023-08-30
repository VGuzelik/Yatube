import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from posts.forms import PostForm, CommentForm
from posts.models import Post, Group, User, Comment
from django.test import Client, TestCase, override_settings
from django.urls import reverse

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.form = PostForm()
        cls.user = User.objects.create_user(username='Thank_you')
        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=cls.user
        )
        cls.group = Group.objects.create(
            title='Тест_группа',
            slug='slug'
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post_without_group(self):
        """Валидная форма, без поля группы, создает запись в Post."""
        post_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый пост 2',
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:profile', kwargs={'username': self.user})
        )
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text=form_data['text'],
            ).exists()
        )

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        post_count = Post.objects.count()
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
            content_type='image/gif',
        )
        form_data = {
            'text': 'Тестовый пост 2',
            'group': self.group.id,
            'image': uploaded
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:profile', kwargs={'username': self.user})
        )
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text=form_data['text'],
                group=self.group,
                image='posts/small.gif'
            ).exists()
        )

    def test_create_post_no_valid_form(self):
        """Не валидная форма не создает запись в Post."""
        post_count = Post.objects.count()
        form_data = {
            'text': '',
        }
        self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), post_count)

    def test_post_edit(self):
        """Автор поста редактуриет запись в Post."""
        form_data = {
            'text': 'Тестовый пост  - редактированный',
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:post_detail', kwargs={'post_id': self.post.pk})
        )
        self.assertTrue(
            Post.objects.filter(
                text=form_data['text'],
            ).exists()
        )

    def test_post_edit_group(self):
        """Автор поста редактуриет группу поста в Post."""
        form_data = {
            'text': self.post.text,
            'group': self.group.id
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:post_detail', kwargs={'post_id': self.post.pk})
        )
        self.assertTrue(
            Post.objects.filter(
                text=form_data['text'],
                group=form_data['group']
            ).exists()
        )


class CommentCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.form = CommentForm()
        cls.user = User.objects.create_user(username='Thank_you')
        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=cls.user
        )
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

    def test_create_comment_no_valid_form(self):
        """Не валидная форма не создает коментарий."""
        first_post = Post.objects.first()
        comment_count = first_post.comments.count()
        form_data = {
            'text': '',
        }
        self.authorized_client.post(
            reverse(
                'posts:add_comment', kwargs={'post_id': first_post.pk}
            ),
            data=form_data,
            follow=True
        )
        self.assertEqual(first_post.comments.count(), comment_count)

    def test_create_comment_no_authorized_client(self):
        """Не авторизованный клиент не создает коментарий."""
        first_post = Post.objects.first()
        comment_count = first_post.comments.count()
        form_data = {
            'text': 'Тестовый текст',
        }
        self.guest_client.post(
            reverse(
                'posts:add_comment', kwargs={'post_id': first_post.pk}
            ),
            data=form_data,
            follow=True
        )
        self.assertEqual(first_post.comments.count(), comment_count)

    def test_create_comment(self):
        """Валидная форма создает комментарий."""
        first_post = Post.objects.first()
        comment_count = first_post.comments.count()
        form_data = {
            'text': 'Тестовый комментарий',
        }
        response = self.authorized_client.post(
            reverse(
                'posts:add_comment', kwargs={'post_id': first_post.pk}
            ),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:post_detail', kwargs={'post_id': first_post.pk})
        )
        self.assertEqual(first_post.comments.count(), comment_count + 1)
        self.assertTrue(
            Comment.objects.filter(
                post=first_post,
                text=form_data['text']
            ).exists()
        )
