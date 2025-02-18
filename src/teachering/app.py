from flask import Flask, request, jsonify
from flask_jwt_extended import (
    JWTManager, create_access_token, create_refresh_token, 
    jwt_required, get_jwt_identity, get_jwt
)
from flask_bcrypt import Bcrypt
from peewee import *
from flask_caching import Cache

# 初始化 Flask
app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = "your_secret_key"  # 請換成安全的密鑰
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

# 設定 SQLite 資料庫
db = SqliteDatabase("attendance.db")

# 使用 Peewee 定義 User 模型
class User(Model):
    email = CharField(unique=True)
    password_hash = CharField()
    role = CharField(choices=[("teacher", "teacher"), ("student", "student")])

    class Meta:
        database = db

# 創建資料表（如果不存在）
db.connect()
db.create_tables([User])


# 註冊 API
@app.route("/auth/register", methods=["POST"])
def register():
    data = request.json
    email = data.get("email")
    password = data.get("password")
    role = data.get("role")

    if not email or not password or role not in ["teacher", "student"]:
        return jsonify({"error": "Invalid data"}), 400

    if User.select().where(User.email == email).exists():
        return jsonify({"error": "User already exists"}), 400

    password_hash = bcrypt.generate_password_hash(password).decode("utf-8")
    user = User.create(email=email, password_hash=password_hash, role=role)
    
    return jsonify({"message": "User registered successfully"}), 201

# 登入 API
@app.route("/auth/login", methods=["POST"])
def login():
    data = request.json
    email = data.get("email")
    password = data.get("password")

    user = User.get_or_none(User.email == email)
    if not user or not bcrypt.check_password_hash(user.password_hash, password):
        return jsonify({"error": "Invalid credentials"}), 401

    access_token = create_access_token(identity=user.email, additional_claims={"role": user.role})
    refresh_token = create_refresh_token(identity=user.email)

    return jsonify({
        "access_token": access_token,
        "refresh_token": refresh_token
    }), 200

# 刷新 Access Token API
@app.route("/auth/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    new_access_token = create_access_token(identity=identity)
    return jsonify({"access_token": new_access_token}), 200

# 測試 API（需要登入）
@app.route("/protected", methods=["GET"])
@jwt_required()
def protected():
    current_user = get_jwt_identity()
    return jsonify({"message": f"Hello, {current_user['email']}!"}), 200


# 初始化 Flask-Caching（使用 SQLite 儲存黑名單）
app.config["CACHE_TYPE"] = "simple"  # 或使用 Redis、Memcached
cache = Cache(app)
cache.init_app(app)

# 黑名單存儲機制
TOKEN_BLACKLIST = "token_blacklist"


# 登出 API（將 Refresh Token 加入黑名單）
@app.route("/auth/logout", methods=["POST"])
@jwt_required(refresh=True)
def logout():
    # print(get_jwt_identity())  # Debug 用，查看 token 是否解析成功
    jti = get_jwt()["jti"]  # 取得 Token 唯一 ID
    cache.set(f"{TOKEN_BLACKLIST}:{jti}", True, timeout=604800)  # 設定 7 天有效（跟 Refresh Token 週期一致）
    return jsonify({"message": "Successfully logged out"}), 200

# 攔截黑名單中的 Token
@jwt.token_in_blocklist_loader
def check_if_token_in_blacklist(jwt_header, jwt_payload):
    jti = jwt_payload["jti"]
    return cache.get(f"{TOKEN_BLACKLIST}:{jti}") is not None


if __name__ == "__main__":
    app.run(debug=True)
