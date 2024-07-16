"""
Test for ingredient APIs
"""

from decimal import Decimal

from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient, Recipe
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

    def test_delete_ingredient(self):
        # Test deleting an ingredient
        ingredient = Ingredient.objects.create(user=self.user, name="Salt")
        url = detail_url(ingredient.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

        ingredients = Ingredient.objects.filter(user=self.user)
        self.assertFalse(ingredients.exists())

    def test_filter_ingredients_assigned_to_recipes(self):
        # Test listing ingredients by those assigned to recipes
        ingredient1 = Ingredient.objects.create(
            user=self.user,
            name="Apples",
        )
        ingredient2 = Ingredient.objects.create(
            user=self.user,
            name="Turkey",
        )
        recipe = Recipe.objects.create(
            title="Apple Crumble",
            time_minutes=5,
            price=Decimal("4.50"),
            user=self.user,
        )
        recipe.ingredients.add(ingredient1)

        res = self.client.get(INGREDIENTS_URL, {"assigned_only": 1})
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        serializer1 = IngredientSerializer(ingredient1)
        serializer2 = IngredientSerializer(ingredient2)
        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_filtered_ingredients_unique(self):
        # Test filtered ingredients return a unique list
        ingredient = Ingredient.objects.create(user=self.user, name="Salt")
        Ingredient.objects.create(user=self.user, name="Pepper")
        recipe1 = Recipe.objects.create(
            title="Salted Caramel",
            time_minutes=5,
            price=Decimal("4.50"),
            user=self.user,
        )
        recipe2 = Recipe.objects.create(
            title="Herb Eggs",
            time_minutes=20,
            price=Decimal("4.00"),
            user=self.user,
        )
        recipe1.ingredients.add(ingredient)
        recipe2.ingredients.add(ingredient)

        res = self.client.get(INGREDIENTS_URL, {"assigned_only": 1})
        self.assertEqual(len(res.data), 1)
