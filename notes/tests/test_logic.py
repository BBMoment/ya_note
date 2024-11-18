from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.urls import reverse
from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note
from notes.tests.fixtures import TestBaseCase

User = get_user_model()


class TestNoteCreation(TestBaseCase):

    def test_create_note(self):
        """
        Авторизованный пользователь может создать заметку,
        а анонимный - нет.
        """
        clients = (
            (self.client, self.START_NOTES_COUNT),
            (self.auth_client, self.START_NOTES_COUNT + 1),
        )
        for client, result in clients:
            with self.subTest(client=client):
                client.post(reverse('notes:add'), data=self.form_data)
                notes_count = Note.objects.count()
                self.assertEqual(notes_count, result)

    def test_not_unique_slug(self):
        """Проверка на уникальность slug при создании заметок."""
        form_data = self.form_data
        form_data['slug'] = self.note.slug
        response = self.auth_client.post(reverse('notes:add'), data=form_data)

        self.assertFormError(
            response,
            'form',
            'slug',
            errors=(self.note.slug + WARNING)
        )
        assert Note.objects.count() == self.START_NOTES_COUNT

    def test_empty_slug_in_note(self):
        """Проверка на автоформирование slug при пустом в форме."""
        form_data = self.form_data
        form_data.pop('slug')
        slug = slugify(form_data['title'])[:self.SLUG_MAX_LENGHT]

        self.auth_client.post(reverse('notes:add'), data=form_data)

        note = Note.objects.get(pk=self.START_NOTES_COUNT + 1)
        self.assertEqual(note.slug, slug)


class TestCommentEditDelete(TestBaseCase):

    def test_author_can_delete_comment(self):
        """Автор заметки может удалить ее."""
        response = self.auth_client.delete(self.delete_url)
        self.assertRedirects(response, self.redir_delete_url)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, self.START_NOTES_COUNT - 1)

    def test_author_can_edit_comment(self):
        """Автор заметки может отредактировать ее."""
        response = self.auth_client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, self.redir_edit_url)
        note = Note.objects.get(pk=1)
        self.assertEqual(note.text, self.NEW_NOTE_TEXT)
        self.assertEqual(note.title, self.NEW_NOTE_TITLE)
        self.assertEqual(note.slug, self.NEW_NOTE_SLUG)

    def test_user_cant_delete_comment_of_another_user(self):
        """Пользователь не может удалять чужие заметки."""
        response = self.reader_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        comments_count = Note.objects.count()
        self.assertEqual(comments_count, self.START_NOTES_COUNT)

    def test_user_cant_edit_comment_of_another_user(self):
        """Пользователь не может редактировать чужие заметки."""
        response = self.reader_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note = Note.objects.get(pk=1)
        self.assertNotEqual(note.text, self.NEW_NOTE_TEXT)
        self.assertNotEqual(note.title, self.NEW_NOTE_TITLE)
        self.assertNotEqual(note.slug, self.NEW_NOTE_SLUG)
