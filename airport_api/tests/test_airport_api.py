from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.reverse import reverse
from rest_framework.test import APIClient
from rest_framework import status
from airport_api.models import Airport
from airport_api.serializers import AirportListSerializer, AirportRetrieveSerializer

AIRPORT_URL = reverse("api_airport:airport-list")


def detail_url(airport_id):
    return reverse("api_airport:airport-detail", args=[airport_id])


class UnauthenticatedAirportApiTests(TestCase):

    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(AIRPORT_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedAirportApiTests(TestCase):

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

    def test_airport_list(self):
        res = self.client.get(AIRPORT_URL)
        airports = Airport.objects.all()
        serializer = AirportListSerializer(airports, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_filter_airport_by_name(self):
        res = self.client.get(AIRPORT_URL, data={"name": "Name 1"})
        serializer1 = AirportListSerializer(self.airport_1)
        serializer2 = AirportListSerializer(self.airport_2)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(serializer1.data, res.data["results"])
        self.assertNotIn(serializer2.data, res.data["results"])

    def test_retrieve_airport_detail(self):
        res = self.client.get(detail_url(self.airport_1.id))
        serializer = AirportRetrieveSerializer(self.airport_1)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_airport_forbidden(self):
        payload = {
            "name": "Name",
            "closest_big_city": "City"
        }
        res = self.client.post(AIRPORT_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_airport_forbidden(self):
        res = self.client.put(detail_url(self.airport_1.id))
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_airport_forbidden(self):
        res = self.client.delete(detail_url(self.airport_1.id))
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminAirportTests(TestCase):

    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test_admin@admin.com",
            password="Testadminpsw",
            is_staff=True
        )
        self.client.force_authenticate(self.user)

        self.airport_1 = Airport.objects.create(
            name="Airport Name 1",
            closest_big_city="Random City 1"
        )

    def test_create_airport(self):
        payload = {
            "name": "Name",
            "closest_big_city": "City"
        }
        res = self.client.post(AIRPORT_URL, payload)

        airport = Airport.objects.get(id=res.data["id"])
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Airport.objects.count(), 2)

        for key in payload:
            self.assertEqual(payload[key], getattr(airport, key))

    def test_update_airport(self):
        payload = {
            "name": "Updated Name",
            "closest_big_city": "Updated City"
        }
        res = self.client.put(detail_url(self.airport_1.id), payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        airport = Airport.objects.get(id=res.data["id"])
        for key in payload:
            self.assertEqual(payload[key], getattr(airport, key))

    def test_delete_airport(self):
        res = self.client.delete(detail_url(self.airport_1.id))
        self.assertEqual(Airport.objects.count(), 0)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

    def test_get_invalid_airport(self):
        invalid_id = self.airport_1.id + 1
        res = self.client.get(detail_url(invalid_id))
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
