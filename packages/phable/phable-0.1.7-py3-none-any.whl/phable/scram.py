import hashlib
import hmac
import logging
import re
from base64 import urlsafe_b64decode, urlsafe_b64encode
from binascii import hexlify, unhexlify
from dataclasses import dataclass
from hashlib import pbkdf2_hmac
from random import getrandbits
from time import time_ns
from typing import Optional

from phable.http import request

from .http import Response

logger = logging.getLogger(__name__)


# TODO: Check the validity of the server final message


class ScramException(Exception):
    def __init__(self, message: str, server_error: Optional[str] = None):
        super().__init__(message)
        self.server_error = server_error

    def __str__(self):
        s_str = "" if self.server_error is None else f": {self.server_error}"
        return super().__str__() + s_str


@dataclass
class NotFoundError(Exception):
    help_msg: str


class ScramClient:
    def __init__(
        self, host_url: str, username: str, password: str, hash: str = "sha256"
    ):
        if hash not in ["sha256"]:
            raise ScramException(
                "The 'hash' parameter must be a str equal to 'sha256'."
            )

        self.host_url = host_url
        self._username = username
        self._password = password
        self.auth_token = self._get_auth_token()
        self._hash = hash

    def _get_auth_token(self):
        host_url = self.host_url

        # send hello msg & set the response
        hello_resp = request(host_url, headers=self._get_hello_req())
        self._set_hello_resp(hello_resp)

        # send first msg & set the response
        first_resp = request(host_url, headers=self._get_first_req())
        self._set_first_resp(first_resp)

        # send last msg & receive the response
        last_resp = request(host_url, headers=self._get_last_req())

        # parse the auth token from the last response
        auth_token = _parse_auth_token(last_resp.headers.as_string())

        return auth_token

    def _get_hello_req(self) -> dict[str, str]:
        """
        Return the HTTP headers required for the client's hello message.

        Note:  There is no data required for the client's hello message.
        """
        username = _to_base64(self._username)
        headers = {"Authorization": f"HELLO username={username}"}
        return headers

    def _set_hello_resp(self, resp: Response) -> None:
        """
        Save server's response data as class attributes to be able to get other
        request messages.
        """
        auth_header = resp.headers["WWW-Authenticate"]
        self.handshake_token = _parse_handshake_token(auth_header)
        self._hash = _parse_hash_func(auth_header)

    def _get_first_req(self) -> dict[str, str]:
        gs2_header = "n,,"

        self._c_nonce: str = _gen_nonce()
        self._c1_bare: str = f"n={self._username},r={self._c_nonce}"

        headers = {
            "Authorization": f"scram handshakeToken={self.handshake_token}, "
            f"hash={self._hash}, data={_to_base64(gs2_header+self._c1_bare)}"
        }
        return headers

    def _set_first_resp(self, resp: Response) -> None:
        auth_header = resp.headers["WWW-Authenticate"]
        r, s, i = _parse_scram_data(auth_header)
        self._s_nonce: str = r
        self._salt: str = s
        self._iter_count: int = i

    def _get_last_req(self):
        # define the client final no proof
        client_final_no_proof = f"c={_to_base64('n,,')},r={self._s_nonce}"

        # define the auth msg
        auth_msg = (
            f"{self._c1_bare},r={self._s_nonce},s={self._salt},"
            + f"i={self._iter_count},{client_final_no_proof}"
        )

        # define the client key
        client_key = hmac.new(
            unhexlify(
                _salted_password(
                    self._salt,
                    self._iter_count,
                    self._hash,
                    self._password,
                )
            ),
            "Client Key".encode("UTF-8"),
            self._hash,
        ).hexdigest()

        # find the stored key
        hashFunc = hashlib.new(self._hash)
        hashFunc.update(unhexlify(client_key))
        stored_key = hashFunc.hexdigest()

        # find the client signature
        client_signature = hmac.new(
            unhexlify(stored_key), auth_msg.encode("utf-8"), self._hash
        ).hexdigest()

        # find the client proof
        client_proof = hex(int(client_key, 16) ^ int(client_signature, 16))[2:]

        # may need to do some padding before converting the hex to its
        # binary representation
        while len(client_proof) < 64:
            client_proof = "0" + client_proof

        client_proof_encode = _to_base64(unhexlify(client_proof))

        client_final = client_final_no_proof + ",p=" + client_proof_encode
        client_final_base64 = _to_base64(client_final)

        final_msg = (
            f"scram handshaketoken={self.handshake_token},data={client_final_base64}"
        )

        headers = {"Authorization": final_msg}
        return headers


def _parse_scram_data(auth_header: str) -> tuple[str, str, int]:
    """Parses and decodes scram data from the contents of a 'WWW-Authenticate' header.

    Args:
        auth_header (str): Contents of the 'WWW-Authenticate' header in the HTTP
        response received from the server.  Search 'WWW-Authenticate' in the Project
        Haystack docs for more details.

    Raises:
        NotFoundError: When the parameter, auth_header, or its decoded variant does not
        contain one or more expected substrings.

    Returns:
        tuple[str, str, int]: Index 0 is the server nonce, Index 1 is the salt, and
        Index 2 is the iteration count which are used by the client for SCRAM
        authentication.

    Examples:
        A valid input
        >>> parse_scram_data("scram data=cj0xODI2YzEwY2VlZDMxYWNjOWYyYmFiY2IxMDAzZjdiNT\
UyNjhhOWFkYTk2NGRhNzhlYmNmYzAxOWIyY2ViNTVkLHM9d1luT3FYc1VTMUZKRHpwTmN3K09FQk9OV3lSTWJMY\
UFrWkpCVUtnZ3RIMD0saT0xMDAwMA, handshakeToken=c3U, hash=SHA-256") #doctest: \
+NORMALIZE_WHITESPACE
        ('1826c10ceed31acc9f2babcb1003f7b55268a9ada964da78ebcfc019b2ceb55d',
        'wYnOqXsUS1FJDzpNcw+OEBONWyRMbLaAkZJBUKggtH0=',
        10000)

        An invalid input
        >>> parse_scram_data("This is an invalid input!")
        Traceback (most recent call last):
        ...
        phable.scram.NotFoundError: Scram data not found in the 'WWW-Authenticate' \
header:
        This is an invalid input!
    """

    exclude_msg = "scram data="
    scram_data = re.search(f"({exclude_msg})[a-zA-Z0-9]+", auth_header)

    if scram_data is None:
        raise NotFoundError(
            f"Scram data not found in the 'WWW-Authenticate' header:\n{auth_header}"
        )

    decoded_scram_data = _from_base64(scram_data.group(0)[len(exclude_msg) :])
    s_nonce, salt, iteration_count = decoded_scram_data.replace(" ", "").split(",")

    if "r=" not in s_nonce:
        raise NotFoundError(
            f"Server nonce not found in the 'WWW-Authenticate' header:\n{auth_header}"
        )
    elif "s=" not in salt:
        raise NotFoundError(
            f"Salt not found in the 'WWW-Authenticate' header:\n{auth_header}"
        )
    elif "i=" not in iteration_count:
        raise NotFoundError(
            (
                "Iteration count not found in the 'WWW-Authenticate' header:"
                f"\n{auth_header}"
            )
        )

    return (
        s_nonce.replace("r=", ""),
        salt.replace("s=", ""),
        int(iteration_count.replace("i=", "")),
    )


def _parse_handshake_token(auth_header: str) -> str:
    """Parses the handshake token from the contents of a 'WWW-Authenticate' header.

    Args:
        auth_header (str): Contents of the 'WWW-Authenticate' header in the HTTP
        response received from the server.  Search 'WWW-Authenticate' in the Project
        Haystack docs for more details.

    Raises:
        NotFoundError: When the parameter, auth_header, does not contain the expected
        substring.

    Returns:
        str: Handshake token defined by the server which the client is required to use
        for SCRAM authentication.

    Examples:
        A valid input
        >>> parse_handshake_token("scram data=cj0xODI2YzEwY2VlZDMxYWNjOWYyYmFiY2IxMDAzZ\
jdiNTUyNjhhOWFkYTk2NGRhNzhlYmNmYzAxOWIyY2ViNTVkLHM9d1luT3FYc1VTMUZKRHpwTmN3K09FQk9OV3lS\
TWJMYUFrWkpCVUtnZ3RIMD0saT0xMDAwMA, handshakeToken=c3U, hash=SHA-256")
        'c3U'

        An invalid input
        >>> parse_handshake_token("This is an invalid input!")
        Traceback (most recent call last):
        ...
        phable.scram.NotFoundError: Handshake token not found in the 'WWW-Authenticate'\
 header:
        This is an invalid input!
    """

    exclude_msg = "handshakeToken="
    s = re.search(f"({exclude_msg})[a-zA-Z0-9]+", auth_header)

    if s is None:
        raise NotFoundError(
            (
                "Handshake token not found in the 'WWW-Authenticate' header:"
                + f"\n{auth_header}"
            )
        )

    return s.group(0)[len(exclude_msg) :]


def _parse_hash_func(auth_header: str) -> str:
    """Parses the hash function from the contents of a 'WWW-Authenticate' header.

    Args:
        auth_header (str): Contents of the 'WWW-Authenticate' header in the HTTP
        response received from the server.  Search 'WWW-Authenticate' in the Project
        Haystack docs for more details.

    Raises:
        NotFoundError: When the parameter, auth_header, does not contain the expected
        substring.

    Returns:
        str: Cryptographic hash function defined by the server which the client is
        required to use for SCRAM authentication.

    Examples:
        A valid input
        >>> parse_hash_func("authToken=web-syPGBhoPY0XhKi6EXUG62BMACc0Ot7xuq4PShtj\
I47c-38,data=dj1ENDJEbS9kckRiSUN1NXpvTHd2OWloSlJiWkxzMFBRNllibm5EY2NNU1M4PQ,\
hash=SHA-256")
        'sha256'

        An invalid input
        >>> parse_hash_func("This is an invalid input!")
        Traceback (most recent call last):
        ...
        phable.scram.NotFoundError: Hash method not found in the 'WWW-Authenticate' \
header:
        This is an invalid input!
    """

    exclude_msg = "hash="
    s = re.search(f"({exclude_msg})(SHA-256)", auth_header)

    if s is None:
        raise NotFoundError(
            f"Hash method not found in the 'WWW-Authenticate' header:\n{auth_header}"
        )

    s_new = s.group(0)[len(exclude_msg) :]

    if s_new == "SHA-256":
        s_new = "sha256"

    return s_new


def _parse_auth_token(auth_header: str) -> str:
    """Parses the auth token from the contents of a 'WWW-Authenticate' header.

    Args:
        auth_header (str): Contents of the 'WWW-Authenticate' header in the HTTP
        response received from the server.  Search 'WWW-Authenticate' in the Project
        Haystack docs for more details.

    Raises:
        NotFoundError: When the parameter, auth_header, does not contain the expected
        substring.

    Returns:
        str: Auth token generated by the server.

    Examples:
        A valid input
        >>> parse_auth_token("authToken=web-syPGBhoPY0XhKi6EXUG62BMACc0Ot7xuq4PShtjI47c\
-38,data=dj1ENDJEbS9kckRiSUN1NXpvTHd2OWloSlJiWkxzMFBRNllibm5EY2NNU1M4PQ,hash=SHA-256")
        'web-syPGBhoPY0XhKi6EXUG62BMACc0Ot7xuq4PShtjI47c-38'

        An invalid input
        >>> parse_auth_token("This is an invalid input!")
        Traceback (most recent call last):
        ...
        phable.scram.NotFoundError: Auth token not found in the 'WWW-Authenticate' \
header:
        This is an invalid input!
    """

    exclude_msg = "authToken="
    s = re.search(f"({exclude_msg})[^,]+", auth_header)

    if s is None:
        raise NotFoundError(
            f"Auth token not found in the 'WWW-Authenticate' header:\n{auth_header}"
        )

    return s.group(0)[len(exclude_msg) :]


def _to_custom_hex(x: int, length: int) -> str:
    """
    Convert an integer x to hexadecimal string representation without a
    prepended '0x' str.  Prepend leading zeros as needed to ensure the
    specified number of nibble characters.
    """

    # Convert x to a hexadecimal number
    x_hex = hex(x)

    # Remove prepended 0x used to describe hex numbers
    x_hex = x_hex.replace("0x", "")

    # Prepend 0s as needed
    if len(x_hex) < length:
        x_hex = "0" * (length - len(x_hex)) + x_hex

    return x_hex


def _gen_nonce() -> str:
    """Generate a nonce."""
    # Notes:
    #   getrandbits() defines a random 64 bit integer
    #   time_ns() defines ticks since the Unix epoch (1 January 1970)

    # Define nonce random mask for this VM
    nonce_mask: int = getrandbits(64)

    rand = getrandbits(64)
    ticks = time_ns() ^ nonce_mask ^ rand
    return _to_custom_hex(rand, 16) + _to_custom_hex(ticks, 16)


def _salted_password(
    salt: str, iterations: int, hash_func: str, password: str
) -> bytes:
    # Need hash_func to be a str here
    dk = pbkdf2_hmac(hash_func, password.encode(), urlsafe_b64decode(salt), iterations)
    encrypt_password = hexlify(dk)
    return encrypt_password


def _to_base64(msg: str | bytes) -> str:
    """Perform base64uri encoding of a message as defined by RFC 4648.

    Args:
        msg (str | bytes): A message to be encoded.

    Returns:
        str: A base64uri encoded message

    Examples:
        >>> _to_base64("example")
        'ZXhhbXBsZQ'
        >>> _to_base64(bytes("example", "utf-8"))
        'ZXhhbXBsZQ'
    """

    # Convert str inputs to bytes
    if isinstance(msg, str):
        msg = msg.encode("utf-8")

    # Encode using URL and filesystem-safe alphabet.
    # This means + is encoded as -, and / is encoded as _.
    output = urlsafe_b64encode(msg)

    # Decode the output as a str
    output = output.decode("utf-8")

    # Remove padding
    output = output.replace("=", "")

    return output


def _from_base64(msg: str) -> str:
    """Decode a base64uri encoded message defined by RFC 4648 into
    its binary contents. Decode a URI-safe RFC 4648 encoding.

    Args:
        msg (str): A base64uri message to be decoded.

    Returns:
        str: A decoded message

    Example:
        >>> _from_base64("ZXhhbXBsZQ")
        'example'
    """

    # Decode base64uri
    decoded_msg = urlsafe_b64decode(_to_bytes(msg))

    # Decode bytes obj as a str
    return decoded_msg.decode("utf-8")


def _to_bytes(s: str) -> bytes:
    """Convert a string to a bytes object.

    Prior to conversion to bytes the string object must have a length that is a
    multiple of 4.  If applicable, padding will be applied to extend the length
    of the string input.

    Args:
        s (str): A string object.

    Returns:
        bytes: A bytes object.

    Examples:
        >>> _to_bytes("abcd")
        b'abcd'
        >>> _to_bytes("abcde")
        b'abcde==='
        >>> _to_bytes("abcdef")
        b'abcdef=='
        >>> _to_bytes("abcdefg")
        b'abcdefg='
    """

    r = len(s) % 4
    if r != 0:
        s += "=" * (4 - r)

    return s.encode("utf-8")
