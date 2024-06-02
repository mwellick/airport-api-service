from datetime import datetime, timedelta, timezone

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.reverse import reverse
from rest_framework.test import APIClient
from rest_framework import status
from airport_api.models import Route, Airport, Airplane, Crew, Flight, AirplaneType
from airport_api.serializers import FlightListSerializer, FlightRetrieveSerializer
from airport_api.tasks import update_flying_hours

FLIGHT_URL = reverse("api_airport:flight-list")


def detail_url(flight_id):
    return reverse("api_airport:flight-detail", args=[flight_id])


class UnauthenticatedFlightApiTests(TestCase):

    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(FLIGHT_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedFlightApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="Test@test.test",
            password="Testpsw1"
        )
        self.client.force_authenticate(self.user)
        self.airport_1 = Airport.objects.create(
            name="Airport Name 1",
            closest_big_city="Random City 1"
        )
        self.airport_2 = Airport.objects.create(
            name="Airport Name 2",
            closest_big_city="Random City 2"
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
            airplane_type=self.airplanetype_1

        )
        self.airplane_2 = Airplane.objects.create(
            name="Airplane Name 2",
            rows=80,
            seats_in_row=10,
            airplane_type=self.airplanetype_2
        )

        departure_time = datetime.now(timezone.utc)
        arrival_time = departure_time + timedelta(hours=2)

        self.flight_1 = Flight.objects.create(
            route=self.route_1,
            airplane=self.airplane_1,
            departure_time=departure_time,
            arrival_time=arrival_time
        )
        self.flight_1.crews.add(self.crew_member1, self.crew_member2)

        self.flight_2 = Flight.objects.create(
            route=self.route_2,
            airplane=self.airplane_2,
            departure_time=departure_time + timedelta(days=1, hours=1, minutes=10),
            arrival_time=arrival_time + timedelta(days=1, hours=2)
        )
        self.flight_2.crews.add(self.crew_member3, self.crew_member4)

    def test_flight_list(self):
        res = self.client.get(FLIGHT_URL)
        flights = Flight.objects.all()
        serializer = FlightListSerializer(flights, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_filter_flight_by_id(self):
        res = self.client.get(FLIGHT_URL, data={"id": 1})
        serializer_1 = FlightListSerializer(self.flight_1)
        serializer_2 = FlightListSerializer(self.flight_2)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(serializer_1.data, res.data["results"])
        self.assertNotIn(serializer_2.data, res.data["results"])

    def test_filter_flight_by_source(self):
        res = self.client.get(FLIGHT_URL, data={"from": "name 1"})
        serializer_1 = FlightListSerializer(self.flight_1)
        serializer_2 = FlightListSerializer(self.flight_2)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(serializer_1.data, res.data["results"])
        self.assertNotIn(serializer_2.data, res.data["results"])

    def test_filter_flight_by_destination(self):
        res = self.client.get(FLIGHT_URL, data={"to": "name 2"})
        serializer_1 = FlightListSerializer(self.flight_1)
        serializer_2 = FlightListSerializer(self.flight_2)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(serializer_1.data, res.data["results"])
        self.assertNotIn(serializer_2.data, res.data["results"])

    def test_filter_flight_by_plane_name(self):
        res = self.client.get(FLIGHT_URL, data={"plane_name": "Name 1"})
        serializer_1 = FlightListSerializer(self.flight_1)
        serializer_2 = FlightListSerializer(self.flight_2)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(serializer_1.data, res.data["results"])
        self.assertNotIn(serializer_2.data, res.data["results"])

    def test_filter_by_departure_date(self):
        departure_date = self.flight_1.departure_time.date()
        formatted_date = departure_date.strftime("%Y-%m-%d")
        res = self.client.get(FLIGHT_URL, data={"departure_date": formatted_date})
        serializer_1 = FlightListSerializer(self.flight_1)
        serializer_2 = FlightListSerializer(self.flight_2)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(serializer_1.data, res.data["results"])
        self.assertNotIn(serializer_2.data, res.data["results"])

    def test_filter_flight_by_departure_hour(self):
        departure_hour = self.flight_2.departure_time.hour
        res = self.client.get(FLIGHT_URL, data={"departure_hour": departure_hour})
        serializer_1 = FlightListSerializer(self.flight_1)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        for result in res.data["results"]:
            self.assertEqual(result, serializer_1.data)

    def test_filter_flight_by_departure_minute(self):
        departure_minute = self.flight_2.departure_time.minute
        res = self.client.get(FLIGHT_URL, data={"departure_hour": departure_minute})
        serializer_1 = FlightListSerializer(self.flight_1)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        for result in res.data["results"]:
            self.assertEqual(result, serializer_1.data)

    def test_filter_by_arrival_date(self):
        arrival_date = self.flight_1.arrival_time.date()
        formatted_date = arrival_date.strftime("%Y-%m-%d")
        res = self.client.get(FLIGHT_URL, data={"arrival_date": formatted_date})
        serializer_1 = FlightListSerializer(self.flight_1)
        serializer_2 = FlightListSerializer(self.flight_2)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(serializer_1.data, res.data["results"])
        self.assertNotIn(serializer_2.data, res.data["results"])

    def test_filter_flight_by_arrival_hour(self):
        arrival_hour = self.flight_2.arrival_time.hour
        res = self.client.get(FLIGHT_URL, data={"arrival_hour": arrival_hour})
        serializer_1 = FlightListSerializer(self.flight_1)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        for result in res.data["results"]:
            self.assertEqual(result, serializer_1.data)

    def test_filter_flight_by_arrival_minute(self):
        arrival_minute = self.flight_2.arrival_time.minute
        res = self.client.get(FLIGHT_URL, data={"arrival_hour": arrival_minute})
        serializer_1 = FlightListSerializer(self.flight_1)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        for result in res.data["results"]:
            self.assertEqual(result, serializer_1.data)

    def test_retrieve_flight_detail(self):
        res = self.client.get(detail_url(self.flight_1.id))
        serializer = FlightRetrieveSerializer(self.flight_1)
        added_data = serializer.data
        added_data["tickets_available"] = 550
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, added_data)

    def test_create_flight_forbidden(self):
        payload = {
            "route": self.route_2,
            "airplane": self.airplane_1,
            "crews": [self.crew_member2, self.crew_member4],
            "departure_time": "2024-06-27T12:00:00Z",
            "arrival_time": "2024-06-27T14:00:00Z"

        }
        res = self.client.post(FLIGHT_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_flight_forbidden(self):
        res = self.client.put(detail_url(self.flight_1.id))
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_flight_forbidden(self):
        res = self.client.delete(detail_url(self.flight_1.id))
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminFlightTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="Test@test.test",
            password="Testpsw1",
            is_staff=True
        )
        self.client.force_authenticate(self.user)
        self.airport_1 = Airport.objects.create(
            name="Airport Name 1",
            closest_big_city="Random City 1"
        )
        self.airport_2 = Airport.objects.create(
            name="Airport Name 2",
            closest_big_city="Random City 2"
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
            airplane_type=self.airplanetype_1

        )
        self.airplane_2 = Airplane.objects.create(
            name="Airplane Name 2",
            rows=80,
            seats_in_row=10,
            airplane_type=self.airplanetype_2
        )

        departure_time = datetime.now(timezone.utc)
        arrival_time = departure_time + timedelta(hours=2)

        self.flight_1 = Flight.objects.create(
            route=self.route_1,
            airplane=self.airplane_1,
            departure_time=departure_time,
            arrival_time=arrival_time
        )
        self.flight_1.crews.add(self.crew_member1, self.crew_member2)

        self.flight_2 = Flight.objects.create(
            route=self.route_2,
            airplane=self.airplane_2,
            departure_time=departure_time + timedelta(days=1, hours=1, minutes=10),
            arrival_time=arrival_time + timedelta(days=1, hours=2)
        )
        self.flight_2.crews.add(self.crew_member3, self.crew_member4)

    def test_create_flight(self):
        payload = {
            "route": self.route_2.id,
            "airplane": self.airplane_1.id,
            "crews": [self.crew_member2.id, self.crew_member4.id],
            "departure_time": "2024-06-27T12:00:00Z",
            "arrival_time": "2024-06-27T14:00:00Z"

        }
        res = self.client.post(FLIGHT_URL, payload)
        flight = Flight.objects.get(id=res.data["id"])
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Flight.objects.count(), 3)

        for key in payload:
            if key == "route":
                self.assertEqual(payload[key], getattr(flight, f"{key}_id"))
            elif key == "airplane":
                self.assertEqual(payload[key], getattr(flight, f"{key}_id"))
            elif key == "crews":
                crew_ids = list(flight.crews.values_list("id", flat=True))
                self.assertEqual(payload[key], crew_ids)
            elif key in ["departure_time", "arrival_time"]:
                expected_date = datetime.strptime(payload[key], "%Y-%m-%dT%H:%M:%SZ")
                expected_date = expected_date.replace(tzinfo=timezone.utc)
                self.assertEqual(expected_date, getattr(flight, key))
            else:
                self.assertEqual(payload[key], getattr(flight, key))

    def test_update_flight(self):
        payload = {
            "route": self.route_2.id,
            "airplane": self.airplane_1.id,
            "crews": [self.crew_member2.id, self.crew_member4.id],
            "departure_time": "2024-06-27T12:00:00Z",
            "arrival_time": "2024-06-27T14:00:00Z"

        }
        res = self.client.put(detail_url(self.flight_1.id), payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        flight = Flight.objects.get(id=res.data["id"])
        for key in payload:
            if key == "route":
                self.assertEqual(payload[key], getattr(flight, f"{key}_id"))
            elif key == "airplane":
                self.assertEqual(payload[key], getattr(flight, f"{key}_id"))
            elif key == "crews":
                crew_ids = list(flight.crews.values_list("id", flat=True))
                self.assertEqual(payload[key], crew_ids)
            elif key in ["departure_time", "arrival_time"]:
                expected_date = datetime.strptime(payload[key], "%Y-%m-%dT%H:%M:%SZ")
                expected_date = expected_date.replace(tzinfo=timezone.utc)
                self.assertEqual(expected_date, getattr(flight, key))
            else:
                self.assertEqual(payload[key], getattr(flight, key))

    def test_delete_flight(self):
        res = self.client.delete(detail_url(self.flight_1.id))
        self.assertEqual(Flight.objects.count(), 1)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

    def test_get_invalid_flight(self):
        invalid_id = self.flight_2.id + 1
        res = self.client.get(detail_url(invalid_id))
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
