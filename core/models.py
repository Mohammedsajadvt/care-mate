from decimal import Decimal
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Avg


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('patient', 'Patient'),
        ('doctor', 'Doctor'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='patient')
    phone = models.CharField(max_length=30, blank=True)

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.role})"


class Doctor(models.Model):
    user = models.OneToOneField(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='doctor_profile',
    )
    name = models.CharField(max_length=120)
    specialty = models.CharField(max_length=80, default='Dentist', db_index=True)
    experience_years = models.PositiveIntegerField(default=1, db_index=True)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=Decimal('4.0'))
    has_booking_fee = models.BooleanField(default=False, db_index=True)
    booking_fee_amount = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('0.00'))
    avatar = models.CharField(max_length=255, default='images/doc_jane.jpg')
    location = models.CharField(max_length=120, default='Main Medical Center')
    bio = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return f"{self.name} — {self.specialty}"

    def recalculate_rating(self):
        """Recompute doctor's average rating from persisted patient reviews."""
        avg_val = self.reviews.aggregate(avg=Avg('rating'))['avg']
        if avg_val is not None:
            self.rating = Decimal(str(round(float(avg_val), 1)))
            self.save(update_fields=['rating'])


class Appointment(models.Model):
    TIME_SLOT_CHOICES = [
        ('09:00 AM', '09:00 AM'),
        ('10:00 AM', '10:00 AM'),
        ('11:00 AM', '11:00 AM'),
        ('01:00 PM', '01:00 PM'),
        ('02:00 PM', '02:00 PM'),
        ('03:30 PM', '03:30 PM'),
        ('05:00 PM', '05:00 PM'),
    ]

    STATUS_CHOICES = [
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='appointments')
    appointment_date = models.DateField(db_index=True)
    time_slot = models.CharField(max_length=20, choices=TIME_SLOT_CHOICES)
    reason = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='confirmed', db_index=True)
    # Nullable unique key enforces DB-level double-booking prevention in MySQL while allowing re-booking cancelled slots.
    slot_lock_key = models.CharField(max_length=120, unique=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['appointment_date', 'time_slot', '-created_at']

    def save(self, *args, **kwargs):
        if self.status == 'cancelled':
            self.slot_lock_key = None
        else:
            self.slot_lock_key = f"{self.doctor_id}:{self.appointment_date.isoformat()}:{self.time_slot}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.patient.username} -> {self.doctor.name} ({self.appointment_date} {self.time_slot})"


class Review(models.Model):
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='reviews')
    rating = models.DecimalField(max_digits=2, decimal_places=1)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('patient', 'doctor')
        ordering = ['doctor__id']

    def __str__(self):
        return f"{self.patient.username} rated {self.doctor.name}: {self.rating}"


class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=220)
    category = models.CharField(max_length=80, db_index=True)
    published_date = models.DateField(db_index=True)
    excerpt = models.TextField()
    content = models.TextField()
    image = models.CharField(max_length=255)
    author = models.CharField(max_length=100, default='CareMate Editorial')

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.title
