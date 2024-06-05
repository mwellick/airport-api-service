from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.reverse import reverse
from rest_framework.test import APIClient
from rest_framework import status
from airport_api.models import AirplaneType
from airport_api.serializers import (
    AirplaneTypeListSerializer,
    AirplaneTypeRetrieveSerializer,
)

AIRPLANE_TYPE_URL = reverse("api_airport:airplanetype-list")


def detail_url(airplane_type_id):
    return reverse("api_airport:airplanetype-detail", args=[airplane_type_id])


class UnauthenticatedAirplaneTypeApiTests(TestCase):

    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(AIRPLANE_TYPE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedAirplaneTypetApiTests(TestCase):

    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="Test@test.test", password="Testpsw1"
        )
        self.client.force_authenticate(self.user)

        self.airplanetype_1 = AirplaneType.objects.create(name="Airplane Type 1")
        self.airplanetype_2 = AirplaneType.objects.create(name="Airplane Type 2")

    def test_airplane_type_list(self):
        res = self.client.get(AIRPLANE_TYPE_URL)
        airports = AirplaneType.objects.all()
        serializer = AirplaneTypeListSerializer(airports, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_filter_airplane_type_by_name(self):
        res = self.client.get(AIRPLANE_TYPE_URL, data={"name": "Type 1"})
        serializer1 = AirplaneTypeListSerializer(self.airplanetype_1)
        serializer2 = AirplaneTypeListSerializer(self.airplanetype_2)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(serializer1.data, res.data["results"])
        self.assertNotIn(serializer2.data, res.data["results"])

    def test_retrieve_airplane_type_detail(self):
        res = self.client.get(detail_url(self.airplanetype_1.id))
        serializer = AirplaneTypeRetrieveSerializer(self.airplanetype_1)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_airplane_type_forbidden(self):
        payload = {
            "name": "Airplane Type 2",
        }
        res = self.client.post(AIRPLANE_TYPE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_airplane_type_forbidden(self):
        res = self.client.put(detail_url(self.airplanetype_1.id))
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_airport_forbidden(self):
        res = self.client.delete(detail_url(self.airplanetype_2.id))
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminAirportTests(TestCase):

    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test_admin@admin.com", password="Testadminpsw", is_staff=True
        )
        self.client.force_authenticate(self.user)

        self.airplanetype_1 = AirplaneType.objects.create(name="Airplane Type 1")
        self.airplanetype_2 = AirplaneType.objects.create(name="Airplane Type 2")

    def test_create_airplane_type(self):
        payload = {"name": "Airplane Type 3"}
        res = self.client.post(AIRPLANE_TYPE_URL, payload)

        airport = AirplaneType.objects.get(id=res.data["id"])
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(AirplaneType.objects.count(), 3)

        for key in payload:
            self.assertEqual(payload[key], getattr(airport, key))

    def test_update_airplane_type(self):
        payload = {"name": "Updated Type"}
        res = self.client.put(detail_url(self.airplanetype_2.id), payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        airplane_type = AirplaneType.objects.get(id=self.airplanetype_2.id)
        for key in payload:
            self.assertEqual(payload[key], getattr(airplane_type, key))

    def test_delete_airplane_type(self):
        res = self.client.delete(detail_url(self.airplanetype_1.id))
        self.assertEqual(AirplaneType.objects.count(), 1)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

    def test_get_invalid_airplane_type(self):
        invalid_id = self.airplanetype_2.id + 1
        res = self.client.get(detail_url(invalid_id))
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
