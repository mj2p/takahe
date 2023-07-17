import urlman
from django.db import models
from pydantic import BaseModel


class PushSubscriptionSchema(BaseModel):
    """
    Basic validating schema for push data
    """

    class Keys(BaseModel):
        p256dh: str
        auth: str

    endpoint: str
    keys: Keys
    alerts: dict[str, bool]
    policy: str


class Token(models.Model):
    """
    An (access) token to call the API with.

    Can be either tied to a user, or app-level only.
    """

    application = models.ForeignKey(
        "api.Application",
        on_delete=models.CASCADE,
        related_name="tokens",
    )

    user = models.ForeignKey(
        "users.User",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name="tokens",
    )

    identity = models.ForeignKey(
        "users.Identity",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name="tokens",
    )

    token = models.CharField(max_length=500, unique=True)
    scopes = models.JSONField()

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    revoked = models.DateTimeField(blank=True, null=True)

    push_subscription = models.JSONField(blank=True, null=True)

    class urls(urlman.Urls):
        edit = "/@{self.identity.handle}/settings/tokens/{self.id}/"

    def has_scope(self, scope: str):
        """
        Returns if this token has the given scope.
        It's a function so we can do mapping/reduction if needed
        """
        # TODO: Support granular scopes the other way?
        scope_prefix = scope.split(":")[0]
        return (scope in self.scopes) or (scope_prefix in self.scopes)

    def set_push_subscription(self, data: dict):
        # Validate schema and assign
        self.push_subscription = PushSubscriptionSchema(**data).dict()
        self.save()
