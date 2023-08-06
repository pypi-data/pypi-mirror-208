import json
import requests


class HttpClient:
    API_VERSION = "2.17"

    def __init__(
        self, host: any, port: int, user: str, password: any, token: any, verify: bool
    ):
        """
        HttpClient handles the REST requests.

        :param host: IP address/FQDN of the Pure Storage Array.
        :param port: Port the Pure Storage is listening on.
        :param user: User account to login with.
        :param password: Password.
        :param verify: Boolean indicating whether certificate verification
                       should be turned on or not.
        """
        self.base_url = f"https://{host}:{port}/api/{self.API_VERSION}/"
        self.request = requests
        self.header = {}
        self.header["Content-Type"] = "application/json; charset=utf-8"
        self.header["Authorization"] = f"Bearer {token}"
        self.header["User-agent"] = "Jakarta Commons-HttpClient/3.1"
        self.header["Accept"] = "application/json"
        self.verify = verify
        if not verify:
            requests.packages.urllib3.disable_warnings()

    def _format_url(self, url):
        """Formats the REST URL to use for API calls."""
        return "%s%s" % (self.base_url, url if url[0] != "/" else url[1:])

    def get(self, url):
        """Perform a REST GET request."""
        return self.request.get(
            self._format_url(url), headers=self.header, verify=self.verify
        )

    def post(self, url, payload):
        """Perform a REST POST request."""
        return self.request.post(
            self._format_url(url),
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers=self.header,
            verify=self.verify,
        )

    def put(self, url, payload):
        """Perform a REST PUT request."""
        return self.request.put(
            self._format_url(url),
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers=self.header,
            verify=self.verify,
        )

    def patch(self, url, payload):
        """Perform a REST PATCH request."""
        return self.request.patch(
            self._format_url(url),
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers=self.header,
            verify=self.verify,
        )

    def delete(self, url, payload=None):
        """Perform a REST DELETE request."""
        return self.request.delete(
            self._format_url(url),
            params=payload,
            headers=self.header,
            verify=self.verify,
        )
