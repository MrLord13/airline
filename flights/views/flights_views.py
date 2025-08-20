from django.shortcuts import render
from django.http import JsonResponse
from django.contrib import messages

from appuser.models import AdminUser, CrewMember
from flights.models import Flights, FlightCrews
from django.db.models import Q
import datetime


# Create your views here.
def flights(request):
    if request.user.is_authenticated and request.user.is_active:
        data = {}
        data['page_title'] = 'Flights'
        data['breadcrumbs'] = [{'text': 'Flights', 'url': '/dashboard/flights/'}]

        return render(request, 'panel/flights.html', data)


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
        if request.user.is_superuser or request.user.is_staff:
            flights = Flights.objects
        else:
            flights = Flights.objects.filter(flightcrews__user=request.user)

        search = request.POST.get('search[value]', None)
        if search is not None:
            flights = flights.filter(
                Q(origin__contains=search) |
                Q(destination__contains=search) |
                Q(flight_no__contains=search) |
                Q(airline_name__contains=search) |
                Q(airline_code__contains=search) |
                Q(airline_type__contains=search) |
                Q(flight_date__contains=search) |
                Q(arrive_date__contains=search) |
                Q(flight_time__contains=search) |
                Q(flight_permit__contains=search)
            )
        airline_search = request.POST.get('columns[1][search][value]', '').replace('\\', '')
        if len(airline_search) > 0:
            flights = flights.filter(airline_name=airline_search)

        origin_search = request.POST.get('columns[2][search][value]', '').replace('\\', '')
        if len(origin_search) > 0:
            flights = flights.filter(origin=origin_search)

        destination_search = request.POST.get('columns[3][search][value]', '').replace('\\', '')
        if len(destination_search) > 0:
            flights = flights.filter(destination=destination_search)

        airline_code_search = request.POST.get('columns[4][search][value]', '').replace('\\', '')
        if len(airline_code_search) > 0:
            flights = flights.filter(airline_code=airline_code_search)

        date_search = date_filter(request.POST.get('columns[5][search][value]', '').replace('\\', ''))
        if len(date_search) > 0:
            flights = flights.filter(flight_date__gte=date_search[0], flight_date__lte=date_search[1])

        date_search = date_filter(request.POST.get('columns[6][search][value]', '').replace('\\', ''))
        if len(date_search) > 0:
            flights = flights.filter(arrive_date__gte=date_search[0], arrive_date__lte=date_search[1])

        permit_search = request.POST.get('columns[8][search][value]', '').replace('\\', '')
        if len(permit_search) > 0:
            flights = flights.filter(flight_permit=permit_search)

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
        if order_type == 'asc':
            flights = flights.order_by(f'-{order_mapping[order]}')
        else:
            flights = flights.order_by(f'{order_mapping[order]}')

        page_size = int(request.POST.get('length', 10))
        page_start = int(request.POST.get('start', 0))
        data = {
            "draw": int(request.POST.get('draw', 1)),
            "recordsTotal": flights.count(),
            "recordsFiltered": flights.count(),
            "data": [
            ]
        }
        flights = flights.all()[page_start:page_start + page_size]

        for flight in flights:
            print(flight.flightcrews_set)
            data['data'].append(
                {
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
                    # 'status':1
                })
        return JsonResponse(data, content_type='application/json', status=200)
    else:
        return
        return JsonResponse({'message': "Method is invalid."}, content_type='application/json', status=400)


def create_flight(request):
    if request.method == 'POST' and request.user.is_authenticated and request.user.is_active and (
            request.user.is_superuser or request.user.is_staff):
        origin = str(request.POST.get('origin', ''))
        if len(origin) == 0:
            return JsonResponse({'message': 'origin is empty.'}, status=400)

        destination = str(request.POST.get('destination', ''))
        if len(destination) == 0:
            return JsonResponse({'message': 'Destination is empty.'}, status=400)

        flight_no = str(request.POST.get('flight_no', ''))
        if len(flight_no) == 0:
            return JsonResponse({'message': 'Flight number is empty.'}, status=400)

        if str(request.POST.get('flight_no_old', '')) != flight_no and Flights.objects.filter(
                flight_no=flight_no).count() > 0:
            return JsonResponse({'message': 'Flight number is duplicated.'}, status=400)

        airline_name = str(request.POST.get('airline_name', ''))
        if len(airline_name) == 0:
            return JsonResponse({'message': 'Airline Name is empty.'}, status=400)

        airline_code = str(request.POST.get('airline_code', ''))
        if len(airline_code) == 0:
            return JsonResponse({'message': 'Airline Code is empty.'}, status=400)

        airline_type = str(request.POST.get('airline_type', ''))
        if len(airline_type) == 0:
            return JsonResponse({'message': 'Airline Type is empty.'}, status=400)

        flight_date = str(request.POST.get('flight_date', ''))
        try:
            flight_date = datetime.datetime.strptime(flight_date, '%Y-%m-%d %H:%M')
        except ValueError:
            return JsonResponse({'message': 'Flight date is invalid.'}, status=400)

        arrive_date = str(request.POST.get('arrive_date', ''))
        try:
            arrive_date = datetime.datetime.strptime(arrive_date, '%Y-%m-%d %H:%M')
        except ValueError:
            return JsonResponse({'message': 'Arrive date is invalid.'}, status=400)

        if arrive_date <= flight_date:
            return JsonResponse({'message': 'Arrive date is invalid.'}, status=400)

        flight_permit = str(request.POST.get('flight_permit', ''))
        if flight_permit not in ['PPL', 'CPL', 'ATPL', 'HPL', 'GPL']:
            return JsonResponse({'message': 'Flight Permit is invalid.'}, status=400)

        dif_time = arrive_date - flight_date
        flight_time = ''

        days = dif_time.days
        hours = int(dif_time.total_seconds() // 3600)
        minutes = int((dif_time.total_seconds() % 3600) // 60)
        if minutes < 10:
            flight_time = f'0{minutes}'
        else:
            flight_time = minutes
        if hours < 10:
            flight_time = f'0{hours}:{flight_time}'
        else:
            flight_time = f'{hours}:{flight_time}'

        if days > 1:
            flight_time = f'{days} Days and {flight_time}'
        elif days == 1:
            flight_time = f'{days} Day and {flight_time}'
        flight_date = flight_date.strftime('%Y-%m-%d %H:%M')
        arrive_date = arrive_date.strftime('%Y-%m-%d %H:%M')
        try:
            if str(request.POST.get('flight_no_old', '')) != 'null':
                flight = Flights.objects.filter(flight_no=str(request.POST.get('flight_no_old', '')))[0]
                flight.origin = origin
                flight.destination = destination
                flight.airline_name = airline_name
                flight.airline_code = airline_code
                flight.airline_type = airline_type
                flight.flight_date = flight_date
                flight.arrive_date = arrive_date
                flight.flight_time = flight_time
                flight.flight_permit = flight_permit
                flight.save()
            else:
                Flights.objects.create(
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
                    status='SCHEDULED',
                    total_seats=None  # Set to None since it's optional
                )
            return JsonResponse({'message': 'success', 'flight_no': flight_no}, status=200)
        except Exception as e:
            return JsonResponse({'message': f'Unknown error occurred: {str(e)}'}, status=400)
    return JsonResponse({'message': 'Request type is invalid.'}, status=400)


def get_crews(request):
    if request.method == 'POST' and request.user.is_authenticated and request.user.is_active:
        flight_no = request.POST.get('flight_no', '')
        data = {
            'flight_no': flight_no,
            'Flight_PI': [],
            'Flight_CO_PI': [],
            'Flight_FL_EN': [],
            'Flight_FL_ATE': [],
            'PI': [],
            'CO_PI': [],
            'FL_EN': [],
            'FL_ATE': [],
        }

        if Flights.objects.filter(pk=flight_no).count() == 1:
            if not request.user.is_superuser and not request.user.is_staff and FlightCrews.objects.filter(
                    flight_id=flight_no, user_id=request.user.id).count() == 0:
                return JsonResponse({'message': 'Request is invalid.'}, status=400)

            # Get existing crew assignments for this flight
            crews = FlightCrews.objects.filter(flight_id=flight_no)
            for crew in crews:
                if crew.role == 'PI':
                    data['Flight_PI'].append(crew.crew_member.id)
                elif crew.role == 'CO-PI':
                    data['Flight_CO_PI'].append(crew.crew_member.id)
                elif crew.role == 'FL-EN':
                    data['Flight_FL_EN'].append(crew.crew_member.id)
                elif crew.role == 'FL-ATE':
                    data['Flight_FL_ATE'].append(crew.crew_member.id)

            # Get available crew members for each role
            for crew in CrewMember.objects.filter(role='PI', is_active=True):
                data['PI'].append(
                    {'id': crew.id, 'name': f"{crew.first_name} {crew.last_name} (L:{crew.expertise_level})"})

            for crew in CrewMember.objects.filter(role='CO-PI', is_active=True):
                data['CO_PI'].append(
                    {'id': crew.id, 'name': f"{crew.first_name} {crew.last_name} (L:{crew.expertise_level})"})

            for crew in CrewMember.objects.filter(role='FL-EN', is_active=True):
                data['FL_EN'].append(
                    {'id': crew.id, 'name': f"{crew.first_name} {crew.last_name} (L:{crew.expertise_level})"})

            for crew in CrewMember.objects.filter(role='FL-ATE', is_active=True):
                data['FL_ATE'].append(
                    {'id': crew.id, 'name': f"{crew.first_name} {crew.last_name} (L:{crew.expertise_level})"})
            
            return JsonResponse(data, status=200)
        else:
            return JsonResponse({'message': 'Flight is invalid.'}, status=400)
    return JsonResponse({'message': 'Request is invalid.'}, status=400)


def update_crews(request):
    if request.method == 'POST' and request.user.is_authenticated and request.user.is_active and (
            request.user.is_superuser or request.user.is_staff):
        flight_no = request.POST.get('flight_no', '')
        if Flights.objects.filter(pk=flight_no).count() == 1:
            FlightCrews.objects.filter(flight_id=flight_no).delete()
            if request.POST.get('pi', '').isnumeric():
                crew = CrewMember.objects.get(id=request.POST.get('pi'))
                FlightCrews.objects.create(flight_id=flight_no, crew_member=crew, role='PI')
            if request.POST.get('co-pi', '').isnumeric():
                crew = CrewMember.objects.get(id=request.POST.get('co-pi'))
                FlightCrews.objects.create(flight_id=flight_no, crew_member=crew, role='CO-PI')
            if request.POST.get('en', '').isnumeric():
                crew = CrewMember.objects.get(id=request.POST.get('en'))
                FlightCrews.objects.create(flight_id=flight_no, crew_member=crew, role='FL-EN')
            crews = request.POST.get('crews', '').split(',')
            for crew_id in crews:
                if crew_id.isnumeric():
                    crew = CrewMember.objects.get(id=crew_id)
                    FlightCrews.objects.create(flight_id=flight_no, crew_member=crew, role='FL-ATE')
            return JsonResponse({'message': "Saved successfully."}, status=200)
        else:
            return JsonResponse({'message': 'Flight is invalid.'}, status=400)
    else:
        return JsonResponse({'message': 'Request is invalid.'}, status=400)


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
