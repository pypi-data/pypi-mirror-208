from requests import request, ConnectTimeout, ReadTimeout


def available(url, method="GET"):
    try:
        response = request(
            method,
            url,
            timeout=5,
            verify=False,
            headers={
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,"
                "image/avif,image/webp,image/apng,*/*;q=0.8,"
                "application/signed-exchange;v=b3;q=0.7"
            },
        )
    except (ConnectionError, ConnectTimeout, ReadTimeout):
        return False

    if response.status_code == 400 or response.status_code == 200:
        return True

    return False
