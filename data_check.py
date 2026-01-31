from app import app
from models import (
    db,
    Admin,
    House,
    Captain,
    Advisor,
    Member,
    Achievement,
    Announcement,
    PointTransaction
)

def check_tables():
    with app.app_context():
        print("=== TABLE CONTENT CHECK ===")
        print(f"Admins: {Admin.query.count()}")
        print(f"Houses: {House.query.count()}")
        print(f"Captains: {Captain.query.count()}")
        print(f"Advisors: {Advisor.query.count()}")
        print(f"Members: {Member.query.count()}")
        print(f"Achievements: {Achievement.query.count()}")
        print(f"Announcements: {Announcement.query.count()}")
        print(f"Point Transactions: {PointTransaction.query.count()}")
        print("===========================")

if __name__ == "__main__":
    check_tables()
