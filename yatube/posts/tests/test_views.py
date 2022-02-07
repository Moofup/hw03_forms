from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from django import forms

from ..models import Group, Post

User = get_user_model()


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='Nameless')
        cls.group = Group.objects.create(title='Test-group', slug='t-group', description='test-description')
        for i in range(1, 14):
            cls.post = Post.objects.create(
                text='Тестовый текст' + str(i),
                author=cls.author,
                group=cls.group
            )
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.author)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': 't-group'}): 'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': 'Nameless'}): 'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id': '1'}): 'posts/post_detail.html',
            reverse('posts:post_edit', kwargs={'post_id': '1'}): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_shows_correct_context(self):
        response = self.authorized_client.get(reverse('posts:index'))
        test_object = response.context['page_obj'][0]
        test_title = response.context['title']
        self.assertEqual(test_object, self.post)
        self.assertEqual(test_title, 'Последние обновления на сайте')

    def test_group_list_shows_correct_context(self):
        response = self.authorized_client.get(reverse('posts:group_list', kwargs={'slug': 't-group'}))
        test_object = response.context['page_obj'][0]
        test_title = response.context['title']
        test_group = response.context['group']
        self.assertEqual(test_object, self.post)
        self.assertEqual(test_title, 'Записи сообщества Test-group')
        self.assertEqual(test_group, self.group)

    def test_profile_shows_correct_context(self):
        response = self.authorized_client.get(reverse('posts:profile', kwargs={'username': 'Nameless'}))
        test_object = response.context['page_obj'][0]
        test_title = response.context['title']
        test_author = response.context['author']
        test_post_count = response.context['author_posts_count']
        self.assertEqual(test_object, self.post)
        self.assertEqual(test_title, 'Все посты пользователя Nameless')
        self.assertEqual(test_author, self.author)
        self.assertEqual(test_post_count, self.author.posts.count())

    def test_post_detail_shows_correct_context(self):
        response = self.authorized_client.get(reverse('posts:post_detail', kwargs={'post_id': '13'}))
        test_title = response.context['title']
        test_post = response.context['post']
        test_post_count = response.context['author_posts_count']
        self.assertEqual(test_title, self.post.text)
        self.assertEqual(test_post, self.post)
        self.assertEqual(test_post_count, self.post.author.posts.count())

    def test_edit_post_shows_correct_context(self):
        response = self.authorized_client.get(reverse('posts:post_edit', kwargs={'post_id': '1'}))
        test_is_edit = response.context['is_edit']
        form_fields = {
            'text': forms.fields.CharField,
        }
        form_field = response.context.get('form').fields.get('text')
        self.assertIsInstance(form_field, form_fields['text'])
        self.assertEqual(test_is_edit, True)

    def test_post_create_shows_correct_context(self):
        response = self.authorized_client.get(reverse('posts:post_create'))

        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.MultipleChoiceField,
        }
        form_field = response.context.get('form').fields.get('text')
        self.assertIsInstance(form_field, form_fields['text'])

    class PaginatorViewsTest(TestCase):
        def test_first_page_index_contains_ten_records(self):
            response = self.client.get(reverse('index'))
            self.assertEqual(len(response.context['page_obj']), 10)

        def test_second_page_index_contains_three_records(self):
            response = self.client.get(reverse('index') + '?page=2')
            self.assertEqual(len(response.context['page_obj']), 3)
