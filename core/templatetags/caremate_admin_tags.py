from django import template
from core.models import Appointment, BlogPost, Doctor, Review

register = template.Library()


@register.simple_tag
def get_caremate_stats():
    """Return live CareMate counts for the admin dashboard cards."""
    return {
        'doctors': Doctor.objects.count(),
        'confirmed_appointments': Appointment.objects.filter(status='confirmed').count(),
        'total_appointments': Appointment.objects.count(),
        'reviews': Review.objects.count(),
        'blogs': BlogPost.objects.count(),
    }
