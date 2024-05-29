from django.urls import path
from . import views

urlpatterns = [
    path('register/',views.register, name='register'),
    path('login/',views.login, name='login'),
    path('enter-otp/',views.enter_otp, name='enter-otp'),
    path('logout/',views.logout, name='logout'),

    path('dashboard/',views.dashboard,name='dashboard'),
    path('',views.dashboard,name='dashboard'),
    path('validate_phone_number/', views.validate_phone_number, name='validate_phone_number'),
    path('toggle-two-factor/', views.toggle_two_factor, name='toggle_two_factor'),

    path('activate/<uidb64>/<token>/',views.activate, name='activate'),
    path("forgotPassword/", views.forgotPassword, name="forgotPassword"),
    path('resetpassword_validate/<uidb64>/<token>/',views.resetpassword_validate, name='resetpassword_validate'),
    
    path("resetPassword/", views.resetPassword, name="resetPassword"),
    path("my_orders/", views.my_orders, name="my_orders"),
    path("edit_profile/", views.edit_profile, name="edit_profile"),
    path("change_password/", views.change_password, name="change_password"),
    path("change_password/", views.change_password, name="change_password"),
    path("oder_detail/<int:order_id>/", views.order_detail, name="order_detail"),
]
