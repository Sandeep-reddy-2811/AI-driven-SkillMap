from django.urls import path
from . import views

urlpatterns = [
    # GET /api/health/
    # React frontend pings this to check if backend is alive
    path('health/', views.health_check, name='health'),

    # POST /api/analyze/
    # Main endpoint — upload resume + JD, get back learning roadmap
    path('analyze/', views.analyze_and_generate, name='analyze'),
]