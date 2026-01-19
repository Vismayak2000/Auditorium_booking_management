from django.urls import path
from . import views

urlpatterns = [
    
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),

    # Admin
    path('admin_dashboard', views.admin_dashboard, name='admin_dashboard'),
    path('add_auditorium', views.add_auditorium, name='add_auditorium'),
    path('view_bookings', views.view_bookings, name='view_bookings'),
    path('confirm_booking/<int:booking_id>/', views.confirm_booking, name='confirm_booking'),
    path('edit_auditorium/<int:auditorium_id>/', views.edit_auditorium, name='edit_auditorium'),
    path('delete_auditorium/<int:auditorium_id>/', views.delete_auditorium, name='delete_auditorium'),


    # User
    path('user_dashboard', views.user_dashboard, name='user_dashboard'),
    path('book_auditorium', views.book_auditorium, name='book_auditorium'),
    path('view_my_bookings', views.view_my_bookings, name='view_my_bookings'),
    path('edit_booking/<int:booking_id>/', views.edit_booking, name='edit_booking'),
    path('delete_booking/<int:booking_id>/', views.delete_booking, name='delete_booking'),
    path('', views.calendar_view, name='calendar_view'),
    
]
