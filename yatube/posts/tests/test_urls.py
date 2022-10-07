from http import HTTPStatus
from django.urls import reverse

from django.contrib.auth import get_user_model
from django.test import TestCase, Client

from ..models import Group, Post

User = get_user_model()


class PostsURLTests(TestCase):

    @classmethod
    def setUpClass(cls):
        """ Создаем тестовые экземпляры постов."""
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.non_auth = User.objects.create_user(username='nonauth')
        cls.group = Group.objects.create(
            title='group',
            slug='slug',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='тестовый текст поста',
            group=cls.group,
        )

    def setUp(self):
        """Создаем авторизованного и неавторизованного клиента"""
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.non_auth)
        self.author_client = Client()
        self.author_client.force_login(self.user)

    def test_urls_guest(self):
        """Страница доступна любому пользователю."""
        urls = (reverse('posts:index'),
                reverse('posts:postsname',
                        kwargs={'slug': self.group.slug}),
                reverse('posts:profile',
                        kwargs={'username': self.user.username}),
                reverse('posts:post_detail', args=[self.post.id]),
                )
        for url in urls:
            with self.subTest():
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK.value)
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND.value)

    def test_url_post_create(self):
        """Страница create доступна только авторизованному пользователю."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        self.assertEqual(response.status_code, HTTPStatus.OK.value)

    def test_url_post_edit(self):
        """Страница create доступна только автору поста."""
        response = self.author_client.get(
            reverse('posts:post_edit',
                    kwargs={'post_id': f'{self.post.id}'})
        )
        self.assertEqual(response.status_code, HTTPStatus.OK.value)

    def test_url_redirect_anonymous(self):
        """Страница перенаправит пользователся на login"""
        url_templates_names = {
            "/create/": "/auth/login/?next=/create/",
            "/posts/1/edit/": "/auth/login/?next=/posts/1/edit/",
        }
        for address, template in url_templates_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.FOUND)
                self.assertRedirects(response, template)

    def test_url_redirect_authorized_client_post_edit(self):
        """Перенаправление пользователя на post detail"""
        response = self.authorized_client.get(
            f'/posts/{self.post.pk}/edit/', follow=True
        )
        self.assertRedirects(response,
                             f'/posts/{self.post.pk}/'
                             )

    def test_reddirect_guest_client(self):
        """Проверка редиректа неавторизованного пользователя"""
        self.post = Post.objects.create(text='Тестовый текст',
                                        author=self.user,
                                        group=self.group)
        form_data = {'text': 'Текст записанный в форму'}
        response = self.guest_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(response,
                             f'/auth/login/?next=/posts/{self.post.id}/edit/')

    def test_urls_templates(self):
        """Тест на соотвецтвие адресов и шаблонов"""
        urls_templates = {
            'posts/index.html': '/',
            'posts/group_list.html': reverse('posts:postsname',
                                             kwargs={'slug': self.group.slug}),
            'posts/profile.html': reverse('posts:profile',
                                          kwargs={
                                              'username': self.user.username}),
            'posts/post_detail.html': reverse('posts:post_detail',
                                              kwargs={
                                                  'post_id': self.post.id}),
            'posts/create_post.html': reverse('posts:post_edit',
                                              kwargs={
                                                  'post_id': self.post.id}),
        }
        for template, address in urls_templates.items():
            with self.subTest(address=address):
                response = self.author_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_noname_user_create_post(self):
        """ Проверка создания записи не авторизированным пользователем ."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'тестовый текст',
            'group': self.group.id,
        }
        response = self.guest_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(Post.objects.count(), posts_count)

    def test_url_comment(self):
        """Страница comment доступна только авторизованному пользователю."""
        response = self.guest_client.get(
            reverse('posts:add_comment',
                    kwargs={'post_id': f'{self.post.id}'})
        )
        self.assertEqual(response.status_code, 302)
