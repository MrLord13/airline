from django.shortcuts import render
from django.http import JsonResponse
from django.contrib import messages
from django.conf import settings
from django.shortcuts import get_object_or_404, render
from appuser.models import AdminUser, CrewMember
from flights.models import Flights, FlightCrews 
from django.db.models import Q
import datetime
from datetime import timedelta
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import make_aware
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt





# Create your views here.
def flights(request):
    if request.user.is_authenticated and request.user.is_active:
        data = {}
        data['page_title'] = 'Flights'
        data['breadcrumbs'] = [{'text': 'Flights', 'url': '/dashboard/flights/'}]

        return render(request, 'panel/flights.html', data)


# To connect the history view to the template(panel/crew_summary.html), do this:
def crew_summary_page(request):
    if request.user.is_authenticated and request.user.is_active:
        crew_members = CrewMember.objects.filter(is_active=True)
        return render(request, 'panel/crew_summary.html', {'crew_members': crew_members})
    return redirect('login')


def flight_info(request):
    if request.user.is_authenticated and request.user.is_active:
        data = {}
        if request.method == 'POST' and request.POST.get('flight_no', None):
            flight = None
            if request.user.is_superuser or request.user.is_staff:
                flight = Flights.objects.get(flight_no=request.POST.get('flight_no', None))
            elif FlightCrews.objects.filter(flight_id=request.POST.get('flight_no', None),
                                            user_id=request.user.id).count() > 0:
                flight = Flights.objects.get(flight_no=request.POST.get('flight_no', None))
            if flight:
                data['flight_no'] = flight.flight_no
                data['origin'] = flight.origin
                data['destination'] = flight.destination
                data['airline_name'] = flight.airline_name
                data['airline_code'] = flight.airline_code
                data['airline_type'] = flight.airline_type
                data['flight_date'] = flight.flight_date.strftime('%Y-%m-%d %H:%M')
                data['arrive_date'] = flight.arrive_date.strftime('%Y-%m-%d %H:%M')
                data['flight_permit'] = flight.flight_permit
                return JsonResponse(data, status=200)
            else:
                return JsonResponse({'message': 'Flight not found.'}, status=404)
        else:
            return JsonResponse({'message': 'Flight not found.'}, status=404)


def date_filter(date):
    now = datetime.datetime.now()
    if date == 'n-3-m':
        other = now + datetime.timedelta(days=61)
        return [now.strftime("%Y-%m-%d"), other.strftime("%Y-%m-%d")]
    elif date == 'n-1-m':
        other = now + datetime.timedelta(days=31)
        return [now.strftime("%Y-%m-%d"), other.strftime("%Y-%m-%d")]
    elif date == 'n-1-w':
        other = now + datetime.timedelta(days=80)
        return [now.strftime("%Y-%m-%d"), other.strftime("%Y-%m-%d")]
    elif date == 'now':
        other = now + datetime.timedelta(days=1)
        return [now.strftime("%Y-%m-%d"), other.strftime("%Y-%m-%d")]
    elif date == 'l-1-w':
        other = now - datetime.timedelta(days=7)
        return [other.strftime("%Y-%m-%d"), now.strftime("%Y-%m-%d")]
    elif date == 'l-1-m':
        other = now - datetime.timedelta(days=30)
        return [other.strftime("%Y-%m-%d"), now.strftime("%Y-%m-%d")]
    elif date == 'l-3-m':
        other = now - datetime.timedelta(days=90)
        return [other.strftime("%Y-%m-%d"), now.strftime("%Y-%m-%d")]
    elif date == 'l-6-m':
        other = now - datetime.timedelta(days=6 * 30)
        return [other.strftime("%Y-%m-%d"), now.strftime("%Y-%m-%d")]
    elif date == 'l-1-y':
        other = now - datetime.timedelta(days=12 * 30)
        return [other.strftime("%Y-%m-%d"), now.strftime("%Y-%m-%d")]
    else:
        return []


def data_tables(request):
    if request.method == 'POST' and request.user.is_authenticated and request.user.is_active:
        try:
            if request.user.is_superuser or request.user.is_staff:
                flights = Flights.objects
            else:
                flights = Flights.objects.filter(flightcrews__user=request.user)

            search = request.POST.get('search[value]', None)
            if search:
                flights = flights.filter(
                    Q(origin__icontains=search) |
                    Q(destination__icontains=search) |
                    Q(flight_no__icontains=search) |
                    Q(airline_name__icontains=search) |
                    Q(airline_code__icontains=search) |
                    Q(airline_type__icontains=search) |
                    Q(flight_date__icontains=search) |
                    Q(arrive_date__icontains=search) |
                    Q(flight_time__icontains=search) |
                    Q(flight_permit__icontains=search)
                )

            # فیلترهای ستونی
            if (val := request.POST.get('columns[1][search][value]', '').strip()):
                flights = flights.filter(airline_name=val)

            if (val := request.POST.get('columns[2][search][value]', '').strip()):
                flights = flights.filter(origin=val)

            if (val := request.POST.get('columns[3][search][value]', '').strip()):
                flights = flights.filter(destination=val)

            if (val := request.POST.get('columns[4][search][value]', '').strip()):
                flights = flights.filter(airline_code=val)

            if (val := request.POST.get('columns[5][search][value]', '').strip()):
                date_range = date_filter(val)
                if date_range:
                    flights = flights.filter(flight_date__range=date_range)

            if (val := request.POST.get('columns[6][search][value]', '').strip()):
                date_range = date_filter(val)
                if date_range:
                    flights = flights.filter(arrive_date__range=date_range)

            if (val := request.POST.get('columns[8][search][value]', '').strip()):
                flights = flights.filter(flight_permit=val)

            order = request.POST.get('order[0][column]', '0')
            order_type = request.POST.get('order[0][dir]', 'asc')
            order_mapping = {
                '0': 'flight_no',
                '1': 'airline_name',
                '2': 'origin',
                '3': 'destination',
                '4': 'airline_code',
                '5': 'flight_date',
                '6': 'arrive_date',
                '7': 'flight_time',
                '8': 'flight_permit'
            }

            order_field = order_mapping.get(order, 'flight_no')
            if order_type == 'asc':
                flights = flights.order_by(order_field)
            else:
                flights = flights.order_by(f'-' + order_field)

            # صفحه‌بندی
            page_size = int(request.POST.get('length', 10))
            page_start = int(request.POST.get('start', 0))

            total = flights.count()
            flights = flights.all()[page_start:page_start + page_size]

            data = {
                "draw": int(request.POST.get('draw', 1)),
                "recordsTotal": total,
                "recordsFiltered": total,
                "data": []
            }

            for flight in flights:
                data['data'].append({
                    'Flight NO': flight.flight_no,
                    'Airline': flight.airline_name,
                    'Origin': flight.origin,
                    'Destination': flight.destination,
                    'Airline Code': flight.airline_code,
                    'Type': flight.airline_type,
                    'Date': flight.flight_date.strftime('%Y-%m-%d %H:%M'),
                    'Arrive': flight.arrive_date.strftime('%Y-%m-%d %H:%M'),
                    'Flight Time': flight.flight_time,
                    'Permit': flight.flight_permit,
                })

            return JsonResponse(data, content_type='application/json', status=200)

        except Exception as e:
            return JsonResponse({'message': f'Server error: {str(e)}'}, content_type='application/json', status=500)

    return JsonResponse({'message': "Method is invalid."}, content_type='application/json', status=400)



#A portion of the flight hours restrictions are recorded here for each crew member and sent to View(update_crew). It is reviewed here, and flight information is not recorded here until the crew member section is approved.
def create_flight(request):
    

    FLIGHT_PERMIT_LIMITS = {
        'PPL': 8,
        'CPL': 14,
        'ATPL': 14,
        'HPL': 8,
        'GPL': 5
    }

    max_flight_duty_period = 14

    if request.method == 'POST' and request.user.is_authenticated and request.user.is_active and (
        request.user.is_superuser or request.user.is_staff
    ):
        try:
            origin = request.POST.get('origin', '').strip()
            destination = request.POST.get('destination', '').strip()
            flight_no = request.POST.get('flight_no', '').strip()
            airline_name = request.POST.get('airline_name', '').strip()
            airline_code = request.POST.get('airline_code', '').strip()
            airline_type = request.POST.get('airline_type', '').strip()
            flight_permit = request.POST.get('flight_permit', '').strip()
            flight_date_str = request.POST.get('flight_date', '').strip()
            arrive_date_str = request.POST.get('arrive_date', '').strip()

            required_fields = {
                "origin": origin,
                "destination": destination,
                "flight_no": flight_no,
                "airline_name": airline_name,
                "airline_code": airline_code,
                "airline_type": airline_type,
                "flight_permit": flight_permit,
                "flight_date": flight_date_str,
                "arrive_date": arrive_date_str,
            }

            missing_fields = [key for key, val in required_fields.items() if not val]
            if missing_fields:
               return JsonResponse({'message': f'The following required fields are missing: {", ".join(missing_fields)}'}, status=400)


            if flight_permit not in FLIGHT_PERMIT_LIMITS:
                return JsonResponse({'message': 'Flight permit is invalid.'}, status=400)

            if Flights.objects.filter(flight_no=flight_no).exists():
                return JsonResponse({'message': 'Flight number already exists.'}, status=400)

            flight_date = datetime.datetime.strptime(flight_date_str, '%Y-%m-%d %H:%M')
            arrive_date = datetime.datetime.strptime(arrive_date_str, '%Y-%m-%d %H:%M')

            if arrive_date <= flight_date:
                return JsonResponse({'message': 'Arrive time must be after departure time.'}, status=400)

            flight_hours = (arrive_date - flight_date).total_seconds() / 3600
            if flight_hours > max_flight_duty_period:
                return JsonResponse({'message': f'Flight time exceeds max duty period ({max_flight_duty_period}h).'}, status=400)

           
            hours = int(flight_hours)
            minutes = int((flight_hours - hours) * 60)
            flight_time = f"{hours:02d}:{minutes:02d}"

           
            flight = Flights.objects.create(
                origin=origin,
                destination=destination,
                flight_no=flight_no,
                airline_name=airline_name,
                airline_code=airline_code,
                airline_type=airline_type,
                flight_date=flight_date,
                arrive_date=arrive_date,
                flight_time=flight_time,
                flight_permit=flight_permit,
                total_seats=None,
                status='DRAFT'
            )

            return JsonResponse({'message': 'The flight has been saved as a draft.', 'flight_no': flight_no}, status=200)

        except Exception as e:
            return JsonResponse({'message': f'A system error occurred: {str(e)}'}, status=400)
    return JsonResponse({'message': 'Invalid request.'}, status=400)





#Flight restrictions are being reviewed in this section.
def get_crews(request):
    if request.method != 'POST' or not request.user.is_authenticated or not request.user.is_active:
        return JsonResponse({'message': 'Request is invalid.'}, status=400)

    flight_no = request.POST.get('flight_no', '')
    if not Flights.objects.filter(pk=flight_no).exists():
        return JsonResponse({'message': 'Flight is invalid.'}, status=400)

    flight = Flights.objects.get(pk=flight_no)
    flight_day = flight.flight_date.date()
    flight_hours = (flight.arrive_date - flight.flight_date).total_seconds() / 3600

    def is_available(crew):
        overlapping = Flights.objects.filter(
            flightcrews__crew_member=crew,
            flight_date__lt=flight.arrive_date,
            arrive_date__gt=flight.flight_date
        ).exclude(flight_no=flight.flight_no).exists()

        if overlapping:
            return False

        def calc_hours(start, end):
            flights = Flights.objects.filter(
                flightcrews__crew_member=crew,
                flight_date__date__gte=start,
                flight_date__date__lte=end
            ).exclude(flight_no=flight.flight_no)
            return sum((f.arrive_date - f.flight_date).total_seconds() / 3600 for f in flights)

        # Information collection for each crew role is taken here.
        if calc_hours(flight_day, flight_day) + flight_hours > 8:
            return False
        if calc_hours(flight_day - timedelta(days=6), flight_day) + flight_hours > 60:
            return False
        if calc_hours(flight_day - timedelta(days=27), flight_day) + flight_hours > 112:
            return False
        if calc_hours(flight_day.replace(month=1, day=1), flight_day) + flight_hours > 1000:
            return False

        return True

    def get_crew(role_code, flight_role_key):
        available = []
        assigned_ids = []

        crews = FlightCrews.objects.filter(flight_id=flight_no, role=flight_role_key)
        for fc in crews:
            assigned_ids.append(fc.crew_member.id)

        for crew in CrewMember.objects.filter(role=role_code, is_active=True):
            if is_available(crew) or crew.id in assigned_ids:
                available.append({
                    'id': crew.id,
                    'name': f"{crew.first_name} {crew.last_name} (L:{crew.expertise_level})"
                })

        return available, assigned_ids

    data = {
        'flight_no': flight_no,
    }

    # Information collection for each crew role is taken here.
    data['PI'], data['Flight_PI'] = get_crew('PI', 'PI')
    data['CO_PI'], data['Flight_CO_PI'] = get_crew('CO-PI', 'CO-PI')
    data['FL_EN'], data['Flight_FL_EN'] = get_crew('FL-EN', 'FL-EN')
    data['FL_ATE'], data['Flight_FL_ATE'] = get_crew('FL-ATE', 'FL-ATE')

    return JsonResponse(data, status=200)



#Here, the hours of restrictions are checked and error management is performed, and if flight hours are calculated.

def update_crews(request):
    if request.method != 'POST' or not request.user.is_authenticated or not request.user.is_active or not (request.user.is_superuser or request.user.is_staff):
        return JsonResponse({'message': 'Invalid request.'}, status=400)

    flight_no = request.POST.get('flight_no', '').strip()
    if not flight_no or not Flights.objects.filter(flight_no=flight_no).exists():
        return JsonResponse({'message': 'Flight not found.'}, status=400)

    flight = Flights.objects.get(flight_no=flight_no)
    flight_day = flight.flight_date.date()
    flight_hours = (flight.arrive_date - flight.flight_date).total_seconds() / 3600

    
    pi_id = request.POST.get('pi', '').strip()
    co_pi_id = request.POST.get('co-pi', '').strip()
    en_id = request.POST.get('en', '').strip()
    fl_ates_str = request.POST.get('crews', '').strip()
    fl_ates = fl_ates_str.split(',') if fl_ates_str else []

   
    if not (pi_id.isnumeric() and co_pi_id.isnumeric() and en_id.isnumeric()):
        return JsonResponse({'message': 'Pilot, co-pilot, and flight engineer must be selected.'}, status=400)


    crew_ids = [pi_id, co_pi_id, en_id] + [cid for cid in fl_ates if cid.isnumeric()]
    crew_ids = list(set(crew_ids)) 

    crew_members = CrewMember.objects.filter(id__in=crew_ids)
    if crew_members.count() != len(crew_ids):
        return JsonResponse({'message': 'Some crew members are invalid.'}, status=400)

 
    def calc_total_hours(crew, start_date, end_date):
        flights = Flights.objects.filter(
            flightcrews__crew_member=crew,
            flight_date__date__gte=start_date,
            flight_date__date__lte=end_date
        ).exclude(flight_no=flight.flight_no).distinct()
        return sum((f.arrive_date - f.flight_date).total_seconds() / 3600 for f in flights)

    for crew in crew_members:
        overlapping_flights = Flights.objects.filter(
                flightcrews__crew_member=crew,
                flight_date__lt=flight.arrive_date,
                arrive_date__gt=flight.flight_date
            ).exclude(flight_no=flight.flight_no)

        if overlapping_flights.exists():
                return JsonResponse({
                    'message': f"{crew} has overlapping flights at the same time."
                }, status=400)

        total_day = calc_total_hours(crew, flight_day, flight_day)
        if total_day + flight_hours > 8:
            return JsonResponse({
                'message': f"{crew} exceeds the daily limit of 8 hours. Current hours: {total_day:.1f}h + {flight_hours:.1f}h"
            }, status=400)

        
        week_start = flight_day - timedelta(days=6)
        total_week = calc_total_hours(crew, week_start, flight_day)
        if total_week + flight_hours > 60:
            return JsonResponse({
                'message': f"{crew} exceeds the weekly limit of 60 hours. Current: {total_week:.1f}h + {flight_hours:.1f}h"
            }, status=400)

        
        month_28_start = flight_day - timedelta(days=27)
        total_28_days = calc_total_hours(crew, month_28_start, flight_day)
        if total_28_days + flight_hours > 112:
            return JsonResponse({
                'message': f"{crew} exceeds the 28-day limit (112 hours). Current: {total_28_days:.1f}h + {flight_hours:.1f}h"
            }, status=400)

        
        year_start = flight_day.replace(month=1, day=1)
        total_year = calc_total_hours(crew, year_start, flight_day)
        if total_year + flight_hours > 1000:
            return JsonResponse({
                'message': f"{crew} exceeds the annual limit (1000 hours). Current: {total_year:.1f}h + {flight_hours:.1f}h"
            }, status=400)

    
    FlightCrews.objects.filter(flight=flight).delete()

    def assign_role(crew_id, role):
        try:
            crew = CrewMember.objects.get(id=crew_id)
            FlightCrews.objects.create(flight=flight, crew_member=crew, role=role)
        except CrewMember.DoesNotExist:
            pass

    assign_role(pi_id, 'PI')
    assign_role(co_pi_id, 'CO-PI')
    assign_role(en_id, 'FL-EN')
    for crew_id in fl_ates:
        if crew_id.isnumeric():
            assign_role(crew_id, 'FL-ATE')

    
    if FlightCrews.objects.filter(flight=flight).count() < 3:
        return JsonResponse({'message': 'At least 3 main crew members must be registered.'}, status=400)


    flight.status = 'SCHEDULED'
    flight.save()

    return JsonResponse({'message': 'Saved successfully.'}, status=200)




  
def get_filters(request):
    if request.method == 'POST':
        data = {
            'origin': [],
            'destination': [],
            'airline': [],
            'airline_code': [],
        }

        for row in Flights.objects.values_list('origin', flat=True).distinct()[:50]:
            data['origin'].append(row)

        for row in Flights.objects.values_list('destination', flat=True).distinct()[:50]:
            data['destination'].append(row)

        for row in Flights.objects.values_list('airline_name', flat=True).distinct()[:50]:
            data['airline'].append(row)

        for row in Flights.objects.values_list('airline_code', flat=True).distinct()[:50]:
            data['airline_code'].append(row)

        return JsonResponse(data, status=200)
    else:
        return JsonResponse({'message': 'Request type is invalid.'}, status=400)


def flight_delete(request):
    if request.method == 'POST' and request.user.is_authenticated and request.user.is_active and (
            request.user.is_superuser or request.user.is_staff):
        flight_no = request.POST.get('id', '')
        if flight_no != '':
            user = Flights.objects.get(flight_no=flight_no)
            try:
                user.delete()
                return JsonResponse({'message': 'Successfully Deleted.'}, status=200)
            except:
                pass
    return JsonResponse({'message': 'Request type is invalid.'}, status=500)


def assign_crew(request, flight_id):
    flight = Flights.objects.get(flight_no=flight_id)
    
    pilots = CrewMember.objects.filter(role='PI', is_active=True)
    co_pilots = CrewMember.objects.filter(role='CO-PI', is_active=True)
    flight_engineers = CrewMember.objects.filter(role='FL-EN', is_active=True)
    flight_attendants = CrewMember.objects.filter(role='FL-ATE', is_active=True)
    
    return render(request, 'flights/assign_crew.html', {
        'flight': flight,
        'pilots': pilots,
        'co_pilots': co_pilots,
        'flight_engineers': flight_engineers,
        'flight_attendants': flight_attendants
    })



@csrf_exempt
def available_crew(request):
    if request.method != 'POST':
        return JsonResponse({'message': 'Invalid request method'}, status=400)

    try:
        flight_id = request.POST.get('flight_id', '')
        if not flight_id:
            return JsonResponse({'message': 'Flight ID is required'}, status=400)

        flight = Flights.objects.get(id=flight_id)
        flight_start = flight.flight_date
        flight_end = flight.arrive_date

        overlapping = Flights.objects.filter(
            flightcrews__crew_member__isnull=False,
            flight_date__lt=flight_end,
            arrive_date__gt=flight_start
        ).exclude(id=flight.id).values_list('flightcrews__crew_member_id', flat=True)

        available_crew = CrewMember.objects.exclude(id__in=overlapping).filter(is_active=True)

        crew_list = [
            {
                'id': c.id,
                'name': f"{c.first_name} {c.last_name}",
                'role': c.get_role_display()
            }
            for c in available_crew
        ]

        return JsonResponse({'crew': crew_list}, status=200)

    except Flights.DoesNotExist:
        return JsonResponse({'message': 'Flight not found'}, status=404)
    except Exception as e:
        return JsonResponse({'message': f'Error: {str(e)}'}, status=500)





# The section displays the history of each crew based on the user's selection in the selected time period of flight hours and calculates the remaining hours.
@csrf_exempt
def crew_flight_summary(request):
    if request.method == 'POST' and request.user.is_authenticated and request.user.is_active:
        try:
            crew_id = request.POST.get('crew_id')
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')

            if not crew_id or not start_date or not end_date:
                return JsonResponse({'message': 'All fields are required.'}, status=400)

            try:
                crew = CrewMember.objects.get(pk=crew_id)
            except CrewMember.DoesNotExist:
                return JsonResponse({'message': 'Crew member not found.'}, status=404)

            try:
                start_dt = make_aware(datetime.datetime.strptime(start_date, '%Y-%m-%d'))
                end_dt = make_aware(datetime.datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1))
            except ValueError:
                return JsonResponse({'message': 'Invalid date format. Use YYYY-MM-DD.'}, status=400)

           
            flights = Flights.objects.filter(
                flightcrews__crew_member=crew,
                flight_date__gte=start_dt,
                flight_date__lt=end_dt
            ).distinct()

            total_hours = 0
            flight_list = []
            for f in flights:
                duration = (f.arrive_date - f.flight_date).total_seconds() / 3600
                total_hours += duration
                flight_list.append({
                    'flight_no': f.flight_no,
                    'origin': f.origin,
                    'destination': f.destination,
                    'departure': f.flight_date.strftime('%Y-%m-%d %H:%M'),
                    'arrival': f.arrive_date.strftime('%Y-%m-%d %H:%M'),
                    'hours': f"{duration:.2f}"
                })

            
            now = end_dt
            period_starts = {
                'day': now - timedelta(days=1),
                'week': now - timedelta(days=7),
                '28_days': now - timedelta(days=28),
                'year': now - timedelta(days=365)
            }

            def get_hours_in_period(start, end):
                return sum(
                    (f.arrive_date - f.flight_date).total_seconds() / 3600
                    for f in Flights.objects.filter(
                        flightcrews__crew_member=crew,
                        flight_date__gte=start,
                        flight_date__lt=end
                    ).distinct()
                )

            # محاسبه ساعات در بازه‌های مختلف
            hours_day = get_hours_in_period(period_starts['day'], now)
            hours_week = get_hours_in_period(period_starts['week'], now)
            hours_28 = get_hours_in_period(period_starts['28_days'], now)
            hours_year = get_hours_in_period(period_starts['year'], now)

            
            limits = {
                'daily': 8,
                'weekly': 40,
                '28_days': 100,
                'year': 1000
            }

            summary = {
                'crew': str(crew),
                'role': crew.get_role_display() if hasattr(crew, 'get_role_display') else crew.role,
                'flight_permit': 'GENERAL',  # فرضی
                'date_range': f"{start_date} → {end_date}",
                'days': (end_dt.date() - start_dt.date()).days,
                'flights_count': len(flight_list),
                'total_hours_in_period': f"{total_hours:.2f}",

                # ساعات استفاده‌شده در هر بازه
                'used_daily': f"{hours_day:.2f}",
                'used_weekly': f"{hours_week:.2f}",
                'used_28_day': f"{hours_28:.2f}",
                'used_yearly': f"{hours_year:.2f}",

                # محدودیت‌ها
                'max_allowed_daily': limits['daily'],
                'max_allowed_weekly': limits['weekly'],
                'max_allowed_28_days': limits['28_days'],
                'max_allowed_yearly': limits['year'],

                # ساعات باقی‌مانده
                'remaining_daily': f"{limits['daily'] - hours_day:.2f}",
                'remaining_weekly': f"{limits['weekly'] - hours_week:.2f}",
                'remaining_28_day': f"{limits['28_days'] - hours_28:.2f}",
                'remaining_yearly': f"{limits['year'] - hours_year:.2f}",

                
                'flights': flight_list
            }

            return JsonResponse({'summary': summary}, status=200)

        except Exception as e:
            return JsonResponse({'message': f'Error: {str(e)}'}, status=500)

    return JsonResponse({'message': 'Unauthorized or invalid request.'}, status=403)