from rest_framework import generics, permissions, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from .models import Book
from .serializers import BookSerializer
import requests
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response


class CustomAuthToken(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        print(user)
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email
        })


class CustomPageNumberPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class BookListCreateView(generics.ListCreateAPIView):
    """
    API endpoint for listing and creating books.
    """
    queryset = Book.objects.select_related('user')
    serializer_class = BookSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        """
        Retrieve a list of books for the current user.
        """
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        """
        Create a new book associated with the current user.
        """
        serializer.save(user=self.request.user)

    def list(self, request, *args, **kwargs):
        """
        List books for the current user.
        """
        try:
            return super().list(request, *args, **kwargs)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create(self, request, *args, **kwargs):
        """
        Create a new book by providing ISBN.
        """
        isbn = request.data.get('isbn')

        if not isbn:
            return Response({'error': 'ISBN is required'}, status=status.HTTP_400_BAD_REQUEST)

        book_data = self.fetch_book_details(isbn, request.user)

        if not book_data:
            return Response({'error': 'Book details not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(data=book_data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def fetch_book_details(self, isbn, user):
        """
        Fetch book details from the Open Library API based on ISBN.
        """
        open_library_url = f'https://openlibrary.org/api/books?bibkeys=ISBN:{isbn}&format=json&jscmd=data'

        try:
            response = requests.get(open_library_url)
            response.raise_for_status()

            book_data = response.json().get(f'ISBN:{isbn}', {})
            return {
                'user': user.id,
                'title': book_data.get('title', ''),
                'author': ', '.join(author['name'] for author in book_data.get('authors', [])),
                'isbn': isbn,
            }
        except requests.exceptions.RequestException as e:
            print(f"Error fetching book details: {e}")
            return None


class BookDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    API endpoint that allows viewing, updating, and deleting a book.
    """
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [permissions.IsAuthenticated]

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve details of a specific book.
        """
        try:
            return super().retrieve(request, *args, **kwargs)
        except NotFound:
            return Response({'error': 'Book not found'}, status=status.HTTP_404_NOT_FOUND)

    def update(self, request, *args, **kwargs):
        """
        Update details of a specific book.
        """
        try:
            return super().update(request, *args, **kwargs)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        """
        Delete a specific book.
        """
        try:
            return super().destroy(request, *args, **kwargs)
        except NotFound:
            return Response({'error': 'Book not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
