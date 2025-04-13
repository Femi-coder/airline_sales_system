from django.urls import path
from .views import (
    register_view, home_view, CustomLoginView, CustomLogoutView,
    dashboard_view, admin_dashboard_view, customer_booking_view,
    staff_dashboard_view, staff_manage_orders, update_booking_status,
    add_flight_view, edit_flight_view, delete_flight_view,
    manage_flights
)

urlpatterns = [
    path('', home_view, name='home'),
    path('register/', register_view, name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('book/', customer_booking_view, name='book_flight'),
    path('staff_dashboard/', staff_dashboard_view, name='staff_dashboard'),
    path('staff_manage_orders/', staff_manage_orders, name='staff_manage_orders'),
    path('staff_manage_orders/update/<int:booking_id>/', update_booking_status, name='update_booking_status'),
    path('admin_dashboard/', admin_dashboard_view, name='admin_dashboard'),
    path('manage_flights/', manage_flights, name='manage_flights'),
    path('edit_flight/<int:flight_id>/', edit_flight_view, name='edit_flight'),
    path('delete_flight/<int:flight_id>/', delete_flight_view, name='delete_flight'),
    path('add_flight/', add_flight_view, name='add_flight'),
]
