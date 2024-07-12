"""
Test for ingredient APIs
"""

from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient
from core.helper import create_user

from recipe.serializers import IngredientSerializer

INGREDIENTS_URL = reverse("recipe:ingredient-list")


def detail_url(ingredient_id):
    # Return ingredient detail URL
    return reverse("recipe:ingredient-detail", args=[ingredient_id])


class PublicIngredientsAPITests(TestCase):
    # Test unauthenticated ingredient API requests

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        # Test auth is required to call API
        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsAPITests(TestCase):
    # Test authenticated ingredient API requests
    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredients(self):
        # Test retrieving a list of ingredients
        Ingredient.objects.create(user=self.user, name="Salt")
        Ingredient.objects.create(user=self.user, name="Pepper")

        res = self.client.get(INGREDIENTS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        ingredients = Ingredient.objects.all().order_by("-name")
        serializer = IngredientSerializer(ingredients, many=True)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        # Test list of ingredients is limited to auntheticated user
        other_user = create_user(email="user2@example.com")
        Ingredient.objects.create(user=other_user, name="Vinegar")
        ingredient = Ingredient.objects.create(user=self.user, name="Chili")

        res = self.client.get(INGREDIENTS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["name"], ingredient.name)
        self.assertEqual(res.data[0]["id"], ingredient.id)

    def test_update_ingredient(self):
        # Test updating an ingredient
        ingredient = Ingredient.objects.create(user=self.user, name="Salt")
        payload = {"name": "Sugar"}
        url = detail_url(ingredient.id)
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        ingredient.refresh_from_db()
        self.assertEqual(ingredient.name, payload["name"])
