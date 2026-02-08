import json
import urllib.error
import urllib.request

BASE_URL = "http://127.0.0.1:8000"


def req(method, url, data=None, token=None):
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    payload = None
    if data is not None:
        payload = json.dumps(data).encode("utf-8")
    req_obj = urllib.request.Request(url, data=payload, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req_obj, timeout=8) as resp:
            return resp.status, resp.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read().decode("utf-8")
    except Exception as exc:
        return None, str(exc)


def extract_exception(html):
    marker = '<pre class="exception_value">'
    start = html.find(marker)
    if start == -1:
        return "<no exception_value found>"
    start += len(marker)
    end = html.find("</pre>", start)
    if end == -1:
        return html[start:].strip()
    return html[start:end].strip()


def main():
    status, body = req(
        "POST",
        f"{BASE_URL}/api/v1/auth/login/",
        {"username": "admin@itsm.local", "password": "admin123456"},
    )
    token = json.loads(body).get("access") if status == 200 else None

    for name, path in [
        ("cmdb-config-items", "/api/v1/cmdb/config-items/"),
        ("cmdb-ci-relationships", "/api/v1/cmdb/ci-relationships/"),
    ]:
        status, body = req("GET", f"{BASE_URL}{path}", token=token)
        print(f"{name} {status}")
        print(extract_exception(body))
        print("-")


if __name__ == "__main__":
    main()
