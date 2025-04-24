from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from .models import CustomUser, Flight, Booking

class BaseTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = CustomUser.objects.create_user(username='admin', password='password', role='admin')
        self.staff = CustomUser.objects.create_user(username='staff', password='password', role='staff')
        self.customer = CustomUser.objects.create_user(username='customer', password='password', role='user')

        self.flight = Flight.objects.create(
            flight_number='EI123',
            origin='Dublin',
            destination='London',
            departure_time=timezone.now(),
            arrival_time=timezone.now() + timezone.timedelta(hours=2),
            available_seats=50
        )

class RegistrationLoginTests(BaseTestCase):
    def test_registration_page_loads(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)

    def test_login_redirects_to_correct_dashboard(self):
        self.client.login(username='admin', password='password')
        response = self.client.get(reverse('dashboard'))
        self.assertContains(response, 'Admin Dashboard')

class BookingTests(BaseTestCase):
    def test_flight_booking_reduces_seats(self):
        self.client.login(username='customer', password='password')
        response = self.client.post(reverse('book_flight'), {
            'flight_id': self.flight.id,
            'booked_seats': 3
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.flight.refresh_from_db()
        self.assertEqual(self.flight.available_seats, 47)

class StaffBookingStatusTests(BaseTestCase):
    def test_staff_can_confirm_booking(self):
        booking = Booking.objects.create(
            user=self.customer,
            flight=self.flight,
            booked_seats=2,
            status='pending'
        )
        self.client.login(username='staff', password='password')
        response = self.client.post(reverse('update_booking_status', args=[booking.id]), {
            'status': 'confirmed'
        }, follow=True)
        booking.refresh_from_db()
        self.assertEqual(booking.status, 'confirmed')

    def test_cancelling_booking_returns_seats(self):
        booking = Booking.objects.create(
            user=self.customer,
            flight=self.flight,
            booked_seats=5,
            status='confirmed'
        )
        self.flight.available_seats -= 5
        self.flight.save()

        self.client.login(username='staff', password='password')
        response = self.client.post(reverse('update_booking_status', args=[booking.id]), {
            'status': 'cancelled'
        }, follow=True)

        booking.refresh_from_db()
        self.flight.refresh_from_db()
        self.assertEqual(booking.status, 'cancelled')
        self.assertEqual(self.flight.available_seats, 50)

class AdminFlightTests(BaseTestCase):
    def test_admin_can_add_flight(self):
        self.client.login(username='admin', password='password')
        response = self.client.post(reverse('add_flight'), {
            'flight_number': 'EI124',
            'origin': 'Paris',
            'destination': 'Berlin',
            'departure_time': timezone.now(),
            'arrival_time': timezone.now() + timezone.timedelta(hours=2),
            'available_seats': 60
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Flight.objects.filter(flight_number='EI124').exists())

    def test_admin_can_edit_flight(self):
        self.client.login(username='admin', password='password')
        response = self.client.post(reverse('edit_flight', args=[self.flight.id]), {
            'flight_number': 'EI999',
            'origin': 'Rome',
            'destination': 'Milan',
            'departure_time': timezone.now(),
            'arrival_time': timezone.now() + timezone.timedelta(hours=2),
            'available_seats': 70
        }, follow=True)
        self.flight.refresh_from_db()
        self.assertEqual(self.flight.flight_number, 'EI999')
        self.assertEqual(self.flight.available_seats, 70)
