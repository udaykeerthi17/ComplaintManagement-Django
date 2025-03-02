from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_text  # use force_text instead of six

class AccountActivationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            str(user.pk) + str(timestamp) +
            str(user.profile.email_confirmed)  # Convert boolean to string if necessary
        )

account_activation_token = AccountActivationTokenGenerator()
