def test_healthz(client):
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"


def test_get_users(client):
    response = client.get("/users")
    assert response.status_code == 200
    data = response.get_json()
    assert data["total"] == 3
    assert len(data["users"]) == 3


def test_get_user(client):
    response = client.get("/users/1")
    assert response.status_code == 200
    assert response.get_json()["name"] == "Alex"


def test_get_user_not_found(client):
    response = client.get("/users/999")
    assert response.status_code == 404


def test_create_user(client):
    response = client.post("/users", json={"name": "Reyna", "email": "reyna@fetchman.dev"})
    assert response.status_code == 201
    data = response.get_json()
    assert data["name"] == "Reyna"
    assert data["id"] == 4


def test_create_user_missing_fields(client):
    response = client.post("/users", json={"name": "No Email"})
    assert response.status_code == 400


def test_update_user(client):
    response = client.put("/users/2", json={"name": "Killjoy"})
    assert response.status_code == 200
    assert response.get_json()["name"] == "Killjoy"


def test_update_user_not_found(client):
    response = client.put("/users/999", json={"name": "Ghost"})
    assert response.status_code == 404


def test_delete_user(client):
    response = client.delete("/users/3")
    assert response.status_code == 200
    assert client.get("/users/3").status_code == 404


def test_delete_user_not_found(client):
    response = client.delete("/users/999")
    assert response.status_code == 404


def test_get_products(client):
    response = client.get("/products")
    assert response.status_code == 200
    assert response.get_json()["total"] == 4


def test_get_products_by_category(client):
    response = client.get("/products?category=electronics")
    assert response.status_code == 200
    data = response.get_json()
    assert data["total"] == 2
    assert all(p["category"] == "electronics" for p in data["products"])


def test_get_product(client):
    response = client.get("/products/1")
    assert response.status_code == 200
    assert response.get_json()["name"] == "Laptop Pro"


def test_get_product_not_found(client):
    response = client.get("/products/999")
    assert response.status_code == 404
