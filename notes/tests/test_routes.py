from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.urls import reverse

from notes.tests.fixtures import TestBaseCase

User = get_user_model()


class TestRoutes(TestBaseCase):

    def test_pages_availability(self):
        """Основные страницы доступны анонимному пользователю."""
        urls = (
            'notes:home',
            'users:login',
            'users:logout',
            'users:signup',
        )
        for name in urls:
            with self.subTest(name=name):
                response = self.client.get(reverse(name))
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_authenticated_user(self):
        """Основные страницы доступны авторизованному пользователю."""
        urls = (
            'notes:home',
            'notes:success',
            'notes:list',
            'notes:add',
            'users:login',
            'users:logout',
            'users:signup',
        )
        for name in urls:
            with self.subTest(name=name):
                response = self.auth_client.get(reverse(name))
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_availability_for_note_edit_and_delete(self):
        """
        Страница заметки, редактирования и удаления заметки
        доступны только автору.
        """
        users_statuses = (
            (self.auth_client, HTTPStatus.OK),
            (self.reader_client, HTTPStatus.NOT_FOUND),
        )
        urls = (
            self.edit_url,
            self.delete_url,
            self.note_url,
        )
        for client, status in users_statuses:
            for url in urls:
                with self.subTest(client=client, url=url):
                    response = client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_redirect_for_anonymous_client(self):
        """Редирект анонимного пользователя на страницу входа."""
        login_url = reverse('users:login')
        urls = (
            reverse('notes:list'),
            reverse('notes:success'),
            reverse('notes:add'),
            self.note_url,
            self.edit_url,
            self.delete_url,
        )
        for url in urls:
            with self.subTest(url=url):
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
