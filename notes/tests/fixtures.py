from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestBaseCase(TestCase):

    USER_NOTES_ON_PAGE = 10
    USER_NOTES_COUNT = USER_NOTES_ON_PAGE + 1
    START_NOTES_COUNT = USER_NOTES_COUNT * 2
    SLUG_MAX_LENGHT = Note._meta.get_field('slug').max_length

    NEW_NOTE_TEXT = 'new text'
    NEW_NOTE_TITLE = 'new title'
    NEW_NOTE_SLUG = 'new_slug'

    @classmethod
    def setUpTestData(cls):
        # Пользователи
        cls.author1 = User.objects.create(username='author1')
        cls.author2 = User.objects.create(username='author2')

        # Заметки
        notes = []
        for index in range(cls.USER_NOTES_COUNT):
            for author in (cls.author1, cls.author2):
                note = Note(
                    title='title',
                    text='text',
                    slug=f'{author.username}_{index}',
                    author=author
                )
                notes.append(note)
        Note.objects.bulk_create(notes)

        # Заметка от author1
        cls.note = notes[0]

        # Клиенты
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.author1)

        cls.reader_client = Client()
        cls.reader_client.force_login(cls.author2)

        # Адреса urls
        cls.note_url = reverse('notes:detail', args=(cls.note.slug,))

        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.redir_edit_url = reverse('notes:success')

        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.redir_delete_url = reverse('notes:success')

        # Формы
        cls.form_data = {
            'text': cls.NEW_NOTE_TEXT,
            'title': cls.NEW_NOTE_TITLE,
            'slug': cls.NEW_NOTE_SLUG,
        }
