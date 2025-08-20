from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from appuser.models import CrewMember
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.db.models import Q

# Expertise level mapping
EXPERTISE_LEVELS = {
    1: 'Level 1',
    2: 'Level 2',
    3: 'Level 3',
    4: 'Level 4',
    5: 'Level 5'
}

@login_required
def crews(request):
    if request.user.is_superuser:
        data = {}
        data['page_title'] = 'Crews'
        data['breadcrumbs'] = [{'text': 'Crews', 'url': '/dashboard/crews/'}]
        return render(request, 'panel/crews.html', data)
    else:
        return HttpResponseForbidden("You don't have permission to access this page.")

@login_required
def crew_data(request):
    if request.method == 'GET' and request.user.is_authenticated and request.user.is_active:
        if request.user.is_superuser or request.user.is_staff:
            crews = CrewMember.objects
        else:
            crews = CrewMember.objects.filter(user=request.user)

        search = request.GET.get('search[value]', None)
        if search is not None:
            crews = crews.filter(
                Q(first_name__contains=search) |
                Q(last_name__contains=search) |
                Q(email__contains=search) |
                Q(role__contains=search) |
                Q(expertise_level__contains=search)
            )

        role_search = request.GET.get('columns[4][search][value]', '').replace('\\', '')
        if len(role_search) > 0:
            crews = crews.filter(role=role_search)

        level_search = request.GET.get('columns[5][search][value]', '').replace('\\', '')
        if len(level_search) > 0:
            crews = crews.filter(expertise_level=level_search)

        order = request.GET.get('order[0][column]', '0')
        order_type = request.GET.get('order[0][dir]', 'asc')
        order_mapping = {
            '0': 'id',
            '1': 'first_name',
            '2': 'last_name',
            '3': 'email',
            '4': 'role',
            '5': 'expertise_level',
            '6': 'is_active'
        }
        if order_type == 'asc':
            crews = crews.order_by(f'-{order_mapping[order]}')
        else:
            crews = crews.order_by(f'{order_mapping[order]}')

        page_size = int(request.GET.get('length', 10))
        page_start = int(request.GET.get('start', 0))
        data = {
            "draw": int(request.GET.get('draw', 1)),
            "recordsTotal": crews.count(),
            "recordsFiltered": crews.count(),
            "data": []
        }
        crews = crews.all()[page_start:page_start + page_size]

        for crew in crews:
            data['data'].append({
                'ID': crew.id,
                'First Name': crew.first_name,
                'Last Name': crew.last_name,
                'Email': crew.email,
                'Role': crew.role,
                'Expertise Level': crew.expertise_level,
                'Status': 'Active' if crew.is_active else 'Inactive'
            })
        return JsonResponse(data, content_type='application/json', status=200)
    else:
        return JsonResponse({'message': "Method is invalid."}, content_type='application/json', status=400)

@csrf_exempt
@login_required
def create_crew(request):
    if request.method == 'POST' and request.user.is_superuser:
        try:
            first_name = request.POST.get('first_name', '').strip()
            last_name = request.POST.get('last_name', '').strip()
            email = request.POST.get('email', '').strip()
            phone_number = request.POST.get('phone_number', '').strip()
            role = request.POST.get('role', '').strip()
            expertise_level = request.POST.get('expertise_level', '').strip()
            location = request.POST.get('location', '').strip()
            availability_time = request.POST.get('availability_time', '').strip()
            description = request.POST.get('description', '').strip()
            is_active = request.POST.get('is_active') == 'true'

            # Validate required fields
            if not email:
                return JsonResponse({'message': 'Email is required.'}, status=400)
            if not role:
                return JsonResponse({'message': 'Role is required.'}, status=400)
            if not expertise_level:
                return JsonResponse({'message': 'Expertise level is required.'}, status=400)

            try:
                expertise_level = int(expertise_level)
                if expertise_level not in EXPERTISE_LEVELS:
                    return JsonResponse({'message': 'Invalid expertise level.'}, status=400)
            except ValueError:
                return JsonResponse({'message': 'Expertise level must be a number.'}, status=400)

            # Check if email already exists
            if CrewMember.objects.filter(email=email).exists():
                return JsonResponse({'message': 'Email already exists.'}, status=400)

            # Create new crew member
            crew = CrewMember.objects.create(
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone_number=phone_number,
                role=role,
                expertise_level=expertise_level,
                location=location,
                availability_time=availability_time,
                description=description,
                is_active=is_active
            )

            return JsonResponse({
                'message': 'Crew member created successfully.',
                'id': crew.id
            }, status=201)

        except Exception as e:
            return JsonResponse({
                'message': f'An error occurred while creating crew member: {str(e)}'
            }, status=500)

    return JsonResponse({'message': 'Invalid request.'}, status=400)

@csrf_exempt
@login_required
def update_crew(request):
    if request.method == 'POST' and request.user.is_superuser:
        try:
            crew_id = request.POST.get('id')
            if not crew_id:
                return JsonResponse({'message': 'Crew ID is required.'}, status=400)

            try:
                crew = CrewMember.objects.get(id=crew_id)
            except CrewMember.DoesNotExist:
                return JsonResponse({'message': 'Crew member not found.'}, status=404)

            new_email = request.POST.get('email', '').strip()
            expertise_level = request.POST.get('expertise_level', '').strip()

            # Validate expertise level
            try:
                expertise_level = int(expertise_level)
                if expertise_level not in EXPERTISE_LEVELS:
                    return JsonResponse({'message': 'Invalid expertise level.'}, status=400)
            except ValueError:
                return JsonResponse({'message': 'Expertise level must be a number.'}, status=400)

            # Check if email exists for other users
            if CrewMember.objects.exclude(id=crew_id).filter(email=new_email).exists():
                return JsonResponse({'message': 'Email already exists.'}, status=400)

            crew.first_name = request.POST.get('first_name', crew.first_name).strip()
            crew.last_name = request.POST.get('last_name', crew.last_name).strip()
            crew.email = new_email
            crew.phone_number = request.POST.get('phone_number', crew.phone_number).strip()
            crew.role = request.POST.get('role', crew.role).strip()
            crew.expertise_level = expertise_level
            crew.location = request.POST.get('location', crew.location).strip()
            crew.availability_time = request.POST.get('availability_time', crew.availability_time).strip()
            crew.description = request.POST.get('description', crew.description).strip()
            crew.is_active = request.POST.get('is_active') == 'true'

            crew.save()
            return JsonResponse({'message': 'Crew member updated successfully.'}, status=200)
            
        except Exception as e:
            return JsonResponse({'message': f'An error occurred: {str(e)}'}, status=500)
            
    return JsonResponse({'message': 'Invalid request.'}, status=400)

@csrf_exempt
@login_required
def delete_crew(request):
    if request.method == 'POST' and request.user.is_superuser:
        crew_id = request.POST.get('id')
        try:
            crew = CrewMember.objects.get(id=crew_id)
            crew.delete()
            return JsonResponse({'message': 'Crew member deleted successfully.'}, status=200)
        except CrewMember.DoesNotExist:
            return JsonResponse({'message': 'Crew member not found.'}, status=404)
    return JsonResponse({'message': 'Invalid request.'}, status=400)

@login_required
def get_crew_details(request):
    if request.method == 'GET' and request.user.is_superuser:
        crew_id = request.GET.get('id')
        try:
            crew = CrewMember.objects.get(id=crew_id)
            data = {
                'ID': crew.id,
                'First Name': crew.first_name,
                'Last Name': crew.last_name,
                'Email': crew.email,
                'Phone Number': crew.phone_number,
                'Role': crew.role,
                'Expertise Level': str(crew.expertise_level),
                'Location': crew.location,
                'Availability Time': crew.availability_time,
                'Description': crew.description,
                'Status': 'Active' if crew.is_active else 'Disabled'
            }
            return JsonResponse(data, status=200)
        except CrewMember.DoesNotExist:
            return JsonResponse({'message': 'Crew member not found.'}, status=404)
    return JsonResponse({'message': 'Invalid request.'}, status=400)

@login_required
def manage_users(request):
    if request.method == 'POST':
        user_id = request.POST.get('id', '')
        if user_id:
            user = CrewMember.objects.get(id=user_id)
        else:
            user = CrewMember()
        
        # Validate email uniqueness
        email = request.POST.get('email', '')
        if user_id:
            old_email = CrewMember.objects.filter(email=email).exclude(id=user_id).count()
        else:
            old_email = CrewMember.objects.filter(email=email).count()
        
        if old_email > 0:
            messages.error(request, 'Email already exists')
            return redirect('manage_users')
        
        # Update user fields
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = email
        user.role = request.POST.get('role', '')
        user.phone_number = request.POST.get('phone_number', '')
        user.availability_time = request.POST.get('availability_time', '')
        user.location = request.POST.get('location', '')
        user.description = request.POST.get('description', '')
        user.is_active = request.POST.get('is_active', '') == 'on'
        
        user.save()
        messages.success(request, 'User saved successfully')
        return redirect('manage_users')
        
    users = CrewMember.objects.all()
    return render(request, 'appuser/manage_users.html', {'users': users})

@login_required
def view_user(request, user_id):
    user = CrewMember.objects.get(id=user_id)
    return render(request, 'appuser/view_user.html', {'user': user}) 