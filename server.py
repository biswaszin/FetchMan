from flask import Flask, request, jsonify

server = Flask(__name__)

users = [
    {"id": 1, "name": "Ankit", "email": "ankit@fetchman.dev", "role": "admin"},
    {"id": 2, "name": "Sayak", "email": "sayak@fetchman.dev", "role": "user"},
    {"id": 3, "name": "Debadrita", "email": "debadrita@fetchman.dev", "role": "user"},
]

products = [
    {"id": 1, "name": "Laptop Pro", "price": 1299.99, "category": "electronics"},
    {"id": 2, "name": "Wireless Mouse", "price": 29.99, "category": "electronics"},
    {"id": 3, "name": "Standing Desk", "price": 499.00, "category": "furniture"},
    {"id": 4, "name": "Coffee Mug", "price": 12.50, "category": "kitchen"},
]


@server.route("/healthz")
def health_check():
    return jsonify({"status": "ok", "service": "FetchMan Demo Server"})


@server.route("/users", methods=["GET"])
def get_users():
    return jsonify({"users": users, "total": len(users)})


@server.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    user = next((u for u in users if u["id"] == user_id), None)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user)


@server.route("/users", methods=["POST"])
def create_user():
    body = request.get_json()
    if not body or "name" not in body or "email" not in body:
        return jsonify({"error": "name and email are required"}), 400
    new_user = {
        "id": max(u["id"] for u in users) + 1,
        "name": body["name"],
        "email": body["email"],
        "role": body.get("role", "user"),
    }
    users.append(new_user)
    return jsonify(new_user), 201


@server.route("/users/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    user = next((u for u in users if u["id"] == user_id), None)
    if not user:
        return jsonify({"error": "User not found"}), 404
    body = request.get_json()
    if not body:
        return jsonify({"error": "Request body must be JSON"}), 400
    user.update({key: value for key, value in body.items() if key != "id"})
    return jsonify(user)


@server.route("/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    user = next((u for u in users if u["id"] == user_id), None)
    if not user:
        return jsonify({"error": "User not found"}), 404
    users.remove(user)
    return jsonify({"message": f"User {user_id} deleted"})


@server.route("/products", methods=["GET"])
def get_products():
    category = request.args.get("category")
    result = [p for p in products if p["category"] == category] if category else products
    return jsonify({"products": result, "total": len(result)})


@server.route("/products/<int:product_id>", methods=["GET"])
def get_product(product_id):
    product = next((p for p in products if p["id"] == product_id), None)
    if not product:
        return jsonify({"error": "Product not found"}), 404
    return jsonify(product)


if __name__ == "__main__":
    server.run(debug=True, port=5000)
