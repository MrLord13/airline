
from django.utils import timezone
from datetime import timedelta
from flights.models import Flights, FlightCrews


def delete_stale_drafts():
    
    print(">>> Running delete_stale_drafts task!")

    threshold = timezone.now() - timedelta(minutes=1)
    drafts = Flights.objects.filter(status='DRAFT', flight_date__lt=threshold)
    print(f"Found {drafts.count()} draft flights older than 1 minute")

    deleted_count = 0
    for flight in drafts:
        crew_exists = FlightCrews.objects.filter(flight=flight).exists()
        print(f"Flight {flight.flight_no}, crew assigned: {crew_exists}")
        if not crew_exists:
            flight.delete()
            print(f"Deleted flight {flight.flight_no}")
            deleted_count += 1

    print(f"✅ Total deleted: {deleted_count}")
