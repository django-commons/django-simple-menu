from django.urls import path

from accounts import views

app_name = 'accounts'
urlpatterns = [
    path('sign_in/', views.SignInView.as_view(), name='sign_in'),
    path('sign_out/', views.SignOutView.as_view(), name='sign_out'),

    path('', views.IndexView.as_view(), name='index'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('super/', views.SuperOnlyView.as_view(), name='super_only'),

    path("sub/<int:i>/", views.SubPageView.as_view(), name='subpage'),
    path("space test", views.SubPageView.as_view(), name='space_test'),
]
