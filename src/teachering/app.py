from flask import Flask, request, jsonify
from flask_jwt_extended import (
    JWTManager, create_access_token, create_refresh_token, 
    jwt_required, get_jwt_identity, get_jwt
)
from flask_bcrypt import Bcrypt
from peewee import *
from flask_caching import Cache
from teachering.models import User, Attendance
from flask_cors import CORS

# 初始化 Flask
app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = "your_secret_key"  # 請換成安全的密鑰
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

CORS(app)


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




# 學生簽到
@app.route("/attendance/check-in", methods=["POST"])
@jwt_required()
def check_in():
    current_user_email = get_jwt_identity()
    student = User.get_or_none(User.email == current_user_email)

    if not student or student.role != "student":
        return jsonify({"error": "Unauthorized"}), 403

    # 建立簽到記錄（初始狀態為 pending）
    Attendance.create(student=student, status="pending")
    return jsonify({"message": "Check-in submitted, waiting for approval"}), 201

# 老師查詢點名記錄
@app.route("/attendance/list", methods=["GET"])
@jwt_required()
def get_attendance_list():
    current_user_email = get_jwt_identity()
    teacher = User.get_or_none(User.email == current_user_email)

    if not teacher or teacher.role != "teacher":
        return jsonify({"error": "Unauthorized"}), 403

    records = Attendance.select(Attendance, User.email).join(User).dicts()
    return jsonify(list(records)), 200

# 老師核准/拒絕簽到
@app.route("/attendance/verify", methods=["POST"])
@jwt_required()
def verify_attendance():
    current_user_email = get_jwt_identity()
    teacher = User.get_or_none(User.email == current_user_email)

    if not teacher or teacher.role != "teacher":
        return jsonify({"error": "Unauthorized"}), 403

    data = request.json
    attendance_id = data.get("attendance_id")
    status = data.get("status")

    if status not in ["approved", "rejected"]:
        return jsonify({"error": "Invalid status"}), 400

    attendance = Attendance.get_or_none(Attendance.id == attendance_id)
    if not attendance:
        return jsonify({"error": "Attendance record not found"}), 404

    attendance.status = status
    attendance.save()
    
    return jsonify({"message": f"Attendance {status} successfully"}), 200

if __name__ == "__main__":
    app.run(debug=True)
