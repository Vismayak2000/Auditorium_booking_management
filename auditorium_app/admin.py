from django.contrib import admin

from auditorium_app.models import Booking

# Register your models here.
@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'auditorium', 'date', 'start_time', 'end_time', 'duration', 'total_cost', 'status')
