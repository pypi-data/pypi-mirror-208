from urllib.parse import parse_qs, urlencode, urlparse, urlunparse


def add_query_parameters(url: str, new_params: dict):
    parsed_url = urlparse(url)

    # Parse the existing query parameters
    query_params = parse_qs(parsed_url.query)

    # Add the new query parameter
    for key, value in new_params.items():
        query_params[key] = value

    # Reconstruct the query string
    new_query = urlencode(query_params, doseq=True)

    # Reconstruct the full URL with the new query string
    new_url = urlunparse(parsed_url._replace(query=new_query))

    return new_url
