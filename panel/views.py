from django.shortcuts import render, redirect
from django.db.models import Count
from django.db.models.functions import TruncMonth
from appuser.models import AdminUser, CrewMember
from flights.models import Flights, FlightCrews
from datetime import datetime, timedelta
import json
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.urls import reverse
from django.http import JsonResponse

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'panel/login.html')

def logout_view(request):
    logout(request)
    return redirect('login_page')

def dashboard(request):
    if request.user.is_authenticated and request.user.is_active:
        context = {
            'page_title': 'Dashboard',
            'breadcrumbs': [{'text': 'Dashboard', 'url': '/dashboard'}]
        }

        try:
            # User Statistics
            total_users = CrewMember.objects.all().count()
            
            active_users = CrewMember.objects.filter(is_active=True).count()
            
            # Debug prints
            print(f"Total Users: {total_users}")
            print(f"Active Users: {active_users}")
            
            context['user_stats'] = {
                'total': total_users,
                'active': active_users,
                'roles': list(CrewMember.objects.values('role').annotate(count=Count('id')).order_by('role'))
            }

            # Flight Statistics
            total_flights = Flights.objects.all().count()
            upcoming_flights = Flights.objects.filter(flight_date__gte=datetime.now().date()).count()
            
            # Debug prints
            print(f"Total Flights: {total_flights}")
            print(f"Upcoming Flights: {upcoming_flights}")
            
            context['flight_stats'] = {
                'total': total_flights,
                'upcoming': upcoming_flights,
                'statuses': list(FlightCrews.objects.values('status').annotate(count=Count('id')).order_by('status'))
            }

            # Monthly Flight Statistics for last 12 months
            end_date = datetime.now()
            start_date = end_date - timedelta(days=365)  # 12 months ago
            
            monthly_data = Flights.objects.filter(
                flight_date__range=(start_date, end_date)
            ).annotate(
                month=TruncMonth('flight_date')
            ).values('month').annotate(
                count=Count('flight_no')
            ).order_by('month')

            # Generate complete monthly data
            all_months = []
            flight_counts = []
            current_date = start_date
            
            while current_date <= end_date:
                month_str = current_date.strftime('%b %Y')
                all_months.append(month_str)
                
                # Find count for this month
                month_count = next(
                    (item['count'] for item in monthly_data 
                    if item['month'].strftime('%b %Y') == month_str),
                    0
                )
                flight_counts.append(month_count)
                
                current_date = (current_date.replace(day=1) + timedelta(days=32)).replace(day=1)

            context['monthly_stats'] = {
                'labels': all_months,
                'data': flight_counts
            }

            # Debug print final context
            print("Context Data:", json.dumps(context, indent=2, default=str))

            return render(request, 'panel/dashboard.html', context)
            
        except Exception as e:
            print(f"Error in dashboard view: {str(e)}")
            # Return empty stats in case of error
            context['user_stats'] = {'total': 0, 'active': 0, 'roles': []}
            context['flight_stats'] = {'total': 0, 'upcoming': 0, 'statuses': []}
            context['monthly_stats'] = {'labels': [], 'data': []}
            return render(request, 'panel/dashboard.html', context)
            
    return render(request, 'panel/login.html')

@login_required
def profile(request):
    context = {
        'page_title': 'Profile',
        'breadcrumbs': [
            {'text': 'Dashboard', 'url': reverse('dashboard')},
            {'text': 'Profile', 'url': None}
        ]
    }
    
    # Check if user is superadmin and trying to view another user's profile
    if request.user.is_superuser and 'id' in request.GET:
        try:
            user_id = request.GET.get('id')
            user_to_show = AdminUser.objects.get(id=user_id)
            context['user_to_show'] = user_to_show
        except AdminUser.DoesNotExist:
            messages.error(request, 'User not found.')
            return redirect('profile')
    else:
        context['user_to_show'] = request.user
    
    return render(request, 'panel/profile.html', context)

@login_required
def update_profile(request):
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        
        if not request.user.check_password(current_password):
            return JsonResponse({'success': False, 'message': 'Current password is incorrect.'}, status=400)
        
        request.user.set_password(new_password)
        request.user.save()
        
        # Update session to prevent logout
        update_session_auth_hash(request, request.user)
        
        return JsonResponse({'success': True, 'message': 'Password changed successfully!'})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method.'}, status=400) 