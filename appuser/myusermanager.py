from django.contrib.auth.base_user import BaseUserManager


class AdminUserManager(BaseUserManager):

    def _create_user(
            self,
            username,
            password,
            is_superuser=False,
            is_active=False,
            **extra_fields
    ):
        if not username:
            raise ValueError("Username is Required.")

        user = self.model(
            username=username,
            password=password,
            is_active=is_active,
            is_superuser=is_superuser,
            **extra_fields
        )
        user.set_password(password)
        user.save()
        return user

    def create_user(self, username, email, password=None):
        if not email:
            raise ValueError('Users must have an email address')
        if not username:
            raise ValueError('Users must have a username')

        user = self.model(
            email=self.normalize_email(email),
            username=username,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None):
        user = self.create_user(
            username=username,
            email=email,
            password=password,
        )
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user
