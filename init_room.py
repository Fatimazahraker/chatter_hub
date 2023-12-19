from app import app, db, Room

def add_default_rooms():
    with app.app_context():
        # Create or initialize default rooms
        default_user_id = 1  # Change this to the default user ID you want
        for room_name in ["lounge", "news", "games", "coding"]:
            existing_room = Room.query.filter_by(name=room_name).first()
            if not existing_room:
                new_room = Room(name=room_name, created_by=default_user_id)
                db.session.add(new_room)
                db.session.commit()

if __name__ == "__main__":
    add_default_rooms()
