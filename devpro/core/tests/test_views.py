from http import HTTPStatus

import pytest
from django.shortcuts import resolve_url

from devpro.core.models import Author, Book

list_author_url = resolve_url('core:list-authors')
pytestmark = pytest.mark.django_db
CT_JSON = 'application/json'


@pytest.fixture
def book(db):
    author = Author.objects.create(name='Luciano Ramalho')
    book = Book.objects.create(
        name='Python Fluente',
        edition=2,
        publication_year=2022,
    )
    book.authors.set([author])
    return book


def test_list_all_authors(client):
    authors = Author.objects.bulk_create(Author(name=f'Author {i}') for i in range(10))

    response = client.get(list_author_url, data={'page': 2, 'page_size': 5})

    assert response.status_code == HTTPStatus.OK
    assert [a['name'] for a in response.json()['data']] == [a.name for a in authors[5:]]
    assert response.json()['num_pages'] == 2


def test_search_author_by_name(client):
    autor_1 = Author.objects.create(name='J.K Rowling')
    Author.objects.create(name='David Beazley')
    response = client.get(list_author_url, data={'name': 'rowling'})

    assert response.status_code == HTTPStatus.OK
    assert response.json()['data'] == [{'id': autor_1.id, 'name': 'J.K Rowling'}]


def test_search_author_by_name_without_match(client):
    Author.objects.create(name='David Beazley')
    response = client.get(list_author_url, data={'name': 'no match'})

    assert response.status_code == HTTPStatus.OK
    assert response.json()['data'] == []


def test_create_book(client):
    author = Author.objects.create(name='Luciano Ramalho')
    data = {
        "name": 'Python fluente',
        "edition": 2,
        "publication_year": 2022,
        "authors": [author.id]
    }
    response = client.post('/api/books/', data=data, content_type=CT_JSON)

    assert response.status_code == HTTPStatus.CREATED
    response_data = response.json()
    assert response_data['edition'] == 2
    assert response_data['name'] == 'Python fluente'
    assert response_data['publication_year'] == 2022
    assert response_data['authors'] == [author.id]


def test_read_book(client, book):
    response = client.get(f'/api/books/{book.id}/')

    assert response.json() == book.to_dict()
    assert response.status_code == HTTPStatus.OK


def test_read_unixist_book(client):
    response = client.get('/api/books/10/')

    assert response.status_code == HTTPStatus.NOT_FOUND


def test_update_book(client, book):
    author_2 = Author.objects.create(name='Renzo')
    data = {
        "id": book.id,
        "name": 'Python Fluente',
        "edition": 2,
        "publication_year": 2022,
        "authors": [author_2.pk]
    }
    response = client.put(f'/api/books/{book.id}/', data=data, content_type=CT_JSON)

    assert response.status_code == HTTPStatus.OK
    assert response.json() == data


def test_put_unixist_book(client):
    response = client.put('/api/books/10/', content_type=CT_JSON)

    assert response.status_code == HTTPStatus.NOT_FOUND


def test_delete_book(client, book):
    response = client.delete(f'/api/books/{book.id}/')

    assert response.status_code == HTTPStatus.NO_CONTENT
    assert Book.objects.filter(pk=book.id).exists()


def test_delete_unixist_book(client):
    response = client.delete('/api/books/10/', content_type=CT_JSON)

    assert response.status_code == HTTPStatus.NOT_FOUND


def test_list_books(client, book):
    response = client.get('/api/books/')

    assert response.status_code == HTTPStatus.OK
    assert response.json()['data'] == [book.to_dict()]


def test_list_books_filter_by_publication_year(client, book):
    book_2 = Book.objects.create(
        name='Python cockbook',
        edition=2,
        publication_year=2016,
    )
    book_2.authors.add(Author.objects.create(name='David Beazley'))

    response = client.get('/api/books/', data={'publication_year': book.publication_year})

    assert response.status_code == HTTPStatus.OK
    assert response.json()['data'] == [book.to_dict()]


def test_list_books_filter_by_author(client, book):
    author = Author.objects.create(name='David Beazley')
    book_2 = Book.objects.create(
        name='Python cockbook',
        edition=2,
        publication_year=2016,
    )
    book_2.authors.add(author)

    response = client.get('/api/books/', data={'author': author.id})

    assert response.status_code == HTTPStatus.OK
    assert response.json()['data'] == [book_2.to_dict()]


def test_list_books_filter_by_author_and_publication_year(client, book):
    author = Author.objects.create(name='David Beazley')
    book_2 = Book.objects.create(
        name='Python Cockbook',
        edition=2,
        publication_year=2016,
    )
    book_2.authors.add(author)

    response = client.get('/api/books/', data={'author': author.id, 'publication_year': book.publication_year})

    assert response.status_code == HTTPStatus.OK
    assert response.json()['data'] == [book_2.to_dict(), book.to_dict()]
