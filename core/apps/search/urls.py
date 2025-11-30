from django.urls import path
from .views import ProductAutoCompleteView


urlpatterns = [
    path('api/search/suggest/',ProductAutoCompleteView.as_view(),name='product-autocomplete'),
]