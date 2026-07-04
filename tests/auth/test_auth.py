import pytest

pytestmark = pytest.mark.asyncio


class TestSignup:
    async def test_signup_success(self, client, user_data):
        resp = await client.post("/auth/signup", json=user_data)
        assert resp.status_code == 201
        body = resp.json()
        assert "message" in body

    async def test_signup_duplicate_email(self, client, user_data):
        await client.post("/auth/signup", json=user_data)
        resp = await client.post("/auth/signup", json=user_data)
        assert resp.status_code == 400
        assert "Email already registered" in resp.text

    async def test_signup_duplicate_username(self, client, user_data):
        await client.post("/auth/signup", json=user_data)
        payload = {**user_data, "email": "other@example.com"}
        resp = await client.post("/auth/signup", json=payload)
        assert resp.status_code == 400
        assert "Username already registered" in resp.text


class TestLogin:
    async def test_login_success(self, client, user_data):
        await client.post("/auth/signup", json=user_data)
        resp = await client.post("/auth/login", json=user_data)
        assert resp.status_code == 200
        body = resp.json()
        assert "access_token" in body
        assert "refresh_token" in body
        assert body["token_type"] == "bearer"

    async def test_login_wrong_password(self, client, user_data):
        await client.post("/auth/signup", json=user_data)
        payload = {**user_data, "password": "wrongpass"}
        resp = await client.post("/auth/login", json=payload)
        assert resp.status_code == 401

    async def test_login_not_found(self, client):
        resp = await client.post("/auth/login", json={
            "email": "nobody@example.com",
            "password": "password123",
        })
        assert resp.status_code == 400


class TestRefresh:
    async def test_refresh_success(self, client, user_data, auth_headers):
        refresh_token = auth_headers["refresh_token"]
        client.cookies.set("refresh_token", refresh_token)
        resp = await client.post("/auth/refresh")
        assert resp.status_code == 200
        body = resp.json()
        assert "access_token" in body
        assert "refresh_token" in body

    async def test_refresh_no_cookie(self, client):
        resp = await client.post("/auth/refresh")
        assert resp.status_code == 401

    async def test_refresh_invalid_token(self, client):
        client.cookies.set("refresh_token", "invalidtoken")
        resp = await client.post("/auth/refresh")
        assert resp.status_code == 401


class TestLogout:
    async def test_logout_success(self, client, user_data, auth_headers):
        resp = await client.post(
            "/auth/logout",
            json={"refresh_token": auth_headers["refresh_token"]},
            headers={"Authorization": auth_headers["Authorization"]},
        )
        assert resp.status_code == 200

    async def test_logout_no_token(self, client):
        resp = await client.post("/auth/logout", json={"refresh_token": "xxx"})
        assert resp.status_code == 401


class TestGetMe:
    async def test_get_me_success(self, client, user_data, auth_headers):
        resp = await client.get(
            "/users/me",
            headers={"Authorization": auth_headers["Authorization"]},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["email"] == user_data["email"]
        assert body["username"] == user_data["username"]
        assert "id" in body
        assert "is_active" in body
        assert "is_superuser" in body

    async def test_get_me_unauthorized(self, client):
        resp = await client.get("/users/me")
        assert resp.status_code == 401


class TestPatchMe:
    async def test_patch_username(self, client, user_data, auth_headers):
        resp = await client.patch(
            "/users/me",
            json={"username": "newusername"},
            headers={"Authorization": auth_headers["Authorization"]},
        )
        assert resp.status_code == 200
        assert resp.json()["username"] == "newusername"

    async def test_patch_email(self, client, user_data, auth_headers):
        resp = await client.patch(
            "/users/me",
            json={"email": "newemail@example.com"},
            headers={"Authorization": auth_headers["Authorization"]},
        )
        assert resp.status_code == 200
        assert resp.json()["email"] == "newemail@example.com"

    async def test_patch_password(self, client, user_data, auth_headers):
        resp = await client.patch(
            "/users/me",
            json={"password": "newpassword123", "old_password": "password123"},
            headers={"Authorization": auth_headers["Authorization"]},
        )
        assert resp.status_code == 200

    async def test_patch_duplicate_username(self, client, user_data, auth_headers):
        await client.post("/auth/signup", json={
            "email": "second@example.com",
            "username": "seconduser",
            "handle": "@seconduser",
            "password": "password123",
        })
        resp = await client.patch(
            "/users/me",
            json={"username": "seconduser"},
            headers={"Authorization": auth_headers["Authorization"]},
        )
        assert resp.status_code == 400

    async def test_patch_unauthorized(self, client):
        resp = await client.patch("/users/me", json={"username": "hacker"})
        assert resp.status_code == 401
