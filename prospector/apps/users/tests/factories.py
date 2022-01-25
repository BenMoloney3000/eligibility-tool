from typing import Any
from typing import Sequence

from factory import Faker
from factory import post_generation
from factory.django import DjangoModelFactory

from prospector.apps.user.models import User


class UserFactory(DjangoModelFactory):
    username = Faker("user_name")
    email = Faker("email")

    @post_generation
    def password(self, create: bool, extracted: Sequence[Any], **kwargs):
        password = (
            extracted
            if extracted
            else Faker(
                "password",
                length=42,
                special_chars=True,
                digits=True,
                upper_case=True,
                lower_case=True,
            ).evaluate(None, None, extra={"locale": None})
        )
        self.set_password(password)

    class Meta:
        model = User
        django_get_or_create = ["username"]
