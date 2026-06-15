from django.urls import path

from . import views

app_name = "inventory"

urlpatterns = [
    path("", views.ItemListView.as_view(), name="list"),
    path("add/", views.ItemCreateView.as_view(), name="add"),
    path("<int:pk>/", views.ItemDetailView.as_view(), name="detail"),
    path("<int:pk>/edit/", views.ItemUpdateView.as_view(), name="edit"),
    path("<int:pk>/delete/", views.ItemDeleteView.as_view(), name="delete"),
]
