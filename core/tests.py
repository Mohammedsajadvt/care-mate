from datetime import date, timedelta
from decimal import Decimal
from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Appointment, BlogPost, Doctor, Review, UserProfile


class CareMateTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='patient@example.com',
            email='patient@example.com',
            password='password123',
            first_name='Alice',
        )
        UserProfile.objects.create(user=self.user, role='patient', phone='555-0100')

        self.other_user = User.objects.create_user(
            username='other@example.com',
            email='other@example.com',
            password='password123',
            first_name='Bob',
        )
        UserProfile.objects.create(user=self.other_user, role='patient')

        self.doctor = Doctor.objects.create(
            name='Dr Jane Doe',
            specialty='Dentist',
            experience_years=9,
            rating=Decimal('4.0'),
            has_booking_fee=False,
            avatar='images/doc_jane.jpg',
        )
        self.blog = BlogPost.objects.create(
            title='Balanced Diet Guide',
            slug='balanced-diet-guide',
            category='Nutrition & Diet',
            published_date=date(2022, 5, 17),
            excerpt='Eat well every day.',
            content='Full content here.',
            image='images/blog_diet.jpg',
        )

    def test_public_pages_render_ok(self):
        for name in ('landing', 'login', 'signup', 'appointments', 'reviews', 'blog'):
            resp = self.client.get(reverse(name))
            self.assertEqual(resp.status_code, 200, f'{name} failed')
        login_html = self.client.get(reverse('login')).content.decode('utf-8')
        self.assertNotIn('emmawatson@gmail.com', login_html)
        self.assertIn('Enter your username', login_html)
        resp_detail = self.client.get(reverse('blog_detail', args=[self.blog.slug]))
        self.assertEqual(resp_detail.status_code, 200)

    def test_signup_and_login(self):
        resp = self.client.post(
            reverse('signup'),
            {
                'role': 'patient',
                'name': 'Clara Oswald',
                'phone': '555-0123',
                'email': 'clara@example.com',
                'password': 'password123',
            },
        )
        self.assertRedirects(resp, reverse('appointments'))
        self.assertTrue(User.objects.filter(email='clara@example.com').exists())
        self.client.post(reverse('logout'))
        login_resp = self.client.post(
            reverse('login'),
            {'email': 'clara@example.com', 'password': 'password123'},
        )
        self.assertRedirects(login_resp, reverse('appointments'))

    def test_booking_prevents_double_booking_and_releases_on_cancel(self):
        appt_date = (date.today() + timedelta(days=1)).isoformat()
        self.client.force_login(self.user)
        resp = self.client.post(
            reverse('book_appointment'),
            {
                'doctor_id': self.doctor.id,
                'appointment_date': appt_date,
                'time_slot': '10:00 AM',
                'reason': 'Dental checkup',
            },
        )
        self.assertRedirects(resp, reverse('my_appointments'))
        self.assertEqual(Appointment.objects.count(), 1)

        # Available slots API marks 10:00 AM as booked
        slots_resp = self.client.get(
            reverse('available_slots'),
            {'doctor_id': self.doctor.id, 'date': appt_date},
        )
        self.assertEqual(slots_resp.json()['booked_slots'], ['10:00 AM'])

        # Second patient cannot book the same slot
        self.client.force_login(self.other_user)
        dup_resp = self.client.post(
            reverse('book_appointment'),
            {
                'doctor_id': self.doctor.id,
                'appointment_date': appt_date,
                'time_slot': '10:00 AM',
            },
        )
        self.assertRedirects(dup_resp, reverse('appointments'))
        self.assertEqual(Appointment.objects.filter(status='confirmed').count(), 1)

        # Original patient cancels -> slot becomes available again
        appt = Appointment.objects.first()
        self.client.force_login(self.user)
        self.client.post(reverse('cancel_appointment', args=[appt.id]))
        appt.refresh_from_db()
        self.assertEqual(appt.status, 'cancelled')
        self.assertIsNone(appt.slot_lock_key)

        self.client.force_login(self.other_user)
        rebook_resp = self.client.post(
            reverse('book_appointment'),
            {
                'doctor_id': self.doctor.id,
                'appointment_date': appt_date,
                'time_slot': '10:00 AM',
            },
        )
        self.assertRedirects(rebook_resp, reverse('my_appointments'))
        self.assertEqual(Appointment.objects.filter(status='confirmed').count(), 2 - 1)

    def test_submit_review_updates_doctor_rating(self):
        self.client.force_login(self.user)
        resp = self.client.post(
            reverse('submit_review'),
            {'doctor_id': self.doctor.id, 'rating': '5', 'comment': 'Great care!'},
        )
        self.assertRedirects(resp, reverse('reviews'))
        self.doctor.refresh_from_db()
        self.assertEqual(self.doctor.rating, Decimal('5.0'))
        self.assertTrue(Review.objects.filter(patient=self.user, doctor=self.doctor).exists())

    def test_caremate_admin_ui_renders(self):
        login_page = self.client.get('/admin/login/')
        self.assertEqual(login_page.status_code, 200)
        self.assertIn('caremate_admin.css', login_page.content.decode('utf-8'))

        staff_user = User.objects.create_user(
            username='staff_test',
            email='staff_test@example.com',
            password='password123',
            is_staff=True,
            is_superuser=True,
        )
        self.client.force_login(staff_user)
        for url in ('/admin/', '/admin/core/appointment/', '/admin/core/doctor/'):
            resp = self.client.get(url)
            self.assertEqual(resp.status_code, 200, f'{url} failed')
            body = resp.content.decode('utf-8')
            self.assertIn('CareMate', body)
            self.assertIn('caremate_admin.css', body)
