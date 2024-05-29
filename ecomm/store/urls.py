from django.urls import path,include
from .import views


urlpatterns = [
    path("", views.store, name="store"),
    path("category/", views.category, name="category"),
    path('category/<slug:category_slug>/' ,views.category_product, name='category_product'),
    path('<slug:category_slug>/<slug:product_slug>/' ,views.product_detail, name='product_detail'),
]