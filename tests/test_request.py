from app import app


def test_request(client: app):
    response = client.get("/")
    assert b"<h1>Hello, WORLD!</h1>" in response.data
