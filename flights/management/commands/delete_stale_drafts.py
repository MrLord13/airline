from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from flights.models import Flights, FlightCrews

#This section is for removing incomplete, canceled, and incorrectly registered flights, and must be enabled on the server.
class Command(BaseCommand):
    help = 'Deletes flights that are invalid or stale (e.g. draft older than 1 min with no crew).'

    def handle(self, *args, **kwargs):
        now = timezone.now()
        threshold = now - timedelta(minutes=1)

        
        drafts = Flights.objects.filter(status='DRAFT', flight_date__lt=threshold)

      
        cancelled = Flights.objects.filter(status='CANCELLED')

   
        past_invalid = Flights.objects.filter(flight_date__lt=now).exclude(status='CONFIRMED')

        flights_to_delete = drafts | cancelled | past_invalid
        deleted_count = 0

        for flight in flights_to_delete.distinct():
           
            if flight.status == 'DRAFT' and FlightCrews.objects.filter(flight=flight).exists():
                continue 

            flight.delete()
            deleted_count += 1

        self.stdout.write(f"✅ Deleted {deleted_count} invalid/stale flights.")
