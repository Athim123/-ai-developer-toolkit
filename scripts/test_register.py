import httpx

resp = httpx.post(
    'http://127.0.0.1:8000/v1/auth/register',
    json={"email":"athim123@example.com","name":"Athim","password":"Password123"},
    timeout=10,
)
print(resp.status_code)
print(resp.text)
