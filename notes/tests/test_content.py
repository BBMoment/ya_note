from django.contrib.auth import get_user_model
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note
from notes.tests.fixtures import TestBaseCase

User = get_user_model()


class TestContentPage(TestBaseCase):

    def test_notes_in_list_for_author(self):
        """
        На странице списка заметок отображаются заметки автора
        и нет заметок другого пользователя.
        """
        response = self.auth_client.get(reverse('notes:list'))

        object_list = list(response.context['object_list'])
        notes_list = list(Note.objects.filter(author=self.author1))

        self.assertEqual(notes_list, object_list)

    def test_authorized_client_has_form(self):
        """
        Для авторизованного пользователя доступна
        форма создания и редактирования заметки
        """
        urls = (
            self.edit_url,
            reverse('notes:add'),
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.auth_client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
