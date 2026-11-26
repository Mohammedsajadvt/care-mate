from datetime import date
from decimal import Decimal, InvalidOperation
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db import IntegrityError, transaction
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_POST

from .models import Appointment, BlogPost, Doctor, Review, UserProfile


def landing_view(request):
    return render(request, 'core/landing.html', {'active_nav': 'home'})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('appointments')

    error = None
    entered_email = ''
    next_url = request.GET.get('next') or request.POST.get('next') or ''

    if request.method == 'POST':
        entered_email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')

        user_obj = User.objects.filter(
            Q(email__iexact=entered_email) | Q(username__iexact=entered_email)
        ).first()

        user = None
        if user_obj:
            user = authenticate(request, username=user_obj.username, password=password)

        if user is not None:
            login(request, user)
            if next_url and next_url.startswith('/'):
                return redirect(next_url)
            return redirect('appointments')
        error = 'Invalid username or password. Please try again.'

    return render(
        request,
        'core/login.html',
        {
            'active_nav': '',
            'error': error,
            'entered_email': entered_email,
            'next_url': next_url,
        },
    )


def signup_view(request):
    if request.user.is_authenticated:
        return redirect('appointments')

    error = None
    form_data = {'role': '', 'name': '', 'phone': '', 'email': ''}

    if request.method == 'POST':
        role = request.POST.get('role', 'patient').strip().lower()
        name = request.POST.get('name', '').strip()
        phone = request.POST.get('phone', '').strip()
        email = request.POST.get('email', '').strip().lower()
        password = request.POST.get('password', '')

        form_data = {'role': role, 'name': name, 'phone': phone, 'email': email}

        if role not in ('patient', 'doctor'):
            error = 'Please select a valid role.'
        elif not name or not email or not password:
            error = 'Name, email, and password are required.'
        elif len(password) < 6:
            error = 'Password must be at least 6 characters long.'
        elif User.objects.filter(Q(email__iexact=email) | Q(username__iexact=email)).exists():
            error = 'An account with this email already exists.'
        else:
            name_parts = name.split(None, 1)
            first_name = name_parts[0]
            last_name = name_parts[1] if len(name_parts) > 1 else ''
            with transaction.atomic():
                user = User.objects.create_user(
                    username=email,
                    email=email,
                    password=password,
                    first_name=first_name,
                    last_name=last_name,
                )
                UserProfile.objects.create(user=user, role=role, phone=phone)
                if role == 'doctor':
                    display_name = name if name.lower().startswith('dr') else f'Dr {name}'
                    Doctor.objects.create(
                        user=user,
                        name=display_name,
                        specialty='General Physician',
                        experience_years=1,
                        rating=Decimal('5.0'),
                        has_booking_fee=False,
                        avatar='images/doc_dev.jpg',
                    )
            login(request, user)
            messages.success(request, 'Welcome to CareMate! Your account is ready.')
            return redirect('appointments')

    return render(
        request,
        'core/signup.html',
        {'active_nav': '', 'error': error, 'form_data': form_data},
    )


@require_POST
def logout_view(request):
    logout(request)
    return redirect('landing')


def appointments_view(request):
    specialty = request.GET.get('specialty', 'All').strip()
    rating_filter = request.GET.get('rating', 'All').strip()
    experience = request.GET.get('experience', 'All').strip()
    booking_fee = request.GET.get('booking_fee', 'All').strip()

    doctors_qs = Doctor.objects.all()

    if specialty and specialty != 'All':
        doctors_qs = doctors_qs.filter(specialty__iexact=specialty)

    if rating_filter and rating_filter != 'All':
        try:
            min_rating = Decimal(rating_filter)
            doctors_qs = doctors_qs.filter(rating__gte=min_rating)
        except InvalidOperation:
            pass

    if experience and experience != 'All':
        if experience == '0-2':
            doctors_qs = doctors_qs.filter(experience_years__gte=0, experience_years__lte=2)
        elif experience == '2-10':
            doctors_qs = doctors_qs.filter(experience_years__gte=2, experience_years__lte=10)
        elif experience == '10+':
            doctors_qs = doctors_qs.filter(experience_years__gt=10)

    if booking_fee == 'No':
        doctors_qs = doctors_qs.filter(has_booking_fee=False)
    elif booking_fee == 'Yes':
        doctors_qs = doctors_qs.filter(has_booking_fee=True)

    total_doctors = doctors_qs.count()
    paginator = Paginator(doctors_qs, 6)
    page_obj = paginator.get_page(request.GET.get('page', 1))

    specialties = list(
        Doctor.objects.values_list('specialty', flat=True).distinct().order_by('specialty')
    )

    return render(
        request,
        'core/appointments.html',
        {
            'active_nav': 'appointments',
            'page_obj': page_obj,
            'total_doctors': total_doctors,
            'specialties': specialties,
            'selected_specialty': specialty,
            'selected_rating': rating_filter,
            'selected_experience': experience,
            'selected_booking_fee': booking_fee,
            'time_slots': [slot[0] for slot in Appointment.TIME_SLOT_CHOICES],
            'today_iso': date.today().isoformat(),
        },
    )


@require_GET
def available_slots_api(request):
    doctor_id = request.GET.get('doctor_id')
    date_str = request.GET.get('date')
    if not doctor_id or not date_str:
        return JsonResponse({'booked_slots': []})
    try:
        parsed_date = date.fromisoformat(date_str)
    except ValueError:
        return JsonResponse({'booked_slots': []})

    booked = list(
        Appointment.objects.filter(
            doctor_id=doctor_id,
            appointment_date=parsed_date,
        )
        .exclude(status='cancelled')
        .values_list('time_slot', flat=True)
    )
    return JsonResponse({'booked_slots': booked})


@login_required
@require_POST
def book_appointment_view(request):
    doctor_id = request.POST.get('doctor_id')
    date_str = request.POST.get('appointment_date', '').strip()
    time_slot = request.POST.get('time_slot', '').strip()
    reason = request.POST.get('reason', '').strip()

    doctor = get_object_or_404(Doctor, pk=doctor_id)
    valid_slots = {slot[0] for slot in Appointment.TIME_SLOT_CHOICES}

    try:
        appt_date = date.fromisoformat(date_str)
    except ValueError:
        messages.error(request, 'Please select a valid appointment date.')
        return redirect('appointments')

    if appt_date < date.today():
        messages.error(request, 'Appointment date cannot be in the past.')
        return redirect('appointments')

    if time_slot not in valid_slots:
        messages.error(request, 'Please choose a valid time slot.')
        return redirect('appointments')

    try:
        with transaction.atomic():
            # Lock doctor row to serialize concurrent booking checks on MySQL
            Doctor.objects.select_for_update().get(pk=doctor.pk)
            if Appointment.objects.filter(
                doctor=doctor,
                appointment_date=appt_date,
                time_slot=time_slot,
            ).exclude(status='cancelled').exists():
                messages.error(
                    request,
                    f'{doctor.name} is already booked at {time_slot} on {appt_date}. Please pick another slot.',
                )
                return redirect('appointments')

            Appointment.objects.create(
                patient=request.user,
                doctor=doctor,
                appointment_date=appt_date,
                time_slot=time_slot,
                reason=reason,
                status='confirmed',
            )
    except IntegrityError:
        messages.error(request, 'That slot was just booked by another patient. Please pick another time.')
        return redirect('appointments')

    messages.success(
        request,
        f'Appointment confirmed with {doctor.name} on {appt_date.strftime("%b %d, %Y")} at {time_slot}.',
    )
    return redirect('my_appointments')


@login_required
def my_appointments_view(request):
    appointments = (
        Appointment.objects.filter(patient=request.user)
        .select_related('doctor')
        .order_by('-appointment_date', 'time_slot')
    )
    return render(
        request,
        'core/my_appointments.html',
        {'active_nav': 'appointments', 'appointments': appointments},
    )


@login_required
@require_POST
def cancel_appointment_view(request, appointment_id):
    appt = get_object_or_404(Appointment, pk=appointment_id, patient=request.user)
    if appt.status != 'cancelled':
        appt.status = 'cancelled'
        appt.save()
        messages.success(request, f'Cancelled appointment with {appt.doctor.name}.')
    return redirect('my_appointments')


def reviews_view(request):
    # Match Figma ordering: Dr Jane Doe, Dr Sam Wilson, Dr Dev Patel, Dr Meghan Carter first, then others
    preferred_names = ['Dr Jane Doe', 'Dr Sam Wilson', 'Dr Dev Patel', 'Dr Meghan Carter']
    all_doctors = list(Doctor.objects.all())
    by_name = {d.name: d for d in all_doctors}
    ordered_doctors = [by_name[n] for n in preferred_names if n in by_name]
    for d in all_doctors:
        if d.name not in preferred_names:
            ordered_doctors.append(d)

    # Display first 4 doctors matching Figma layout (or all if user wants)
    display_doctors = ordered_doctors[:4]

    if request.user.is_authenticated:
        user_reviews = {
            r.doctor_id: r for r in Review.objects.filter(patient=request.user)
        }
    else:
        demo_user = User.objects.filter(username='emmawatson@gmail.com').first()
        user_reviews = (
            {r.doctor_id: r for r in Review.objects.filter(patient=demo_user)}
            if demo_user
            else {}
        )

    review_cards = []
    for idx, doc in enumerate(display_doctors, start=1):
        rev = user_reviews.get(doc.id)
        score = f'{float(rev.rating):.1f}' if rev else '0.0'
        stars_filled = int(round(float(rev.rating))) if rev else 0
        review_cards.append(
            {
                'index_label': f'{idx:02d}',
                'doctor': doc,
                'review': rev,
                'score': score,
                'stars_filled': stars_filled,
                'has_review': rev is not None,
            }
        )

    return render(
        request,
        'core/reviews.html',
        {'active_nav': 'reviews', 'review_cards': review_cards},
    )


@login_required
@require_POST
def submit_review_view(request):
    doctor_id = request.POST.get('doctor_id')
    rating_raw = request.POST.get('rating', '').strip()
    comment = request.POST.get('comment', '').strip()

    doctor = get_object_or_404(Doctor, pk=doctor_id)
    try:
        rating_val = Decimal(rating_raw)
        if rating_val < Decimal('1') or rating_val > Decimal('5'):
            raise InvalidOperation()
    except InvalidOperation:
        messages.error(request, 'Please select a star rating from 1 to 5.')
        return redirect('reviews')

    Review.objects.update_or_create(
        patient=request.user,
        doctor=doctor,
        defaults={'rating': rating_val, 'comment': comment},
    )
    doctor.recalculate_rating()
    messages.success(request, f'Thank you! Your review for {doctor.name} has been saved.')
    return redirect('reviews')


def blog_view(request):
    category = request.GET.get('category', 'All').strip()
    date_filter = request.GET.get('date_range', 'All').strip()
    keyword = request.GET.get('keyword', '').strip()

    posts_qs = BlogPost.objects.all()

    if category and category != 'All':
        posts_qs = posts_qs.filter(category__iexact=category)

    if date_filter == 'Feb-May':
        posts_qs = posts_qs.filter(published_date__month__gte=2, published_date__month__lte=5)
    elif date_filter == 'Jun-Dec':
        posts_qs = posts_qs.filter(published_date__month__gte=6, published_date__month__lte=12)

    if keyword:
        posts_qs = posts_qs.filter(
            Q(title__icontains=keyword)
            | Q(excerpt__icontains=keyword)
            | Q(category__icontains=keyword)
        )

    paginator = Paginator(posts_qs, 4)
    page_obj = paginator.get_page(request.GET.get('page', 1))

    categories = list(
        BlogPost.objects.values_list('category', flat=True).distinct().order_by('category')
    )

    return render(
        request,
        'core/blog.html',
        {
            'active_nav': 'blog',
            'page_obj': page_obj,
            'categories': categories,
            'selected_category': category,
            'selected_date_range': date_filter,
            'keyword': keyword,
        },
    )


def blog_detail_view(request, slug):
    post = get_object_or_404(BlogPost, slug=slug)
    related_posts = BlogPost.objects.exclude(pk=post.pk)[:2]
    return render(
        request,
        'core/blog_detail.html',
        {'active_nav': 'blog', 'post': post, 'related_posts': related_posts},
    )
