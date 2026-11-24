from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app


def test_logout_revokes_refresh_token_without_access_token() -> None:
    email = f"logout-{uuid4()}@example.com"
    with TestClient(app) as client:
        assert client.post(
            "/api/v1/auth/register",
            json={"email": email, "name": "Logout User", "password": "strong-password"},
        ).status_code == 201
        login = client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": "strong-password"},
        )
        refresh_token = login.json()["refresh_token"]

        logout = client.post(
            "/api/v1/auth/logout",
            json={"refresh_token": refresh_token},
        )

        assert logout.status_code == 204
        assert client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token},
        ).status_code == 401


def test_logout_is_idempotent_for_unknown_or_already_revoked_token() -> None:
    with TestClient(app) as client:
        payload = {"refresh_token": "unknown-refresh-token"}
        assert client.post("/api/v1/auth/logout", json=payload).status_code == 204
        assert client.post("/api/v1/auth/logout", json=payload).status_code == 204


def test_full_budget_discovery_flow() -> None:
    email = f"user-{uuid4()}@example.com"

    with TestClient(app) as client:
        readiness_response = client.get("/api/v1/health/ready")
        assert readiness_response.status_code == 200
        assert readiness_response.json()["status"] == "ready"

        register_response = client.post(
            "/api/v1/auth/register",
            json={"email": email, "name": "Test User", "password": "strong-password"},
        )
        assert register_response.status_code == 201, register_response.text

        login_response = client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": "strong-password"},
        )
        assert login_response.status_code == 200, login_response.text
        tokens = login_response.json()
        headers = {"Authorization": f"Bearer {tokens['access_token']}"}

        forbidden_response = client.get("/api/v1/users", headers=headers)
        assert forbidden_response.status_code == 403

        types_response = client.get("/api/v1/organization-types")
        assert types_response.status_code == 200
        restaurant_type = next(
            item for item in types_response.json() if item["code"] == "restaurant"
        )

        organization_response = client.post(
            "/api/v1/organizations",
            headers=headers,
            json={
                "type_id": restaurant_type["id"],
                "name": "Test Restaurant",
                "city": "Astrakhan",
            },
        )
        assert organization_response.status_code == 201, organization_response.text
        organization = organization_response.json()

        organization_detail_response = client.get(f"/api/v1/organizations/{organization['id']}")
        assert organization_detail_response.status_code == 200
        assert organization_detail_response.json()["id"] == organization["id"]

        filtered_organizations_response = client.get(
            "/api/v1/organizations",
            params={"city": "  astrakhan  "},
        )
        assert filtered_organizations_response.status_code == 200
        assert [item["id"] for item in filtered_organizations_response.json()] == [
            organization["id"]
        ]

        my_organizations_response = client.get(
            "/api/v1/organizations/mine",
            headers=headers,
        )
        assert my_organizations_response.status_code == 200
        assert [item["id"] for item in my_organizations_response.json()] == [organization["id"]]

        catalog_response = client.post(
            f"/api/v1/organizations/{organization['id']}/catalogs",
            headers=headers,
            json={"name": "Меню"},
        )
        assert catalog_response.status_code == 201, catalog_response.text
        catalog = catalog_response.json()
        assert client.get(f"/api/v1/catalogs/{catalog['id']}").status_code == 200

        duplicate_catalog_response = client.post(
            f"/api/v1/organizations/{organization['id']}/catalogs",
            headers=headers,
            json={"name": "Меню"},
        )
        assert duplicate_catalog_response.status_code == 409

        second_email = f"second-{uuid4()}@example.com"
        assert (
            client.post(
                "/api/v1/auth/register",
                json={
                    "email": second_email,
                    "name": "Second User",
                    "password": "strong-password",
                },
            ).status_code
            == 201
        )
        second_login = client.post(
            "/api/v1/auth/login",
            json={"email": second_email, "password": "strong-password"},
        )
        second_headers = {"Authorization": f"Bearer {second_login.json()['access_token']}"}
        forbidden_catalog_response = client.post(
            f"/api/v1/organizations/{organization['id']}/catalogs",
            headers=second_headers,
            json={"name": "Чужой каталог"},
        )
        assert forbidden_catalog_response.status_code == 403

        category_response = client.post(
            f"/api/v1/catalogs/{catalog['id']}/categories",
            headers=headers,
            json={"name": "Основные блюда"},
        )
        assert category_response.status_code == 201, category_response.text
        assert client.get(f"/api/v1/categories/{category_response.json()['id']}").status_code == 200

        item_response = client.post(
            f"/api/v1/catalogs/{catalog['id']}/items",
            headers=headers,
            json={
                "name": "Ужин на двоих",
                "price": "1800.00",
                "category_id": category_response.json()["id"],
                "price_unit": "item",
                "attributes": {"serves": 2},
            },
        )
        assert item_response.status_code == 201, item_response.text
        assert client.get(f"/api/v1/items/{item_response.json()['id']}").status_code == 200

        usd_item_response = client.post(
            f"/api/v1/catalogs/{catalog['id']}/items",
            headers=headers,
            json={
                "name": "Foreign currency item",
                "price": "10.00",
                "category_id": category_response.json()["id"],
                "currency": "USD",
            },
        )
        assert usd_item_response.status_code == 201, usd_item_response.text

        recommendation_response = client.get(
            "/api/v1/recommendations",
            params={
                "budget": "2500",
                "party_size": 2,
                "organization_type_id": restaurant_type["id"],
                "city": "Astrakhan",
            },
        )
        assert recommendation_response.status_code == 200, recommendation_response.text
        recommendations = recommendation_response.json()
        assert any(item["organization"]["id"] == organization["id"] for item in recommendations)
        assert all(
            item["currency"] == "RUB"
            for recommendation in recommendations
            for item in recommendation["suggested_items"]
        )

        invalid_pagination_response = client.get("/api/v1/organizations", params={"limit": 0})
        assert invalid_pagination_response.status_code == 422

        refresh_response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": tokens["refresh_token"]},
        )
        assert refresh_response.status_code == 200, refresh_response.text
        assert refresh_response.json()["refresh_token"] != tokens["refresh_token"]

        reused_response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": tokens["refresh_token"]},
        )
        assert reused_response.status_code == 401

        revoked_family_response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_response.json()["refresh_token"]},
        )
        assert revoked_family_response.status_code == 401

        admin_login = client.post(
            "/api/v1/auth/login",
            json={"email": "admin@example.com", "password": "test-admin-password"},
        )
        assert admin_login.status_code == 200, admin_login.text
        admin_headers = {"Authorization": f"Bearer {admin_login.json()['access_token']}"}

        admin_catalog_response = client.post(
            f"/api/v1/organizations/{organization['id']}/catalogs",
            headers=admin_headers,
            json={"name": "Каталог администратора"},
        )
        assert admin_catalog_response.status_code == 201, admin_catalog_response.text

        permissions_response = client.get("/api/v1/permissions", headers=admin_headers)
        assert permissions_response.status_code == 200, permissions_response.text
        assert any(
            permission["code"] == "roles:manage" for permission in permissions_response.json()
        )

        suffix = uuid4().hex[:8]
        custom_permission_response = client.post(
            "/api/v1/permissions",
            headers=admin_headers,
            json={
                "code": f"reports:{suffix}",
                "name": "Просмотр отчётов",
            },
        )
        assert custom_permission_response.status_code == 201
        custom_permission = custom_permission_response.json()

        role_response = client.post(
            "/api/v1/roles",
            headers=admin_headers,
            json={
                "name": f"analyst-{suffix}",
                "permissions": [custom_permission["code"]],
            },
        )
        assert role_response.status_code == 201, role_response.text
        role = role_response.json()
        assert role["permissions"][0]["id"] == custom_permission["id"]

        second_permission_response = client.post(
            "/api/v1/permissions",
            headers=admin_headers,
            json={
                "code": f"exports:{suffix}",
                "name": "Экспорт отчётов",
            },
        )
        assert second_permission_response.status_code == 201
        assign_response = client.post(
            f"/api/v1/roles/{role['id']}/permissions",
            headers=admin_headers,
            json={"permission_id": second_permission_response.json()["id"]},
        )
        assert assign_response.status_code == 200, assign_response.text
        assert {permission["code"] for permission in assign_response.json()["permissions"]} == {
            custom_permission["code"],
            second_permission_response.json()["code"],
        }
