from werkzeug.security import generate_password_hash
from datetime import datetime
from app import app
from models import (
    db,
    Admin,
    House,
    Captain,
    Advisor,
    Member,
    Achievement,
    Announcement
)

PASSWORD = generate_password_hash("tes123")


def seed_mock_data():
    with app.app_context():

        # ================= ADMIN =================
        if not Admin.query.first():
            admin = Admin(
                name="System Admin",
                username="admin",
                password_hash=PASSWORD
            )
            db.session.add(admin)

        # ================= HOUSES =================
        houses_data = [
            (
                "Al-Ghuraab",
                "Al-Ghuraab (الغراب) — Inspired by the crow mentioned in the Qur’an. "
                "Represents learning through observation, humility, and moral awareness."
            ),
            (
                "An-Nahl",
                "An-Nahl (النحل) — Inspired by the bee mentioned in the Qur’an. "
                "Symbolizes productivity, order, obedience, and service to others."
            ),
            (
                "An-Nun",
                "An-Nun (النون) — Inspired by the great fish associated with Prophet Yunus. "
                "Represents patience, repentance, resilience, and self-reflection."
            ),
            (
                "Al-Adiyat",
                "Al-Adiyat (العاديات) — Inspired by the charging horses mentioned in the Qur’an. "
                "Symbolizes discipline, loyalty, determination, and relentless effort."
            ),
            (
                "Al-Hudhud",
                "Al-Hudhud (الهدهد) — Inspired by the hoopoe bird mentioned in the Qur’an. "
                "Represents intelligence, communication, courage, and responsibility."
            ),
            (
                "An-Naml",
                "An-Naml (النمل) — Inspired by the ants mentioned in the Qur’an. "
                "Symbolizes teamwork, awareness, humility, and care for the community."
            ),
        ]


        houses = {}
        for name, desc in houses_data:
            house = House.query.filter_by(name=name).first()
            if not house:
                house = House(
                    name=name,
                    description=desc,
                    house_points=0
                )
                db.session.add(house)
            houses[name] = house

        db.session.flush()

        # ================= CAPTAINS =================
        captains_data = [
            ("Captain Ghuraab", "ghuraab", "Al-Ghuraab"),
            ("Captain Nahl", "nahl", "An-Nahl"),
            ("Captain Nun", "nun", "An-Nun"),
            ("Captain Adiyat", "adiyat", "Al-Adiyat"),
            ("Captain Hudhud", "hudhud", "Al-Hudhud"),
            ("Captain Naml", "naml", "An-Naml"),
        ]

        for name, username, house_name in captains_data:
            if not Captain.query.filter_by(username=username).first():
                db.session.add(
                    Captain(
                        name=name,
                        username=username,
                        password_hash=PASSWORD,
                        house_id=houses[house_name].id
                    )
                )

        db.session.flush()

        # ================= ANNOUNCEMENTS =================
        announcements_data = [
            ("Welcome Announcement", "Welcome to the new house season!"),
            ("Training Session", "House training will begin this Friday."),
            ("Team Reminder", "Remember to wear house shirts every Monday."),
        ]

        for captain in Captain.query.all():
            for title, content in announcements_data:
                exists = Announcement.query.filter_by(
                    title=title,
                    captain_id=captain.id
                ).first()

                if not exists:
                    db.session.add(
                        Announcement(
                            title=title,
                            content=content,
                            created_at=datetime.utcnow(),
                            house_id=captain.house_id,
                            captain_id=captain.id
                        )
                    )

        # ================= ADVISORS =================
        advisors_data = [
            ("Mr. Rahman", "House Advisor", "rahman", "Al-Ghuraab"),
            ("Ms. Aisyah", "House Advisor", "aisyah", "An-Nahl"),
            ("Mr. Yusuf", "House Advisor", "yusuf", "An-Nun"),
            ("Ms. Hana", "House Advisor", "hana", "Al-Adiyat"),
            ("Mr. Salman", "House Advisor", "salman", "Al-Hudhud"),
            ("Ms. Zahra", "House Advisor", "zahra", "An-Naml"),
        ]

        for name, role, username, house_name in advisors_data:
            if not Advisor.query.filter_by(username=username).first():
                db.session.add(
                    Advisor(
                        name=name,
                        role=role,
                        bio=f"{name} supervises and guides house members.",
                        username=username,
                        password_hash=PASSWORD,
                        house_id=houses[house_name].id
                    )
                )

        # ================= MEMBERS =================
        members_data = [
            ("Ahmad", "Member", "Al-Ghuraab"),
            ("Fatimah", "Member", "Al-Ghuraab"),
            ("Ali", "Member", "An-Nahl"),
            ("Amina", "Member", "An-Nahl"),
            ("Umar", "Member", "An-Nun"),
            ("Khadijah", "Member", "An-Nun"),
            ("Hasan", "Member", "Al-Adiyat"),
            ("Husain", "Member", "Al-Adiyat"),
            ("Bilal", "Member", "Al-Hudhud"),
            ("Zainab", "Member", "Al-Hudhud"),
            ("Yasir", "Member", "An-Naml"),
            ("Maryam", "Member", "An-Naml"),
        ]

        for name, role, house_name in members_data:
            if not Member.query.filter_by(
                name=name,
                house_id=houses[house_name].id
            ).first():
                db.session.add(
                    Member(
                        name=name,
                        role=role,
                        house_id=houses[house_name].id
                    )
                )

        # ================= ACHIEVEMENTS =================
        achievements_data = [
            ("Cleanest House", "Maintained the cleanest environment"),
            ("Best Teamwork", "Excellent collaboration among members"),
            ("Top Discipline", "Outstanding discipline and conduct"),
        ]

        for house in houses.values():
            for title, desc in achievements_data:
                if not Achievement.query.filter_by(
                    name=title,
                    house_id=house.id
                ).first():
                    db.session.add(
                        Achievement(
                            name=title,
                            description=desc,
                            house_id=house.id
                        )
                    )

        db.session.commit()
        print("Mock data seeding completed ✅")

if __name__ == "__main__":
    seed_mock_data()
