from django.urls import path
from . import views

urlpatterns = [
    path('', views.PersonListView.as_view(), name='staff'),
    path('department/<str:dep>/', views.DepartmentView.as_view(), name='department-staff'),
    path('room/<str:room>/', views.RoomView.as_view(), name='room-staff'),
    path('title/<str:title>/', views.TitleView.as_view(), name='title-staff'),
    path('person/<int:id>/', views.PersonDetailView.as_view(), name='person-detail-staff'),
    path('person/<int:id>/table/', views.PersonDetailViewTable.as_view(), name='person-detail-staff-table'),
    path('tree/', views.TreeView.as_view(), name='tree'),
]