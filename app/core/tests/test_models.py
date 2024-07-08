"""
Test for models
"""

from decimal import Decimal

from django.test import TestCase

from core import models
from core.helper import create_user


class ModelTests(TestCase):
    """
    Test User model starts here
    """

    def test_create_user_with_email_successful(self):
        email = "test@example.com"
        password = "testpass123"
        user = create_user(email=email, password=password)

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        # Test email is normalized for new users
        sample_emails = [
            [
                "test1@EXAMPLE.com",
                "test1@example.com",
            ],
            [
                "Test2@Example.com",
                "Test2@example.com",
            ],
            [
                "TEST3@EXAMPLE.COM",
                "TEST3@example.com",
            ],
            [
                "test4@example.COM",
                "test4@example.com",
            ],
        ]

        for email, expected in sample_emails:
            user = create_user(email=email, password="sample123")
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_error(self):
        # Test that creating a user without an email raises a ValueError
        with self.assertRaises(ValueError):
            create_user(email="", password="test123")

    def test_create_superuser(self):
        # Test creating superuser
        user = create_user(
            email="test@example.com",
            password="test123",
            is_superuser=True,
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    """
        Test Recipe model starts here
    """

    def test_create_recipe(self):
        # Test creating a recipe is successful
        user = create_user(
            email="test@example.com",
            password="testpass123",
        )
        recipe = models.Recipe.objects.create(
            user=user,
            title="Sample recipe name",
            time_minutes=5,
            price=Decimal("5.50"),
            description="Sample recipe description.",
        )

        self.assertEqual(str(recipe), recipe.title)

    """
        Test Tag model starts here
    """

    def test_create_tag(self):
        # Test creating a tag is successful
        user = create_user()
        tag = models.Tag.objects.create(user=user, name="Tag1")

        self.assertEqual(str(tag), tag.name)
