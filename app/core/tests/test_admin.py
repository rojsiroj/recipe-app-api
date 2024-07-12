"""
Test for the Django admin modifications
"""

from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from django.test import Client

from core.helper import create_user
from core.models import Recipe, Tag, Ingredient


class AdminSiteTests(TestCase):
    # Tests for django admin

    def setUp(self):
        # Create user and client
        self.client = Client()
        self.admin_user = create_user(
            email="admin@example.com",
            password="testpass1234",
            is_superuser=True,
        )
        self.client.force_login(self.admin_user)

        self.user = create_user(
            email="user@example.com",
            password="testpass1234",
            name="Test User",
        )

        self.recipe = Recipe.objects.create(
            user=self.user,
            title="Sample recipe name",
            time_minutes=5,
            price=Decimal("5.50"),
            description="Sample recipe description.",
        )

        self.tag = Tag.objects.create(user=self.user, name="Test Tag")
        self.ingredient = Ingredient.objects.create(
            user=self.user,
            name="Test Ingredient",
        )

    """
    Test User admin starts here
    """

    def test_users_list(self):
        # Test that users are listed on page
        url = reverse("admin:core_user_changelist")
        res = self.client.get(url)

        self.assertContains(res, self.user.name)
        self.assertContains(res, self.user.email)

    def test_edit_user_page(self):
        # Test edit user page works
        url = reverse("admin:core_user_change", args=[self.user.id])
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)

    def test_create_user_page(self):
        # Test the create user page works
        url = reverse("admin:core_user_add")
        res = self.client.get(url)

        self.assertEqual(res.status_code, 200)

    """
        Test Recipe model starts here
    """

    def test_recipes_list(self):
        # Test that recipes are listed on page
        url = reverse("admin:core_recipe_changelist")
        res = self.client.get(url)

        self.assertContains(res, self.recipe.title)

    """
        Test Tag admin starts here
    """

    def test_tags_list(self):
        # Test that tags are listed on page
        url = reverse("admin:core_tag_changelist")
        res = self.client.get(url)

        self.assertContains(res, self.tag.name)

    """
        Test Ingredient admin starts here
    """

    def test_ingredients_list(self):
        # Test that ingredients are listed on page
        url = reverse("admin:core_ingredient_changelist")
        res = self.client.get(url)

        self.assertContains(res, self.ingredient.name)
