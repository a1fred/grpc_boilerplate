from typing import Optional
import urllib.parse


class ParsedGrpcConnectionString:
    host: str
    port: int
    api_token: Optional[str] = None

    server_crt: Optional[str] = ""

    def is_secure(self) -> bool:
        return bool(self.server_crt)


# Parse grpc connectionstring `h2c|h2cs://[<token>@]host:port[?ServerCrt=<path to server cert>]`
# Attempt to create generic connectionstring format for grpc connections
def parse_grpc_connectionstring(connection_string: str) -> ParsedGrpcConnectionString:
    result = ParsedGrpcConnectionString()

    parsed = urllib.parse.urlparse(connection_string, allow_fragments=False)
    host: Optional[str] = parsed.hostname
    port: Optional[int] = parsed.port
    result.api_token = parsed.username or None

    if not host:
        raise ValueError("host must be specified")
    result.host = host

    if not port:
        raise ValueError("port must be specified")
    result.port = port

    qs = urllib.parse.parse_qs(parsed.query)
    server_crt_values = qs.get('ServerCrt', [])
    if len(server_crt_values) == 0:
        server_crt = None
    elif len(server_crt_values) == 1:
        server_crt = server_crt_values[0]
    else:
        raise ValueError("Multiple ServerCrt is not allowed")

    if parsed.scheme == 'h2c':
        if server_crt:
            raise ValueError("Insecure connection must not contain ServerCrt")
        result.server_crt = None
    elif parsed.scheme == 'h2cs':
        if not server_crt:
            raise ValueError("Secure connection must contain ServerCrt")
        result.server_crt = server_crt
    else:
        raise ValueError(f"Unknown scheme: '{parsed.scheme}' for '{connection_string}'")

    return result
