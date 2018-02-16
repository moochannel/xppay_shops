from social_core.backends.oauth import BaseOAuth2
from social_core.storage import UserMixin


class DiscordOAuth2(BaseOAuth2):
    """Discord OAuth authentication backend"""
    name = 'discord'
    AUTHORIZATION_URL = 'https://discordapp.com/api/oauth2/authorize'
    ACCESS_TOKEN_URL = 'https://discordapp.com/api/oauth2/token'
    ACCESS_TOKEN_METHOD = 'POST'
    REDIRECT_STATE = False
    REQUIRES_EMAIL_VALIDATION = True

    def get_user_details(self, response):
        return {
            'username': UserMixin.clean_username(response.get('username')),
            'email': response.get('email'),
            'first_name': '',
            'last_name': '',
            'discord_id': response.get('id'),
            'discord_name': '#'.join([response.get('username'),
                                      response.get('discriminator')]),
            'avatar_hash': response.get('avatar'),
        }

    def user_data(self, access_token, *args, **kwargs):
        headers = {'Authorization': f'Bearer {access_token}'}
        return self.get_json('https://discordapp.com/api/users/@me', headers=headers)
