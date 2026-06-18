import pytest
import pytest_asyncio

pytestmark = pytest.mark.asyncio


@pytest.fixture
def project_data():
    return {"name": "Test Project", "description": "A test project"}


@pytest.fixture
def second_user_data():
    return {
        "email": "second@example.com",
        "username": "seconduser",
        "password": "password123",
    }


@pytest_asyncio.fixture
async def second_auth_headers(client, second_user_data):
    await client.post("/auth/signup", json=second_user_data)
    resp = await client.post("/auth/login", json=second_user_data)
    tokens = resp.json()
    return {"Authorization": f"Bearer {tokens['access_token']}"}


@pytest_asyncio.fixture
async def created_project(client, auth_headers, project_data):
    resp = await client.post("/projects", json=project_data, headers=auth_headers)
    return resp.json()


@pytest.fixture
def project_with_secret_data():
    return {"name": "Secret Project", "description": "With invite", "secret_key": "mysecret123"}


@pytest_asyncio.fixture
async def created_project_with_secret(client, auth_headers, project_with_secret_data):
    resp = await client.post("/projects", json=project_with_secret_data, headers=auth_headers)
    return resp.json()


class TestCreateProject:
    async def test_create_success(self, client, auth_headers, project_data):
        resp = await client.post("/projects", json=project_data, headers=auth_headers)
        assert resp.status_code == 201
        body = resp.json()
        assert body["name"] == project_data["name"]
        assert body["description"] == project_data["description"]
        assert "id" in body

    async def test_create_unauthorized(self, client, project_data):
        resp = await client.post("/projects", json=project_data)
        assert resp.status_code == 401

    async def test_create_empty_name(self, client, auth_headers):
        resp = await client.post("/projects", json={"name": ""}, headers=auth_headers)
        assert resp.status_code == 422


class TestGetProjects:
    async def test_get_projects_success(self, client, auth_headers, created_project):
        resp = await client.get("/projects", headers=auth_headers)
        assert resp.status_code == 200
        body = resp.json()
        assert len(body) >= 1
        assert body[0]["name"] == created_project["name"]

    async def test_get_projects_unauthorized(self, client):
        resp = await client.get("/projects")
        assert resp.status_code == 401

    async def test_get_projects_empty(self, client, auth_headers):
        resp = await client.get("/projects", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json() == []


class TestGetProject:
    async def test_get_project_success(self, client, auth_headers, created_project):
        resp = await client.get(f"/projects/{created_project['id']}", headers=auth_headers)
        assert resp.status_code == 200
        body = resp.json()
        assert body["project"]["id"] == created_project["id"]
        assert "members" in body
        assert len(body["members"]) == 1
        assert body["members"][0]["role"] == "admin"

    async def test_get_project_not_found(self, client, auth_headers):
        resp = await client.get("/projects/nonexistent-uuid", headers=auth_headers)
        assert resp.status_code == 404

    async def test_get_project_unauthorized(self, client):
        resp = await client.get("/projects/some-project-id")
        assert resp.status_code == 401

    async def test_get_project_not_member(self, client, second_auth_headers, created_project):
        resp = await client.get(f"/projects/{created_project['id']}", headers=second_auth_headers)
        assert resp.status_code == 403


class TestAddMember:
    async def test_add_member_success(self, client, auth_headers, second_auth_headers, created_project):
        resp = await client.get("/users/me", headers=second_auth_headers)
        second_user = resp.json()

        resp = await client.post(
            f"/projects/{created_project['id']}/members",
            json={"user_id": second_user["id"], "role": "member"},
            headers=auth_headers,
        )
        assert resp.status_code == 201
        assert resp.json()["role"] == "member"

    async def test_add_member_not_admin(self, client, second_auth_headers, created_project):
        resp = await client.get("/users/me", headers=second_auth_headers)
        second_user = resp.json()

        resp = await client.post(
            f"/projects/{created_project['id']}/members",
            json={"user_id": second_user["id"], "role": "member"},
            headers=second_auth_headers,
        )
        assert resp.status_code == 403

    async def test_add_member_user_not_found(self, client, auth_headers, created_project):
        resp = await client.post(
            f"/projects/{created_project['id']}/members",
            json={"user_id": 99999, "role": "member"},
            headers=auth_headers,
        )
        assert resp.status_code == 404

    async def test_add_member_already_exists(self, client, auth_headers, second_auth_headers, created_project):
        resp = await client.get("/users/me", headers=second_auth_headers)
        second_user = resp.json()
        await client.post(
            f"/projects/{created_project['id']}/members",
            json={"user_id": second_user["id"], "role": "member"},
            headers=auth_headers,
        )
        resp = await client.post(
            f"/projects/{created_project['id']}/members",
            json={"user_id": second_user["id"], "role": "member"},
            headers=auth_headers,
        )
        assert resp.status_code == 400


class TestUpdateMemberRole:
    async def test_update_role_success(self, client, auth_headers, second_auth_headers, created_project):
        resp = await client.get("/users/me", headers=second_auth_headers)
        second_user = resp.json()

        await client.post(
            f"/projects/{created_project['id']}/members",
            json={"user_id": second_user["id"], "role": "member"},
            headers=auth_headers,
        )

        resp = await client.patch(
            f"/projects/{created_project['id']}/members/{second_user['id']}",
            json={"role": "admin"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        assert resp.json()["role"] == "admin"

    async def test_update_role_not_admin(self, client, auth_headers, second_auth_headers, created_project):
        resp = await client.get("/users/me", headers=second_auth_headers)
        second_user = resp.json()

        await client.post(
            f"/projects/{created_project['id']}/members",
            json={"user_id": second_user["id"], "role": "member"},
            headers=auth_headers,
        )

        resp = await client.patch(
            f"/projects/{created_project['id']}/members/{second_user['id']}",
            json={"role": "admin"},
            headers=second_auth_headers,
        )
        assert resp.status_code == 403


class TestRemoveMember:
    async def test_remove_member_success(self, client, auth_headers, second_auth_headers, created_project):
        resp = await client.get("/users/me", headers=second_auth_headers)
        second_user = resp.json()

        await client.post(
            f"/projects/{created_project['id']}/members",
            json={"user_id": second_user["id"], "role": "member"},
            headers=auth_headers,
        )

        resp = await client.delete(
            f"/projects/{created_project['id']}/members/{second_user['id']}",
            headers=auth_headers,
        )
        assert resp.status_code == 200

    async def test_remove_member_not_admin(self, client, auth_headers, second_auth_headers, created_project):
        resp = await client.get("/users/me", headers=second_auth_headers)
        second_user = resp.json()

        await client.post(
            f"/projects/{created_project['id']}/members",
            json={"user_id": second_user["id"], "role": "member"},
            headers=auth_headers,
        )

        resp = await client.delete(
            f"/projects/{created_project['id']}/members/{second_user['id']}",
            headers=second_auth_headers,
        )
        assert resp.status_code == 403

    async def test_remove_owner_forbidden(self, client, auth_headers, created_project):
        resp = await client.get("/users/me", headers=auth_headers)
        owner = resp.json()

        resp = await client.delete(
            f"/projects/{created_project['id']}/members/{owner['id']}",
            headers=auth_headers,
        )
        assert resp.status_code == 400


class TestJoinProject:
    async def test_join_success(self, client, second_auth_headers, created_project_with_secret):
        project_id = created_project_with_secret["id"]
        invite = f"{project_id}/mysecret123"

        resp = await client.post("/projects/join", json={"invite": invite}, headers=second_auth_headers)
        assert resp.status_code == 201
        assert resp.json()["role"] == "member"

    async def test_join_invalid_format(self, client, second_auth_headers):
        resp = await client.post("/projects/join", json={"invite": "badformat"}, headers=second_auth_headers)
        assert resp.status_code == 400

    async def test_join_wrong_secret(self, client, second_auth_headers, created_project_with_secret):
        invite = f"{created_project_with_secret['id']}/wrongkey"

        resp = await client.post("/projects/join", json={"invite": invite}, headers=second_auth_headers)
        assert resp.status_code == 403

    async def test_join_project_not_found(self, client, second_auth_headers):
        resp = await client.post("/projects/join", json={"invite": "nonexistent-uuid/key"}, headers=second_auth_headers)
        assert resp.status_code == 404

    async def test_join_no_secret_key(self, client, second_auth_headers, created_project):
        invite = f"{created_project['id']}/anykey"

        resp = await client.post("/projects/join", json={"invite": invite}, headers=second_auth_headers)
        assert resp.status_code == 400

    async def test_join_already_member(self, client, auth_headers, created_project_with_secret):
        invite = f"{created_project_with_secret['id']}/mysecret123"

        resp = await client.post("/projects/join", json={"invite": invite}, headers=auth_headers)
        assert resp.status_code == 400

    async def test_join_unauthorized(self, client):
        resp = await client.post("/projects/join", json={"invite": "any-uuid/key"})
        assert resp.status_code == 401
