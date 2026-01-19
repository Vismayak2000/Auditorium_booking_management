from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import SignupForm, AuditoriumForm, BookingForm
from .models import Auditorium, Booking
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
import calendar
from datetime import date

# ---------- USER AUTH ----------
def signup_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully! Please login.')
            return redirect('login')
    else:
        form = SignupForm()
    return render(request, 'signup.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            if user.is_staff:
                return redirect('admin_dashboard')
            else:
                return redirect('user_dashboard')
        else:
            messages.error(request, 'Invalid credentials')
    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


# ---------- ADMIN ----------
@login_required
def admin_dashboard(request):
    if not request.user.is_staff:
        return redirect('user_dashboard')
    users = Auditorium.objects.all()
    return render(request, 'admin_dashboard.html', {'users': users})


@login_required
def add_auditorium(request):
    if not request.user.is_staff:
        return redirect('user_dashboard')
    form = AuditoriumForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('admin_dashboard')
    return render(request, 'add_auditorium.html', {'form': form})


@login_required
def view_bookings(request):
    bookings = Booking.objects.all()
    return render(request, 'view_bookings.html', {'bookings': bookings})


@login_required
def confirm_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    booking.status = 'Confirmed'
    booking.save()
    return redirect('view_bookings')


# ---------- USER ----------
@login_required
def user_dashboard(request):
    auditoriums = Auditorium.objects.all()
    return render(request, 'user_dashboard.html', {'auditoriums': auditoriums})


@login_required
def book_auditorium(request):
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.save()

            # Send email confirmation
            subject = f"Booking Confirmation - {booking.auditorium.name}"
            message = (
                f"Hi {request.user.username},\n\n"
                f"Your booking has been received.\n\n"
                f"Auditorium: {booking.auditorium.name}\n"
                f"Date: {booking.date}\n"
                f"Time: {booking.start_time} - {booking.end_time}\n"
                f"Total Cost: ₹{booking.total_cost}\n"
                f"Status: {booking.status}\n\n"
                f"Thank you for using our system!"
            )

            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [request.user.email],
                fail_silently=False,
            )

            return redirect('view_my_bookings')
    else:
        form = BookingForm()
    return render(request, 'book_auditorium.html', {'form': form})


@login_required
def view_my_bookings(request):
    bookings = Booking.objects.filter(user=request.user)
    return render(request, 'my_bookings.html', {'bookings': bookings})


@login_required
def edit_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    form = BookingForm(request.POST or None, instance=booking)
    if form.is_valid():
        form.save()
        return redirect('view_my_bookings')
    return render(request, 'book_auditorium.html', {'form': form})


@login_required
def delete_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    booking.delete()
    return redirect('view_my_bookings')


# ---------- EDIT AUDITORIUM ----------
@login_required
def edit_auditorium(request, auditorium_id):
    if not request.user.is_staff:
        return redirect('user_dashboard')
    
    auditorium = get_object_or_404(Auditorium, id=auditorium_id)
    form = AuditoriumForm(request.POST or None, instance=auditorium)
    if form.is_valid():
        form.save()
        return redirect('admin_dashboard')
    return render(request, 'edit_auditorium.html', {'form': form, 'auditorium': auditorium})


# ---------- DELETE AUDITORIUM ----------
@login_required
def delete_auditorium(request, auditorium_id):
    if not request.user.is_staff:
        return redirect('user_dashboard')
    
    auditorium = get_object_or_404(Auditorium, id=auditorium_id)
    if request.method == 'POST':
        auditorium.delete()
        return redirect('admin_dashboard')
    return render(request, 'confirm_delete_auditorium.html', {'auditorium': auditorium})



def calendar_view(request):
    auditoriums = Auditorium.objects.all()
    selected_auditorium_id = request.GET.get('auditorium')
    today = date.today()

    # Get selected month and year
    month = int(request.GET.get('month', today.month))
    year = int(request.GET.get('year', today.year))

    cal = calendar.Calendar(firstweekday=0)
    month_days = cal.monthdatescalendar(year, month)  # list of weeks (each week = 7 date objects)

    booked_dates = []
    if selected_auditorium_id:
        bookings = Booking.objects.filter(
            auditorium_id=selected_auditorium_id,
            date__year=year,
            date__month=month
        )
        booked_dates = [b.date for b in bookings]

    context = {
        'auditoriums': auditoriums,
        'selected_auditorium_id': int(selected_auditorium_id) if selected_auditorium_id else None,
        'month': month,
        'year': year,
        'month_name': calendar.month_name[month],
        'month_days': month_days,
        'booked_dates': booked_dates,
        'today': today,
        'prev_month': month - 1 if month > 1 else 12,
        'prev_year': year if month > 1 else year - 1,
        'next_month': month + 1 if month < 12 else 1,
        'next_year': year if month < 12 else year + 1,
        'day_names': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
    }

    return render(request, 'calendar.html', context)


