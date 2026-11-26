from django.contrib import admin
from django.utils.html import format_html
from .models import Appointment, BlogPost, Doctor, Review, UserProfile

admin.site.site_header = 'CareMate'
admin.site.site_title = 'CareMate Admin'
admin.site.index_title = 'Clinic Administration'


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'phone')
    list_filter = ('role',)
    search_fields = ('user__username', 'user__email', 'phone')


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ('name', 'specialty', 'experience_years', 'rating', 'has_booking_fee', 'location')
    list_filter = ('specialty', 'has_booking_fee')
    search_fields = ('name', 'specialty', 'location')


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'appointment_date', 'time_slot', 'status_badge', 'created_at')
    list_filter = ('status', 'appointment_date', 'doctor')
    search_fields = ('patient__username', 'patient__email', 'doctor__name')

    @admin.display(description='Status', ordering='status')
    def status_badge(self, obj):
        return format_html(
            '<span class="cm-pill cm-pill-{}">{}</span>',
            obj.status,
            obj.get_status_display(),
        )


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'rating', 'updated_at')
    list_filter = ('rating', 'doctor')
    search_fields = ('patient__username', 'doctor__name', 'comment')


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'published_date', 'author')
    list_filter = ('category', 'published_date')
    search_fields = ('title', 'category', 'excerpt')
    prepopulated_fields = {'slug': ('title',)}
