from django.urls import path
from MyLibrary.views import BookListCreateView, BookDetailView, CustomAuthToken

app_name = "MyLibrary"

urlpatterns = [
    path('token/', CustomAuthToken.as_view(), name="get-token"),
    path('books/', BookListCreateView.as_view(), name='book-list-create'),
    path('books/<int:pk>/', BookDetailView.as_view(), name='book-detail'),
]