from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing_view, name='landing'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('appointments/', views.appointments_view, name='appointments'),
    path('appointments/book/', views.book_appointment_view, name='book_appointment'),
    path('appointments/slots/', views.available_slots_api, name='available_slots'),
    path('appointments/<int:appointment_id>/cancel/', views.cancel_appointment_view, name='cancel_appointment'),
    path('my-appointments/', views.my_appointments_view, name='my_appointments'),
    path('reviews/', views.reviews_view, name='reviews'),
    path('reviews/submit/', views.submit_review_view, name='submit_review'),
    path('blog/', views.blog_view, name='blog'),
    path('blog/<slug:slug>/', views.blog_detail_view, name='blog_detail'),
]
