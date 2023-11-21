from rest_framework.test import APITestCase
from rest_framework import status
from .models import Book, CustomUser


class BookAPITests(APITestCase):
    def setUp(self):
        # Create a test user
        self.user = CustomUser.objects.create_user(username='testuser', password='testpassword')

        # Create a test book
        self.book = Book.objects.create(
            title='Test Book',
            author='Test Author',
            isbn='1234567890',
            user=self.user
        )

    def test_list_books_authenticated(self):
        # Ensure the endpoint requires authentication
        response = self.client.get('/api/books/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Authenticate the user
        self.client.force_authenticate(user=self.user)

        # Test listing books for the authenticated user
        response = self.client.get('/api/books/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 1)
        self.assertEqual(response.data["results"][0]['title'], 'Test Book')

    def test_create_book_authenticated(self):
        # Ensure the endpoint requires authentication
        response = self.client.post('/api/books/', data={'title': 'New Book', 'isbn': '9876543210'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Authenticate the user
        self.client.force_authenticate(user=self.user)

        # Test creating a new book for the authenticated user
        response = self.client.post('/api/books/', data={'title': 'New Book', 'isbn': '9876543210'})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Book.objects.count(), 2)

    def test_view_book_authenticated(self):
        # Ensure the endpoint requires authentication
        response = self.client.get(f'/api/books/{self.book.id}/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Authenticate the user
        self.client.force_authenticate(user=self.user)

        # Test viewing details of a book for the authenticated user
        response = self.client.get(f'/api/books/{self.book.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Book')

    def test_update_book_authenticated(self):
        # Ensure the endpoint requires authentication
        response = self.client.put(f'/api/books/{self.book.id}/', data={
            'title': 'Updated Book',
            'author': 'Test Author',
            'isbn': '1234567890',
            'user': self.user.pk})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Authenticate the user
        self.client.force_authenticate(user=self.user)

        # Test updating details of a book for the authenticated user
        response = self.client.put(f'/api/books/{self.book.id}/', data={
            'title': 'Updated Book',
            'author': 'Test Author',
            'isbn': '1234567890',
            'user': self.user.pk})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Book.objects.get(id=self.book.id).title, 'Updated Book')

    def test_delete_book_authenticated(self):
        # Ensure the endpoint requires authentication
        response = self.client.delete(f'/api/books/{self.book.id}/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Authenticate the user
        self.client.force_authenticate(user=self.user)

        # Test deleting a book for the authenticated user
        response = self.client.delete(f'/api/books/{self.book.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Book.objects.count(), 0)

    def test_authentication_required(self):
        # Test that authentication is required for all endpoints
        endpoints = ['/api/books/', f'/api/books/{self.book.id}/', '/api/books/', '/api/books/', '/api/books/']
        for endpoint in endpoints:
            response = self.client.get(endpoint)
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
