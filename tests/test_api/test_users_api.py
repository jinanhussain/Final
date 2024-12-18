import pytest
from httpx import AsyncClient
from app.models.user_model import User, UserRole
from app.services.jwt_service import decode_token
from urllib.parse import urlencode


@pytest.mark.asyncio
async def test_user_upgrade_already_professional(async_client, admin_token, verified_user):
    headers = {"Authorization": f"Bearer {admin_token}"}
    await async_client.patch(f"/users/{verified_user.id}/upgrade-professional", headers=headers)
    response = await async_client.patch(f"/users/{verified_user.id}/upgrade-professional", headers=headers)
    assert response.status_code == 200
    assert response.json()["is_professional"] is True


@pytest.mark.asyncio
async def test_user_delete_unauthorized(async_client, user_token, verified_user):
    headers = {"Authorization": f"Bearer {user_token}"}
    response = await async_client.delete(f"/users/{verified_user.id}", headers=headers)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_update_profile_partial_data(async_client, verified_user, user_token):
    headers = {"Authorization": f"Bearer {user_token}"}
    response = await async_client.patch(
        f"/users/{verified_user.id}/profile", json={"bio": "Test Bio"}, headers=headers
    )
    assert response.status_code == 200
    assert response.json()["bio"] == "Test Bio"


@pytest.mark.asyncio
async def test_delete_non_existent_user(async_client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = await async_client.delete("/users/00000000-0000-0000-0000-000000000000", headers=headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_invalid_token_provided(async_client):
    headers = {"Authorization": "Bearer invalidtoken"}
    response = await async_client.get("/users/", headers=headers)
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_unverified_user(async_client, unverified_user):
    form_data = {"username": unverified_user.email, "password": "ValidPassword123"}
    response = await async_client.post("/login/", data=urlencode(form_data), headers={"Content-Type": "application/x-www-form-urlencoded"})
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_invalid_request_data(async_client):
    invalid_data = {"unknown_field": "value"}
    response = await async_client.post("/register/", json=invalid_data)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_user_retrieve_invalid_uuid(async_client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = await async_client.get("/users/invalid-uuid", headers=headers)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_profile_update_wrong_user(async_client, verified_user, another_user_token):
    headers = {"Authorization": f"Bearer {another_user_token}"}
    response = await async_client.patch(
        f"/users/{verified_user.id}/profile", json={"bio": "Unauthorized Bio"}, headers=headers
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_delete_user_invalid_uuid(async_client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = await async_client.delete("/users/invalid-uuid", headers=headers)
    assert response.status_code == 422


# New test cases added:

@pytest.mark.asyncio
async def test_user_profile_update_with_invalid_data(async_client, verified_user, user_token):
    headers = {"Authorization": f"Bearer {user_token}"}
    # Sending invalid data (e.g., an invalid email)
    response = await async_client.patch(
        f"/users/{verified_user.id}/profile", json={"email": "invalidemail.com"}, headers=headers
    )
    assert response.status_code == 422  # Unprocessable Entity (Invalid data)


@pytest.mark.asyncio
async def test_user_upgrade_to_professional_by_non_admin(async_client, user_token, verified_user):
    headers = {"Authorization": f"Bearer {user_token}"}
    response = await async_client.patch(f"/users/{verified_user.id}/upgrade-professional", headers=headers)
    assert response.status_code == 403  # Should be forbidden for non-admin users


@pytest.mark.asyncio
async def test_user_profile_update_without_token(async_client, verified_user):
    response = await async_client.patch(f"/users/{verified_user.id}/profile", json={"bio": "Updated Bio"})
    assert response.status_code == 401  # Unauthorized since no token is provided


@pytest.mark.asyncio
async def test_user_upgrade_to_professional_success(async_client, admin_token, verified_user):
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = await async_client.patch(f"/users/{verified_user.id}/upgrade-professional", headers=headers)
    assert response.status_code == 200
    assert response.json()["is_professional"] is True


@pytest.mark.asyncio
async def test_user_profile_update_with_missing_fields(async_client, verified_user, user_token):
    headers = {"Authorization": f"Bearer {user_token}"}
    response = await async_client.patch(
        f"/users/{verified_user.id}/profile", json={"first_name": "Updated First Name"}, headers=headers
    )
    assert response.status_code == 200
    assert response.json()["first_name"] == "Updated First Name"
    assert response.json().get("last_name") is None  # Last name should remain None


@pytest.mark.asyncio
async def test_user_update_unauthorized_access(async_client, user_token, another_verified_user):
    headers = {"Authorization": f"Bearer {user_token}"}
    response = await async_client.patch(
        f"/users/{another_verified_user.id}/profile", json={"bio": "Unauthorized Bio"}, headers=headers
    )
    assert response.status_code == 403  # Unauthorized for users to update others' profiles


@pytest.mark.asyncio
async def test_user_update_with_invalid_email(async_client, verified_user, user_token):
    headers = {"Authorization": f"Bearer {user_token}"}
    response = await async_client.patch(
        f"/users/{verified_user.id}/profile", json={"email": "invalidemail.com"}, headers=headers
    )
    assert response.status_code == 422  # Invalid email format should return 422


@pytest.mark.asyncio
async def test_user_profile_update_with_valid_data(async_client, verified_user, user_token):
    headers = {"Authorization": f"Bearer {user_token}"}
    response = await async_client.patch(
        f"/users/{verified_user.id}/profile", json={"bio": "New Bio"}, headers=headers
    )
    assert response.status_code == 200
    assert response.json()["bio"] == "New Bio"


@pytest.mark.asyncio
async def test_user_login_after_profile_update(async_client, verified_user, user_token):
    headers = {"Authorization": f"Bearer {user_token}"}
    response = await async_client.patch(
        f"/users/{verified_user.id}/profile", json={"bio": "Updated Bio"}, headers=headers
    )
    assert response.status_code == 200
    response = await async_client.get("/users/", headers=headers)
    assert response.status_code == 200
    assert "Updated Bio" in response.text
