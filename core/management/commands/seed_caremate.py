from datetime import date, timedelta
from decimal import Decimal
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from core.models import Appointment, BlogPost, Doctor, Review, UserProfile


class Command(BaseCommand):
    help = 'Seed CareMate MySQL database with sample doctors, blog posts, demo patient, and reviews.'

    def handle(self, *args, **options):
        doctors_data = [
            {
                'name': 'Dr Jane Doe',
                'specialty': 'Dentist',
                'experience_years': 9,
                'rating': Decimal('4.0'),
                'has_booking_fee': False,
                'avatar': 'images/doc_jane.jpg',
                'location': 'Downtown Dental Suite',
                'bio': 'Preventive & cosmetic dentistry specialist focused on gentle, anxiety-free patient care.',
            },
            {
                'name': 'Dr Sam Wilson',
                'specialty': 'Dentist',
                'experience_years': 5,
                'rating': Decimal('4.0'),
                'has_booking_fee': False,
                'avatar': 'images/doc_sam.jpg',
                'location': 'CareMate Central Clinic',
                'bio': 'Restorative dental care and routine oral health consultations.',
            },
            {
                'name': 'Dr Pepper Potts',
                'specialty': 'Dentist',
                'experience_years': 5,
                'rating': Decimal('4.0'),
                'has_booking_fee': False,
                'avatar': 'images/doc_pepper.jpg',
                'location': 'Westside Dental Care',
                'bio': 'Orthodontics, aligners, and comprehensive family dentistry.',
            },
            {
                'name': 'Dr Tony Stark',
                'specialty': 'Dentist',
                'experience_years': 4,
                'rating': Decimal('4.0'),
                'has_booking_fee': False,
                'avatar': 'images/doc_tony.jpg',
                'location': 'CareMate Central Clinic',
                'bio': 'Digital smile design, implants, and modern minimally invasive procedures.',
            },
            {
                'name': 'Dr Meghan Carter',
                'specialty': 'Dentist',
                'experience_years': 3,
                'rating': Decimal('4.0'),
                'has_booking_fee': False,
                'avatar': 'images/doc_meghan.jpg',
                'location': 'Greenview Health Plaza',
                'bio': 'Pediatric & family dental care with emphasis on preventive hygiene.',
            },
            {
                'name': 'Dr Dev Patel',
                'specialty': 'Dentist',
                'experience_years': 2,
                'rating': Decimal('4.0'),
                'has_booking_fee': False,
                'avatar': 'images/doc_dev.jpg',
                'location': 'Downtown Dental Suite',
                'bio': 'Periodontal care, dental checkups, and personalized treatment plans.',
            },
        ]

        doctor_map = {}
        for item in doctors_data:
            doc, _ = Doctor.objects.update_or_create(
                name=item['name'],
                defaults=item,
            )
            doctor_map[doc.name] = doc

        blogs_data = [
            {
                'title': 'The Ultimate Guide to a Balanced Diet',
                'slug': 'the-ultimate-guide-to-a-balanced-diet',
                'category': 'Nutrition & Diet',
                'published_date': date(2022, 5, 17),
                'excerpt': 'Discover how a well-balanced diet can improve your energy, mental clarity, and long-term health.',
                'content': (
                    'A balanced diet provides your body with the essential nutrients, vitamins, and minerals '
                    'needed to function at its best every day. Aim to fill half your plate with colorful vegetables '
                    'and fruits, a quarter with lean proteins such as legumes, fish, or poultry, and a quarter with '
                    'whole grains.\n\n'
                    'Consistent hydration and mindful portioning help stabilize blood sugar, improve focus throughout '
                    'the workday, and support long-term cardiovascular and oral health.'
                ),
                'image': 'images/blog_diet.jpg',
                'author': 'Dr Jane Doe',
            },
            {
                'title': 'Quick 20-Min Workouts',
                'slug': 'quick-20-min-workouts',
                'category': 'Fitness',
                'published_date': date(2022, 5, 17),
                'excerpt': 'Get fit in no time! These short, effective workouts are perfect for busy schedules, helping you stay active and healthy ...',
                'content': (
                    'You do not need an hour at the gym to build strength and cardiovascular endurance. A focused '
                    '20-minute bodyweight circuit—combining brisk warm-up mobility, mountain climbers, squats, '
                    'push-ups, and core planks—raises your heart rate and boosts metabolism.\n\n'
                    'Try scheduling three short sessions a week outdoors or at home to improve sleep quality, '
                    'reduce stress, and keep your joints mobile.'
                ),
                'image': 'images/blog_workout.jpg',
                'author': 'Dr Sam Wilson',
            },
            {
                'title': 'Hormonal Changes in Your 30s',
                'slug': 'hormonal-changes-in-your-30s',
                'category': "Women's Health",
                'published_date': date(2022, 5, 17),
                'excerpt': 'Understanding the hormonal shifts that occur in your 30s can help you stay on top of your health. Learn what to expect and how ...',
                'content': (
                    'Your 30s often bring subtle shifts in energy, sleep patterns, skin, and stress resilience as '
                    'estrogen, progesterone, and thyroid levels naturally fluctuate.\n\n'
                    'Tracking cycle symptoms, prioritizing 7-8 hours of restorative sleep, eating iron- and fiber-rich '
                    'meals, and scheduling regular preventive checkups empower you to catch imbalances early.'
                ),
                'image': 'images/blog_hormonal.jpg',
                'author': 'Dr Meghan Carter',
            },
            {
                'title': 'Daily Mindfulness Tips',
                'slug': 'daily-mindfulness-tips',
                'category': 'Mental Health',
                'published_date': date(2022, 5, 17),
                'excerpt': 'Stay grounded with simple mindfulness practices. Learn how to integrate breathing exercises, meditation, and ...',
                'content': (
                    'Mindfulness does not require an empty calendar. Taking five minutes each morning for slow '
                    'diaphragmatic breathing—four seconds in, six seconds out—signals your nervous system to unwind.\n\n'
                    'Pair brief breathwork with screen-free breaks, gentle stretching, or a short gratitude note '
                    'before bed to lower everyday anxiety and sharpen emotional clarity.'
                ),
                'image': 'images/blog_mindfulness.jpg',
                'author': 'Dr Dev Patel',
            },
        ]

        for post in blogs_data:
            BlogPost.objects.update_or_create(slug=post['slug'], defaults=post)

        # Demo patient matching the Figma Login screen email
        demo_user, created = User.objects.get_or_create(
            username='emmawatson@gmail.com',
            defaults={
                'email': 'emmawatson@gmail.com',
                'first_name': 'Emma',
                'last_name': 'Watson',
            },
        )
        if created:
            demo_user.set_password('caremate123')
            demo_user.save()
        UserProfile.objects.get_or_create(
            user=demo_user,
            defaults={'role': 'patient', 'phone': '+1 555-0194'},
        )

        # Seed reviews matching the Figma Reviews screen (01 Jane 4.0, 02 Sam 0.0 unreviewed, 03 Dev 3.0, 04 Meghan 5.0)
        Review.objects.update_or_create(
            patient=demo_user,
            doctor=doctor_map['Dr Jane Doe'],
            defaults={'rating': Decimal('4.0'), 'comment': 'Very gentle and thorough dental checkup.'},
        )
        Review.objects.update_or_create(
            patient=demo_user,
            doctor=doctor_map['Dr Dev Patel'],
            defaults={'rating': Decimal('3.0'), 'comment': 'Helpful consultation and clear care plan.'},
        )
        Review.objects.update_or_create(
            patient=demo_user,
            doctor=doctor_map['Dr Meghan Carter'],
            defaults={'rating': Decimal('5.0'), 'comment': 'Wonderful care and zero wait time!'},
        )

        # Seed a sample upcoming appointment for the demo user if none exist
        if not Appointment.objects.filter(patient=demo_user).exists():
            Appointment.objects.create(
                patient=demo_user,
                doctor=doctor_map['Dr Sam Wilson'],
                appointment_date=date.today() + timedelta(days=2),
                time_slot='10:00 AM',
                reason='Routine dental cleaning and consultation',
                status='confirmed',
            )

        self.stdout.write(self.style.SUCCESS('CareMate database seeded successfully!'))
