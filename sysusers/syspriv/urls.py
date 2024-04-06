from django.urls import path
from . import views
from . import models
from django_filters.views import FilterView
from django.contrib.auth.views import LogoutView



urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('update/', views.get_systems, name='update-systems'),
    path('systems/', views.SystemListView.as_view(), name='system-list'),
    path("system/<int:id>/", views.SystemDetailView.as_view(), name='system-detail'),
    path("system-people/<int:id>/", views.SystemPeopleView.as_view(), name='system-people'),
    path('people/', views.PersonListView.as_view(), name='people-list'),
    path("person/<int:id>/",views.PersonDetailView.as_view(), name='person-detail'),
    path('departments/', views.DeaprtmentListView.as_view(), name='department-list'),
    path('department/<int:id>/', views.DeaprtmentDetailView.as_view(), name='department-detail'),
    path('commission-list/', views.CommissionListView.as_view(), name='commission-list'),

    #    path('roles/', views.RolesListView.as_view(), name='roles-list'),
    #    path("getuser/", views.FilterUserView.as_view(), name='user-form'),
    #    path("getsystem/", views.FilterSystemView.as_view(), name='system-form'),
    path('commission/', views.CommissionCreateView.as_view(), name='commission-create'),
    path('commission-filter/', FilterView.as_view(model=models.Commission, filterset_fields=('user_last_name',)), name='commission-filter'),
    path('commission/<int:pk>/', views.CommissionDetailView.as_view(), name='commission-detail'),
    path('test/', views.test_page, name='test-page'),
    path('login/', views.MyLoginView.as_view(),name='login'),
    #path('login/', views.login_redirect,name='login'),
    path('logout/', LogoutView.as_view(next_page='login'),name='logout'),
    path('summary/', views.SummaryView.as_view(), name='summary'),
    #    path('l/', views.reset, name='reset'),

]

a=FilterView()