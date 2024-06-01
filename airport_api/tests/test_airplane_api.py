from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.reverse import reverse
from rest_framework.test import APIClient
from rest_framework import status
from airport_api.models import Airplane, AirplaneType
from airport_api.serializers import AirplaneListSerializer, AirplaneRetrieveSerializer

AIRPLANE_URL = reverse("api_airport:airplane-list")


def detail_url(airplane_id):
    return reverse("api_airport:airplane-detail", args=[airplane_id])


class UnauthenticatedAirplaneApiTests(TestCase):

    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(AIRPLANE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedAirplaneApiTests(TestCase):

    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="Test@test.test",
            password="Testpsw1"
        )
        self.client.force_authenticate(self.user)

        self.airplanetype_1 = AirplaneType.objects.create(
            name="Airplane Type 1"
        )
        self.airplanetype_2 = AirplaneType.objects.create(
            name="Airplane Type 2"
        )

        self.airplane_1 = Airplane.objects.create(
            name="Airplane Name 1",
            rows=200,
            seats_in_row=10,
            airplane_type=self.airplanetype_1

        )
        self.airplane_2 = Airplane.objects.create(
            name="Airplane Name 2",
            rows=80,
            seats_in_row=10,
            airplane_type=self.airplanetype_2
        )

    def test_airplane_list(self):
        res = self.client.get(AIRPLANE_URL)
        routes = Airplane.objects.all()
        serializer = AirplaneListSerializer(routes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_filter_airplane_by_name(self):
        res = self.client.get(AIRPLANE_URL, data={"name": "name 1"})
        serializer_1 = AirplaneListSerializer(self.airplane_1)
        serializer_2 = AirplaneListSerializer(self.airplane_2)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(serializer_1.data, res.data["results"])
        self.assertNotIn(serializer_2.data, res.data["results"])

    def test_retrieve_airplane_detail(self):
        res = self.client.get(detail_url(self.airplane_1.id))
        serializer = AirplaneRetrieveSerializer(self.airplane_1)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_airplane_forbidden(self):
        payload = {
            "name": "Name 3",
            "rows": 100,
            "seats_in_row": 10,
            "airplane_type": self.airplanetype_2
        }
        res = self.client.post(AIRPLANE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_airplane_forbidden(self):
        res = self.client.put(detail_url(self.airplane_1.id))
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_airplane_forbidden(self):
        res = self.client.delete(detail_url(self.airplane_1.id))
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminAirplaneTests(TestCase):

    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="Test@test.test",
            password="Testpsw1",
            is_staff=True
        )
        self.client.force_authenticate(self.user)

        self.airplanetype_1 = AirplaneType.objects.create(
            name="Airplane Type 1"
        )
        self.airplanetype_2 = AirplaneType.objects.create(
            name="Airplane Type 2"
        )

        self.airplane_1 = Airplane.objects.create(
            name="Airplane Name 1",
            rows=200,
            seats_in_row=10,
            airplane_type=self.airplanetype_1

        )
        self.airplane_2 = Airplane.objects.create(
            name="Airplane Name 2",
            rows=80,
            seats_in_row=10,
            airplane_type=self.airplanetype_2
        )

    def test_create_airplane(self):
        payload = {
            "name": "Name 3",
            "rows": 100,
            "seats_in_row": 10,
            "airplane_type": self.airplanetype_2.id
        }
        res = self.client.post(AIRPLANE_URL, payload)

        airplane = Airplane.objects.get(id=res.data["id"])

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Airplane.objects.count(), 3)

        for key in payload:
            if key == "airplane_type":
                self.assertEqual(payload[key], getattr(airplane, f"{key}_id"))
            else:
                self.assertEqual(payload[key], getattr(airplane, key))

    def test_update_airplane(self):
        payload = {
            "name": "Name 3",
            "rows": 100,
            "seats_in_row": 10,
            "airplane_type": self.airplanetype_2.id
        }
        res = self.client.put(detail_url(self.airplane_1.id), payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        airplane = Airplane.objects.get(id=res.data["id"])

        for key in payload:
            if key == "airplane_type":
                self.assertEqual(payload[key], getattr(airplane, f"{key}_id"))
            else:
                self.assertEqual(payload[key], getattr(airplane, key))

    def test_delete_airplane(self):
        res = self.client.delete(detail_url(self.airplane_2.id))
        self.assertEqual(Airplane.objects.count(), 1)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

    def test_get_invalid_airplane(self):
        invalid_id = self.airplane_2.id + 1
        res = self.client.get(detail_url(invalid_id))
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
