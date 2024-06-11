from datetime import (
    timedelta,
    datetime,
    timezone
)
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.reverse import reverse
from rest_framework.test import APIClient
from rest_framework import status
from airport_api.models import (
    Country,
    City,
    Order,
    Ticket,
    Flight,
    Airplane,
    AirplaneType,
    Crew,
    Route,
    Airport,
)
from airport_api.serializers import (
    TicketListSerializer,
    TicketRetrieveSerializer
)

TICKET_URL = reverse("api_airport:ticket-list")


def detail_url(ticket_id):
    return reverse("api_airport:ticket-detail", args=[ticket_id])


class UnauthenticatedTicketApiTests(TestCase):

    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(TICKET_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedTicketApiTests(
    TestCase
):  # Same permissions for admin and user (if It's user's own ticket)
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="Test@test.test",
            password="Testpsw1"
        )
        self.client.force_authenticate(self.user)
        self.country_1 = Country.objects.create(
            name="Randon Country 1"
        )
        self.country_2 = Country.objects.create(
            name="Randon Country 2"
        )
        self.city_1 = City.objects.create(
            name="Random City 1",
            country=self.country_1
        )
        self.city_2 = City.objects.create(
            name="Random City 2",
            country=self.country_2
        )
        self.airport_1 = Airport.objects.create(
            name="Airport Name 1",
            closest_big_city=self.city_1
        )
        self.airport_2 = Airport.objects.create(
            name="Airport Name 2",
            closest_big_city=self.city_2
        )

        self.route_1 = Route.objects.create(
            source=self.airport_1,
            destination=self.airport_2,
            distance=700.0
        )
        self.route_2 = Route.objects.create(
            source=self.airport_2,
            destination=self.airport_1,
            distance=700.0
        )
        self.crew_member1 = Crew.objects.create(
            first_name="Qwerty",
            last_name="Johnson",
            flying_hours=0.0
        )
        self.crew_member2 = Crew.objects.create(
            first_name="John",
            last_name="Qwerty",
            flying_hours=0.0
        )

        self.crew_member3 = Crew.objects.create(
            first_name="Bob",
            last_name="Miles",
            flying_hours=0.0
        )
        self.crew_member4 = Crew.objects.create(
            first_name="Alex",
            last_name="Ferg"
        )
        self.airplanetype_1 = AirplaneType.objects.create(
            name="Airplane Type 1"
        )
        self.airplanetype_2 = AirplaneType.objects.create(
            name="Airplane Type 2"
        )
        self.airplane_1 = Airplane.objects.create(
            name="Airplane Name 1",
            rows=55,
            seats_in_row=10,
            airplane_type=self.airplanetype_1,
        )
        self.airplane_2 = Airplane.objects.create(
            name="Airplane Name 2",
            rows=80,
            seats_in_row=10,
            airplane_type=self.airplanetype_2,
        )

        departure_time = datetime.now(timezone.utc)
        arrival_time = departure_time + timedelta(hours=2)

        self.flight_1 = Flight.objects.create(
            route=self.route_1,
            airplane=self.airplane_1,
            departure_time=departure_time,
            arrival_time=arrival_time,
        )
        self.flight_1.crews.add(self.crew_member1, self.crew_member2)

        self.flight_2 = Flight.objects.create(
            route=self.route_2,
            airplane=self.airplane_2,
            departure_time=departure_time + timedelta(
                days=1,
                hours=1,
                minutes=10
            ),
            arrival_time=arrival_time + timedelta(
                days=1,
                hours=2
            ),
        )
        self.flight_2.crews.add(self.crew_member3, self.crew_member4)

        self.order_1 = Order.objects.create(user=self.user)
        self.order_2 = Order.objects.create(user=self.user)
        self.ticket_1 = Ticket.objects.create(
            row=7,
            seat=7,
            flight=self.flight_1,
            order=self.order_1
        )
        self.ticket_2 = Ticket.objects.create(
            row=5,
            seat=5,
            flight=self.flight_2,
            order=self.order_2
        )

    def test_ticket_list(self):
        res = self.client.get(TICKET_URL)
        tickets = Ticket.objects.all()
        serializer = TicketListSerializer(tickets, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_filter_tickets_by_range_of_ids(self):
        res = self.client.get(TICKET_URL, data={"id": "1-3"})
        serializer_1 = TicketListSerializer(self.ticket_1)
        serializer_2 = TicketListSerializer(self.ticket_2)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(serializer_1.data, res.data["results"])
        self.assertIn(serializer_2.data, res.data["results"])

    def test_filter_ticket_by_flight_info(self):
        res = self.client.get(TICKET_URL, data={"route": "Name 1"})
        serializer_1 = TicketListSerializer(self.ticket_1)
        serializer_2 = TicketListSerializer(self.ticket_2)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(serializer_1.data, res.data["results"])
        self.assertIn(serializer_2.data, res.data["results"])

    def test_retrieve_ticket_detail(self):
        res = self.client.get(detail_url(self.ticket_1.id))
        serializer = TicketRetrieveSerializer(self.ticket_1)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_update_ticket(self):
        payload = {
            "row": 7,
            "seat": 9,
            "flight": self.flight_1.id
        }

        res = self.client.put(
            detail_url(
                self.ticket_1.id
            ), payload, format="json"
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_delete_ticket(self):
        res = self.client.delete(detail_url(self.ticket_1.id))
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

    def test_get_invalid_ticket(self):
        invalid_id = self.ticket_2.id + 1
        res = self.client.get(detail_url(invalid_id))
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
