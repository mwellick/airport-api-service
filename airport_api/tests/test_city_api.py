from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.reverse import reverse
from rest_framework.test import APIClient
from rest_framework import status
from airport_api.models import Country, City
from airport_api.serializers import (
    CityListSerializer,
    CityRetrieveSerializer
)

CITY_URL = reverse("api_airport:city-list")


def detail_url(city_id):
    return reverse("api_airport:city-detail", args=[city_id])


class UnauthenticatedCityApiTests(TestCase):

    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(CITY_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedCityApiTests(TestCase):

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
            name="Country 2"
        )
        self.city_1 = City.objects.create(
            name="Random city",
            country=self.country_1
        )
        self.city_2 = City.objects.create(
            name="City",
            country=self.country_2
        )

    def test_city_list(self):
        res = self.client.get(CITY_URL)
        cities = City.objects.all()
        serializer = CityListSerializer(cities, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_filter_city_by_name(self):
        res = self.client.get(CITY_URL, data={"name": "Rando"})
        serializer1 = CityListSerializer(self.city_1)
        serializer2 = CityListSerializer(self.city_2)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(serializer1.data, res.data["results"])
        self.assertNotIn(serializer2.data, res.data["results"])

    def test_retrieve_city_detail(self):
        res = self.client.get(detail_url(self.city_1.id))
        serializer = CityRetrieveSerializer(self.city_1)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_city_forbidden(self):
        payload = {
            "name": "Test city",
            "country": self.country_1
        }
        res = self.client.post(CITY_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_city_forbidden(self):
        res = self.client.put(detail_url(self.city_1.id))
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_city_forbidden(self):
        res = self.client.delete(detail_url(self.city_1.id))
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminCityTests(TestCase):

    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test_admin@admin.com",
            password="Testadminpsw",
            is_staff=True
        )
        self.client.force_authenticate(self.user)

        self.country_1 = Country.objects.create(
            name="Randon Country 1"
        )
        self.country_2 = Country.objects.create(
            name="Country 2"
        )
        self.city_1 = City.objects.create(
            name="Random city",
            country=self.country_1
        )
        self.city_2 = City.objects.create(
            name="City",
            country=self.country_2
        )

    def test_create_city(self):
        payload = {
            "name": "Name",
            "country": self.country_1.id
        }
        res = self.client.post(CITY_URL, payload)
        city = City.objects.get(id=res.data["id"])
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(City.objects.count(), 3)

        for key in payload:
            if key == "country":
                city_id = getattr(city, key).id
                self.assertEqual(payload[key], city_id)
            else:
                self.assertEqual(payload[key], getattr(city, key))

    def test_update_city(self):
        payload = {
            "name": "Updated Name",
            "country": self.country_1.id
        }
        res = self.client.put(
            detail_url(
                self.city_1.id
            ), payload
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        city = City.objects.get(id=self.city_1.id)
        for key in payload:
            if key == "country":
                city_id = getattr(city, key).id
                self.assertEqual(payload[key], city_id)
            else:
                self.assertEqual(payload[key], getattr(city, key))

    def test_delete_city(self):
        res = self.client.delete(detail_url(self.city_1.id))
        self.assertEqual(City.objects.count(), 1)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

    def test_get_invalid_city(self):
        invalid_id = self.city_2.id + 1
        res = self.client.get(detail_url(invalid_id))
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
