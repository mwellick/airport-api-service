from .models import Flight

from celery import shared_task


@shared_task
def update_flying_hours() -> None:
    flights = Flight.objects.filter(accounted=False)
    for flight in flights:
        if flight.flight_is_over:
            flight_duration = flight.arrival_time - flight.departure_time
            hours_flight_time = flight_duration.total_seconds() / 3600
            hours_flight_time = round(hours_flight_time, 2)
            for crew in flight.crews.all():
                crew.flying_hours += hours_flight_time

                crew.save()
            flight.accounted = True
            flight.save()
