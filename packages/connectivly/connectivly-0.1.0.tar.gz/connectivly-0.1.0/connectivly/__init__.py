import requests
import jwt
import json


class Connectivly(object):

    def __init__(self, api_key, base_url):
        self.api_key = api_key
        self.jwks = None
        self.base_url = base_url

    def _jwks(self):
        if self.jwks is None:
            rc = requests.get(self.base_url + '/auth/jwks.json')
            if rc.status_code == 200:
                self.jwks = rc.json()

        return self.jwks

    def get_login_session(self, session_id):
        session = requests.get(
            self.base_url + "/api/auth_session/" + session_id,
            headers={'X-API-KEY': self.api_key}
        )

        return session.json()

    def approve_login_session(self, session_id, user_info):
        approval = requests.post(
            self.base_url + "/api/auth_session/" + session_id + "/approve",
            json=user_info,
            headers={'X-API-KEY': self.api_key}
        ).json()

        return approval

    def validate_token(self, token, remote=False):
        # Get JWKS data
        jwks = self._jwks()

        decoded = None

        # Try decoding the key against each public key
        for public_key in jwks['keys']:
            try:
                key = jwt.algorithms.RSAAlgorithm.from_jwk(public_key)
                decoded = jwt.decode(token, key=key, algorithms=['RS256'])
            except:
                continue

        # If we have a valid JWT and want to verify it against Connectivly
        if decoded is not None and remote:

            # Validate the JWT against the server
            rc = requests.post(self.base_url + "/api/introspect", data={"token": token})
            if rc.status_code != 200:
                decoded = None
            else:
                if rc.json()['active'] != True:
                    decoded = None

        # JWT contains the application, user id, and scopes
        return decoded