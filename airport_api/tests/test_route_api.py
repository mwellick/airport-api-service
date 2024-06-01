from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.reverse import reverse
from rest_framework.test import APIClient
from rest_framework import status
from airport_api.models import Route, Airport
from airport_api.serializers import RouteListSerializer, RouteRetrieveSerializer

ROUTE_URL = reverse("api_airport:route-list")


def detail_url(route_id):
    return reverse("api_airport:route-detail", args=[route_id])


class UnauthenticatedRouteApiTests(TestCase):

    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(ROUTE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedRouteApiTests(TestCase):

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

    def test_route_list(self):
        res = self.client.get(ROUTE_URL)
        routes = Route.objects.all()
        serializer = RouteListSerializer(routes, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data["results"], serializer.data)

    def test_filter_route_by_source(self):
        res = self.client.get(ROUTE_URL, data={"from": "name 1"})
        serializer_1 = RouteListSerializer(self.route_1)
        serializer_2 = RouteListSerializer(self.route_2)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(serializer_1.data, res.data["results"])
        self.assertNotIn(serializer_2.data, res.data["results"])

    def test_filter_route_by_destination(self):
        res = self.client.get(ROUTE_URL, data={"to": "name 1"})
        serializer_1 = RouteListSerializer(self.route_1)
        serializer_2 = RouteListSerializer(self.route_2)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(serializer_2.data, res.data["results"])
        self.assertNotIn(serializer_1.data, res.data["results"])

    def test_retrieve_route_detail(self):
        res = self.client.get(detail_url(self.route_1.id))
        serializer = RouteRetrieveSerializer(self.route_1)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_route_forbidden(self):
        payload = {
            "source": "Name 3",
            "destination": "Name 2"
        }
        res = self.client.post(ROUTE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_route_forbidden(self):
        res = self.client.put(detail_url(self.route_1.id))
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_route_forbidden(self):
        res = self.client.delete(detail_url(self.route_1.id))
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminAirportTests(TestCase):

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
        self.airport_3 = Airport.objects.create(
            name="Airport Name 3",
            closest_big_city="Random City 3"
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

    def test_create_route(self):
        payload = {
            "source": self.airport_3.id,
            "destination": self.airport_1.id,
            "distance": 900.0
        }
        res = self.client.post(ROUTE_URL, payload)

        route = Route.objects.get(id=res.data["id"])

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Route.objects.count(), 3)

        for key in payload:
            if key == "source" or key == "destination":
                self.assertEqual(payload[key], getattr(route, f"{key}_id"))
            else:
                self.assertEqual(payload[key], getattr(route, key))

    def test_update_route(self):
        payload = {
            "source": self.airport_3.id,
            "destination": self.airport_1.id,
            "distance": 900.0
        }
        res = self.client.put(detail_url(self.route_2.id), payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        route = Route.objects.get(id=res.data["id"])
        for key in payload:
            if key == "source" or key == "destination":
                self.assertEqual(payload[key], getattr(route, f"{key}_id"))
            else:
                self.assertEqual(payload[key], getattr(route, key))

    def test_delete_route(self):
        res = self.client.delete(detail_url(self.route_2.id))
        self.assertEqual(Route.objects.count(), 1)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

    def test_get_invalid_route(self):
        invalid_id = self.route_2.id + 1
        res = self.client.get(detail_url(invalid_id))
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
