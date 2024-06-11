from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.reverse import reverse
from rest_framework.test import APIClient
from rest_framework import status
from airport_api.models import Country
from airport_api.serializers import (
    CountryListSerializer,
    CountryRetrieveSerializer
)

COUNTRY_URL = reverse("api_airport:country-list")


def detail_url(country_id):
    return reverse("api_airport:country-detail", args=[country_id])


class UnauthenticatedCountryApiTests(TestCase):

    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(COUNTRY_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedCountryApiTests(TestCase):

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

    def test_country_list(self):
        res = self.client.get(COUNTRY_URL)
        countries = Country.objects.all()
        serializer = CountryListSerializer(countries, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_filter_country_by_name(self):
        res = self.client.get(COUNTRY_URL, data={"name": "Country 1"})
        serializer1 = CountryListSerializer(self.country_1)
        serializer2 = CountryListSerializer(self.country_2)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(serializer1.data, res.data["results"])
        self.assertNotIn(serializer2.data, res.data["results"])

    def test_retrieve_country_detail(self):
        res = self.client.get(detail_url(self.country_1.id))
        serializer = CountryRetrieveSerializer(self.country_1)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_country_forbidden(self):
        payload = {
            "name": "Name"
        }
        res = self.client.post(COUNTRY_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_country_forbidden(self):
        res = self.client.put(detail_url(self.country_1.id))
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_country_forbidden(self):
        res = self.client.delete(detail_url(self.country_1.id))
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminCountryTests(TestCase):

    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test_admin@admin.com",
            password="Testadminpsw",
            is_staff=True
        )
        self.client.force_authenticate(self.user)

        self.country = Country.objects.create(
            name="Random Country"
        )

    def test_create_country(self):
        payload = {
            "name": "Name"
        }
        res = self.client.post(COUNTRY_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Country.objects.count(), 2)

    def test_update_country(self):
        payload = {
            "name": "Updated Name",
        }
        res = self.client.put(
            detail_url(
                self.country.id
            ), payload
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        country = Country.objects.get(id=self.country.id)
        for key in payload:
            self.assertEqual(payload[key], getattr(country, key))

    def test_delete_country(self):
        res = self.client.delete(detail_url(self.country.id))
        self.assertEqual(Country.objects.count(), 0)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

    def test_get_invalid_country(self):
        invalid_id = self.country.id + 1
        res = self.client.get(detail_url(invalid_id))
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
