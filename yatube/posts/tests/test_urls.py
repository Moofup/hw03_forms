from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client

from ..models import Group, Post

User = get_user_model()


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_homepage(self):
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_author(self):
        response = self.guest_client.get('/about/author/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_tech(self):
        response = self.guest_client.get('/about/tech/')
        self.assertEqual(response.status_code, HTTPStatus.OK)


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='Nameless')
        cls.group = Group.objects.create(title='Test-group', slug='t-group', description='test-description')
        cls.post = Post.objects.create(
            text='Тестовый заголовок',
            author=cls.author,
        )
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.author)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names_guest = {
            '/': 'posts/index.html',
            '/group/t-group/': 'posts/group_list.html',
            '/profile/Nameless/': 'posts/profile.html',
            '/posts/1/': 'posts/post_detail.html',
            '/unexisting_page/': 'lol.html',
        }
        for address, template in templates_url_names_guest.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                if address == '/unexisting_page/':
                    self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
                else:
                    self.assertEqual(response.status_code, HTTPStatus.OK)

        templates_url_names_authorized = {
            '/': 'posts/index.html',
            '/group/t-group/': 'posts/group_list.html',
            '/profile/Nameless/': 'posts/profile.html',
            '/posts/1/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
            '/posts/1/edit/': 'posts/create_post.html',
        }
        for address, template in templates_url_names_authorized.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                if address == '/unexisting_page/':
                    self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
                else:
                    self.assertEqual(response.status_code, HTTPStatus.OK)
