import base64
import os
import uuid

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from rest_framework.response import Response


class PFunctions:
    __fernet = None

    def __init__(self, encryptionKey=None) -> None:
        if encryptionKey is not None:
            self.__encryptionKey = encryptionKey.encode()
            self.__fernet = Fernet(self.__encryptionKey)

    @staticmethod
    def getClientIP(request):
        """
        This function retrieves the IP address of the client making a request to a web server.
        It first checks if the request object contains the `HTTP_X_FORWARDED_FOR` header,
        which is used by some proxy servers to forward the client's IP address.
        If this header is present, the IP address is extracted from the header and returned as a string.
        If the `HTTP_X_FORWARDED_FOR` header is not present, the function checks the `REMOTE_ADDR`
        attribute of the request object, which contains the IP address of the client as
        reported by the web server.

        Parameters:
            request (HttpRequest): The HttpRequest object representing the incoming request.

        Returns:
            str: The IP address of the client as a string.

        Example:
            If the client's IP address is 123.45.67.89, and the request object is `request`,
            you can retrieve the client's IP address by calling `getClientIP(request)`, which will return `'123.45.67.89'`.

        Note:
            If the `HTTP_X_FORWARDED_FOR` header contains multiple IP addresses,
            this function will return only the first one. If the `REMOTE_ADDR` attribute is not present in the request object,
            this function will raise a `TypeError`.
        """

        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    @staticmethod
    def getClientHost(request):
        """
        The getClientHost() function retrieves the hostname of the client that sent the current request to the server.

        This function first checks if the HTTP_X_FORWARDED_HOST header is set, which contains the original host requested
        by the client in the case of proxy requests. If this header is set, the function returns the first hostname in the comma-separated list of values.

        If the HTTP_X_FORWARDED_HOST header is not set, the function checks if the REMOTE_ADDR header is set,
        which contains the IP address of the client. The IP address is then used to perform a reverse DNS lookup to retrieve the hostname of the client.

        If both headers are not set or if a reverse DNS lookup fails, the function returns the value of the REMOTE_ADDR header.

        Returns:
        The hostname of the client that sent the current request to the server.
        """
        hostname = request.META.get('SERVER_NAME')
        if hostname == "":
            hostname = None
        return hostname

    @staticmethod
    def getClientBrowser(request):
        """
        Return the client browser from the request
        """
        browser = request.META.get('HTTP_USER_AGENT')
        if browser == "":
            browser = None
        return browser

    @staticmethod
    def generateKey():
        # generate a key for encryption and decryption
        # You can use fernet to generate
        # the key or use random key generator
        # here I'm using fernet to generate key
        password = str(uuid.uuid4()).encode()
        salt = os.urandom(16)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=480000,
        )
        return base64.urlsafe_b64encode(kdf.derive(password))

    def encryptMsg(self, message):
        # then use the Fernet class instance
        # to encrypt the string must
        # be encoded to byte string before encryption
        __encMessage = self.__fernet.encrypt(message.encode())
        return __encMessage.decode('utf-8')

    def decryptMsg(self, message):
        # decrypt the encrypted string with the
        # Fernet instance of the key,
        # that was used for encrypting the string
        # encoded byte string is returned by decrypt method,
        # so decode it to string with decode methods
        __encMessage = str(message).encode()
        return self.__fernet.decrypt(__encMessage).decode()

        # request.session[SystemParams.app_name.value] = getattr(settings, "CPS_CORE_APP_NAME", "")
        # request.session[SystemParams.brand_name.value] = getattr(settings, "CPS_CORE_BRAND_NAME", "")

    @staticmethod
    def response_to_success(data=None, message="Success", ):
        return Response({
            "message": message,
            "data": [] if data is None else data,
            'errors': None
        })

    @staticmethod
    def response_to_error(error=None, message="Failed"):
        if error is None:
            error = []
        return Response({
            "message": message,
            "data": None,
            'errors': [] if error is None else error
        })
