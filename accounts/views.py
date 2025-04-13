from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse_lazy
from .forms import BookingStatusForm, CustomUserCreationForm
from .models import Flight, Booking

# Custom user register view
def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.role = form.cleaned_data['role']
            user.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})


# Custom login view
class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'

    def get_success_url(self):
        role = self.request.user.role
        if role == 'admin':
            return reverse_lazy('admin_dashboard')
        elif role == 'staff':
            return reverse_lazy('staff_dashboard')
        return reverse_lazy('dashboard')


# Custom logout view
class CustomLogoutView(LogoutView):
    template_name = 'accounts/logout.html'


# Home page view
def home_view(request):
    return render(request, 'accounts/home.html')


# General dashboard view
@login_required
def dashboard_view(request):
    return render(request, 'accounts/dashboard.html', {
        'user': request.user,
        'role': request.user.role,
        'is_admin': request.user.role == 'admin'
    })


@login_required
@user_passes_test(lambda u: u.role == 'admin')
def admin_dashboard_view(request):
    total_flights = Flight.objects.count()
    total_bookings = Booking.objects.count()
    flights = Flight.objects.all()  # ✅ Make sure this line is here

    return render(request, 'accounts/admin_dashboard.html', {
        'total_flights': total_flights,
        'total_bookings': total_bookings,
        'flights': flights  # ✅ Make sure this is passed to the template
    })



# Admin flight management
@login_required
@user_passes_test(lambda u: u.role == 'admin')
def manage_flights(request):
    if request.method == 'POST':
        flight_number = request.POST.get('flight_number')
        origin = request.POST.get('origin')
        destination = request.POST.get('destination')
        departure_time = request.POST.get('departure_time')
        arrival_time = request.POST.get('arrival_time')
        available_seats = request.POST.get('available_seats')

        Flight.objects.create(
            flight_number=flight_number,
            origin=origin,
            destination=destination,
            departure_time=departure_time,
            arrival_time=arrival_time,
            available_seats=available_seats
        )
        return redirect('admin_dashboard')

    return render(request, 'accounts/manage_flights.html')


# Staff dashboard
@login_required
@user_passes_test(lambda u: u.role == 'staff')
def staff_dashboard_view(request):
    return render(request, 'accounts/staff_dashboard.html', {'user': request.user})


# Staff booking management
@login_required
@user_passes_test(lambda u: u.role == 'staff')
def staff_manage_orders(request):
    bookings = Booking.objects.all()
    return render(request, 'accounts/staff_manage_orders.html', {'bookings': bookings})


@login_required
@user_passes_test(lambda u: u.role == 'staff')
def update_booking_status(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    previous_status = booking.status  # Store the old status
    form = BookingStatusForm(request.POST or None, instance=booking)

    if request.method == 'POST' and form.is_valid():
        new_booking = form.save(commit=False)

        if previous_status != 'cancelled' and new_booking.status == 'cancelled':
            # If changing from something else to 'cancelled', return the seats
            booking.flight.available_seats += booking.booked_seats
            booking.flight.save()

        new_booking.save()
        return redirect('staff_manage_orders')

    return render(request, 'accounts/update_booking_status.html', {
        'form': form,
        'booking': booking
    })
    
# Add flight
@login_required
@user_passes_test(lambda u: u.role == 'admin')
def add_flight_view(request):
    if request.method == 'POST':
        flight_number = request.POST.get('flight_number')
        origin = request.POST.get('origin')
        destination = request.POST.get('destination')
        departure_time = request.POST.get('departure_time')
        arrival_time = request.POST.get('arrival_time')
        available_seats = request.POST.get('available_seats')

        Flight.objects.create(
            flight_number=flight_number,
            origin=origin,
            destination=destination,
            departure_time=departure_time,
            arrival_time=arrival_time,
            available_seats=available_seats
        )
        return redirect('admin_dashboard')
    return render(request, 'accounts/add_flight.html')

# Edit flight
@login_required
@user_passes_test(lambda u: u.role == 'admin')
def edit_flight_view(request, flight_id):
    flight = get_object_or_404(Flight, id=flight_id)
    if request.method == 'POST':
        flight.flight_number = request.POST.get('flight_number')
        flight.origin = request.POST.get('origin')
        flight.destination = request.POST.get('destination')
        flight.departure_time = request.POST.get('departure_time')
        flight.arrival_time = request.POST.get('arrival_time')
        flight.available_seats = request.POST.get('available_seats')
        flight.save()
        return redirect('admin_dashboard')
    return render(request, 'accounts/edit_flight.html', {'flight': flight})

# Delete flight
@login_required
@user_passes_test(lambda u: u.role == 'admin')
def delete_flight_view(request, flight_id):
    flight = get_object_or_404(Flight, id=flight_id)
    if request.method == 'POST':
        flight.delete()
        return redirect('admin_dashboard')
    return render(request, 'accounts/delete_flight.html', {'flight': flight})


# Customer flight booking
@login_required
@user_passes_test(lambda u: u.role == 'user')
def customer_booking_view(request):
    flights = Flight.objects.all()
    error = None

    if request.method == 'POST':
        flight_id = request.POST.get('flight_id')
        booked_seats = int(request.POST.get('booked_seats'))
        try:
            flight = Flight.objects.get(id=flight_id)
            if booked_seats <= flight.available_seats:
                Booking.objects.create(user=request.user, flight=flight, booked_seats=booked_seats)
                flight.available_seats -= booked_seats
                flight.save()
                return redirect('dashboard')
            else:
                error = "Not enough seats available"
        except Flight.DoesNotExist:
            error = "Flight not found"

    return render(request, 'accounts/customer_booking.html', {
        'flights': flights,
        'error': error
    })
