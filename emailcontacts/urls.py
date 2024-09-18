from django.urls import path

from emailcontacts.views import ContactDetailView, ContactListCreateView, GroupDetailView, GroupListCreateView


urlpatterns = [
    path('', GroupListCreateView.as_view(), name='group-list-create'),
    path('<int:pk>/', GroupDetailView.as_view(), name='group-detail'),
    path('<int:pk>/contacts/', ContactListCreateView.as_view(), name='contact-list-create'),
    path('<int:group_id>/contacts/<int:pk>/', ContactDetailView.as_view(), name='contact-detail'),
]
