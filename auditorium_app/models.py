# models.py
from django.db import models
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from django.core.exceptions import ValidationError

class Auditorium(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=150)
    capacity = models.IntegerField()
    rent_per_hour = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Booking(models.Model):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('Cancelled', 'Cancelled')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    auditorium = models.ForeignKey(Auditorium, on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    duration = models.DurationField(blank=True, null=True)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')

    def __str__(self):
        return f"{self.auditorium.name} booked by {self.user.username}"

    def clean(self):
        """Validate non-overlapping and time logic."""
        # Ensure end time is not same as start time
        if self.start_time == self.end_time:
            raise ValidationError("Start time and end time cannot be the same.")

        # Determine real datetime values
        start_dt = datetime.combine(self.date, self.start_time)
        end_dt = datetime.combine(self.date, self.end_time)
        if end_dt <= start_dt:
            end_dt += timedelta(days=1)

        # Check overlap with other bookings
        existing = Booking.objects.filter(
            auditorium=self.auditorium,
            date=self.date
        ).exclude(pk=self.pk)

        for booking in existing:
            b_start = datetime.combine(booking.date, booking.start_time)
            b_end = datetime.combine(booking.date, booking.end_time)
            if b_end <= b_start:
                b_end += timedelta(days=1)

            # Overlap if time ranges intersect
            if (start_dt < b_end) and (end_dt > b_start):
                raise ValidationError(
                    f"This auditorium is already booked between "
                    f"{booking.start_time.strftime('%I:%M %p')} - {booking.end_time.strftime('%I:%M %p')}."
                )

    def save(self, *args, **kwargs):
        """Auto calculate duration and cost."""
        self.full_clean()  # runs clean() before saving

        start_dt = datetime.combine(self.date, self.start_time)
        end_dt = datetime.combine(self.date, self.end_time)
        if end_dt <= start_dt:
            end_dt += timedelta(days=1)

        duration_td = end_dt - start_dt
        self.duration = duration_td

        hours = Decimal(duration_td.total_seconds()) / Decimal(3600)
        raw_cost = self.auditorium.rent_per_hour * hours
        self.total_cost = raw_cost.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        super().save(*args, **kwargs)

    @property
    def duration_h_m(self):
        """Return human-friendly duration: (hours, minutes)."""
        if not self.duration:
            return (0, 0)
        total_seconds = int(self.duration.total_seconds())
        return divmod(total_seconds // 60, 60)  # (hours, minutes)
