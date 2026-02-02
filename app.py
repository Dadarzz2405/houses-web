import os
from flask import Flask, redirect, abort, request, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from flask_migrate import Migrate
from functools import wraps
from flask_cors import CORS
from models import Announcement, PointTransaction, db, Admin, House, Captain, Member, Achievement
from werkzeug.middleware.proxy_fix import ProxyFix
from datetime import datetime

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = \
    'sqlite:///' + os.path.join(basedir, 'app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get(
    'SECRET_KEY',
    '330bf9312848e19d9a88482a033cb4f566c4cbe06911fe1e452ebade42f0bc4c'
)
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Session config for cross-origin cookies
app.config.update(
    SESSION_COOKIE_SAMESITE="None",
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
)

CORS(
    app,
    supports_credentials=True,
    resources={
        r"/*": {
            "origins": [
                "http://localhost:5173",
                "https://darsahouse.netlify.app",
                "https://houses-web.onrender.com",
            ]
        }
    }
)

db.init_app(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# =====================
# Auth helpers
# =====================

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not isinstance(current_user, Admin):
            return jsonify({"error": "Admin access required"}), 403
        return f(*args, **kwargs)
    return decorated

def captain_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not isinstance(current_user, Captain):
            return jsonify({"error": "Captain access required"}), 403
        return f(*args, **kwargs)
    return decorated

@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id)) or Captain.query.get(int(user_id))

@login_manager.unauthorized_handler
def unauthorized():
    return jsonify({"error": "Unauthorized"}), 401

# =====================
# PUBLIC API
# =====================

@app.route("/api/houses")
def get_houses():
    houses = House.query.order_by(House.name).all()
    return jsonify([
        {
            "id": h.id,
            "name": h.name,
            "points": h.house_points,
            "description": h.description
        }
        for h in houses
    ])

@app.route('/api/live-points')
def live_scores():
    houses = House.query.order_by(House.house_points.desc()).all()
    return jsonify([
        {
            "rank": i + 1,
            "name": h.name,
            "points": h.house_points,
            "description": h.description
        }
        for i, h in enumerate(houses)
    ])

@app.route('/api/members')
def members():
    house_name = request.args.get('house')
    houses = (
        [House.query.filter_by(name=house_name).first()]
        if house_name else
        House.query.order_by(House.name).all()
    )

    if house_name and not houses[0]:
        return jsonify({"error": "House not found"}), 404

    return jsonify([
        {
            "house": {
                "id": h.id,
                "name": h.name,
                "description": h.description
            },
            "members": [
                {
                    "id": m.id,
                    "name": m.name,
                    "role": m.role
                }
                for m in Member.query.filter_by(house_id=h.id).all()
            ]
        }
        for h in houses
    ])

@app.route('/api/announcements')
def announcements():
    anns = Announcement.query.order_by(Announcement.created_at.desc()).all()
    return jsonify([
        {
            "id": a.id,
            "title": a.title,
            "content": a.content,
            "created_at": a.created_at.isoformat(),
            "house": {"id": a.house.id, "name": a.house.name},
            "captain": {
                "id": a.captain.id,
                "username": a.captain.username,
                "name": a.captain.name
            }
        }
        for a in anns
    ])

# =====================
# LOGIN / LOGOUT
# =====================

@app.route('/api/login', methods=['POST'])
def api_login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = (
        Admin.query.filter_by(username=username).first()
        or Captain.query.filter_by(username=username).first()
    )

    if user and check_password_hash(user.password_hash, password):
        login_user(user, remember=True)

        return jsonify({
            "success": True,
            "role": "admin" if isinstance(user, Admin) else "captain",
            "user": {
                "id": user.id,
                "username": user.username,
                "name": user.name
            }
        })

    return jsonify({"error": "Invalid username or password"}), 401

@app.route('/api/me')
@login_required
def me():
    return jsonify({
        "id": current_user.id,
        "username": current_user.username,
        "name": current_user.name,
        "role": "admin" if isinstance(current_user, Admin) else "captain",
        "house_id": current_user.house_id if isinstance(current_user, Captain) else None
    })

@app.route('/api/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({"success": True, "message": "Logged out successfully"})

# =====================
# ADMIN ROUTES
# =====================

@app.route('/api/admin/dashboard', methods=['GET'])
@login_required
@admin_required
def admin_dashboard():
    houses = House.query.order_by(House.house_points.desc()).all()
    recent_transactions = PointTransaction.query.order_by(
        PointTransaction.timestamp.desc()
    ).limit(10).all()
    
    return jsonify({
        "houses": [
            {
                "id": h.id,
                "name": h.name,
                "points": h.house_points,
                "description": h.description
            }
            for h in houses
        ],
        "recent_transactions": [
            {
                "id": t.id,
                "house": {
                    "id": t.house.id,
                    "name": t.house.name
                },
                "points_change": t.points_change,
                "reason": t.reason,
                "timestamp": t.timestamp.isoformat(),
                "admin": {
                    "id": t.admin.id,
                    "name": t.admin.name
                }
            }
            for t in recent_transactions
        ]
    })

@app.route('/api/admin/points/add', methods=['POST'])
@login_required
@admin_required
def admin_add_points():
    data = request.get_json()
    house_id = data.get('house_id')
    points = data.get('points')
    reason = data.get('reason', '').strip()

    if not house_id or not points or not reason:
        return jsonify({"error": "All fields are required"}), 400

    if points <= 0:
        return jsonify({"error": "Points must be a positive integer"}), 400
    
    house = House.query.get_or_404(house_id)
    house.house_points += points

    transaction = PointTransaction(
        house_id=house.id,
        points_change=points,
        reason=reason,
        admin_id=current_user.id
    )
    db.session.add(transaction)
    db.session.commit()
    
    return jsonify({
        "success": True,
        "message": f"Successfully added {points} points to {house.name}",
        "house": {
            "id": house.id,
            "name": house.name,
            "points": house.house_points
        }
    })

@app.route('/api/admin/points/deduct', methods=['POST'])
@login_required
@admin_required
def admin_deduct_points():
    data = request.get_json()
    house_id = data.get('house_id')
    points = data.get('points')
    reason = data.get('reason', '').strip()

    if not house_id or not points or not reason:
        return jsonify({"error": "All fields are required"}), 400

    if points <= 0:
        return jsonify({"error": "Points must be a positive integer"}), 400
    
    house = House.query.get_or_404(house_id)
    house.house_points -= points

    transaction = PointTransaction(
        house_id=house.id,
        points_change=-points,  
        reason=reason,
        admin_id=current_user.id
    )
    db.session.add(transaction)
    db.session.commit()
    
    return jsonify({
        "success": True,
        "message": f"Successfully deducted {points} points from {house.name}",
        "house": {
            "id": house.id,
            "name": house.name,
            "points": house.house_points
        }
    })

# =====================
# CAPTAIN ROUTES
# =====================

@app.route('/api/captain/dashboard', methods=['GET'])
@login_required
@captain_required
def captain_dashboard():
    house = House.query.get(current_user.house_id)
    members = Member.query.filter_by(house_id=current_user.house_id).all()

    my_announcements = Announcement.query.filter_by(
        captain_id=current_user.id
    ).order_by(Announcement.created_at.desc()).all()
    
    return jsonify({
        "house": {
            "id": house.id,
            "name": house.name,
            "points": house.house_points,
            "description": house.description
        },
        "members": [
            {
                "id": m.id,
                "name": m.name,
                "role": m.role
            }
            for m in members
        ],
        "my_announcements": [
            {
                "id": a.id,
                "title": a.title,
                "content": a.content,
                "created_at": a.created_at.isoformat()
            }
            for a in my_announcements
        ]
    })

@app.route('/api/captain/announcements/create', methods=['POST'])
@login_required
@captain_required
def captain_create_announcement():
    data = request.get_json()
    title = data.get('title', '').strip()
    content = data.get('content', '').strip()

    if not title or not content:
        return jsonify({"error": "Title and content are required"}), 400
    
    if len(title) > 200:
        return jsonify({"error": "Title must be less than 200 characters"}), 400
    
    announcement = Announcement(
        title=title,
        content=content,
        house_id=current_user.house_id,
        captain_id=current_user.id,
        created_at=datetime.utcnow()
    )

    db.session.add(announcement)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Announcement created successfully",
        "announcement": {
            "id": announcement.id,
            "title": announcement.title,
            "content": announcement.content,
            "created_at": announcement.created_at.isoformat()
        }
    })

@app.route('/api/captain/announcements/<int:announcement_id>/delete', methods=['DELETE'])
@login_required
@captain_required
def captain_delete_announcement(announcement_id):
    announcement = Announcement.query.get_or_404(announcement_id)
    
    if announcement.captain_id != current_user.id:
        return jsonify({"error": "You can only delete your own announcements"}), 403
    
    db.session.delete(announcement)
    db.session.commit()
    
    return jsonify({
        "success": True,
        "message": "Announcement deleted successfully"
    })

# =====================
# ERROR HANDLERS
# =====================

@app.errorhandler(403)
def forbidden(e):
    return jsonify({"error": "Forbidden"}), 403

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)