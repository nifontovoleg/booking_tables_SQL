from postgres_driver import PostgresDriver
from models.user import User
from models.tables import Table
from models.booking import Booking
from datetime import datetime


def create_tables():
    db = PostgresDriver()
    db.create_table_from_model(User, "users")
    db.create_table_from_model(Table, "tables")
    db.create_table_from_model(Booking, "bookings")
    db.close()


if __name__ == "__main__":
    create_tables()
    print("Таблицы созданы")


# ==================== USERS CRUD ====================
def create_user(name: str, email: str = None, phone: str = None, age: int = None, is_active: bool = True) -> int:
    with PostgresDriver() as db:
        with db.conn.cursor() as cur:
            cur.execute(
                """INSERT INTO users (name, email, phone, age, is_active)
                   VALUES (%s, %s, %s, %s, %s) RETURNING id""",
                (name, email, phone, age, is_active),
            )
            return cur.fetchone()[0]


def get_user(user_id: int) -> dict:
    with PostgresDriver() as db:
        with db.conn.cursor() as cur:
            cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
            row = cur.fetchone()
            if row:
                return dict(zip([col[0] for col in cur.description], row))
            return None


def update_user(user_id: int, name: str = None, email: str = None, phone: str = None,
                age: int = None, is_active: bool = None) -> bool:
    with PostgresDriver() as db:
        with db.conn.cursor() as cur:
            cur.execute("""UPDATE users SET name=COALESCE(%s, name), email=COALESCE(%s, email),
                phone=COALESCE(%s, phone), age=COALESCE(%s, age), is_active=COALESCE(%s, is_active)
                WHERE id = %s RETURNING id""",
                (name, email, phone, age, is_active, user_id))
            return cur.fetchone() is not None


def delete_user(user_id: int) -> bool:
    with PostgresDriver() as db:
        with db.conn.cursor() as cur:
            cur.execute("DELETE FROM users WHERE id = %s RETURNING id", (user_id,))
            return cur.fetchone() is not None


def get_all_users() -> list:
    with PostgresDriver() as db:
        with db.conn.cursor() as cur:
            cur.execute("SELECT * FROM users ORDER BY id")
            return [dict(zip([col[0] for col in cur.description], row)) for row in cur.fetchall()]


# ==================== TABLES CRUD ====================
def create_table(number: int, capacity: int, location: str = None, is_outdoor: bool = False,
                 is_reserved: bool = False, description: str = None) -> int:
    with PostgresDriver() as db:
        with db.conn.cursor() as cur:
            cur.execute(
                """INSERT INTO tables (number, capacity, location, is_outdoor, is_reserved, description)
                   VALUES (%s, %s, %s, %s, %s, %s) RETURNING id""",
                (number, capacity, location, is_outdoor, is_reserved, description),
            )
            return cur.fetchone()[0]


def get_table(table_id: int) -> dict:
    with PostgresDriver() as db:
        with db.conn.cursor() as cur:
            cur.execute("SELECT * FROM tables WHERE id = %s", (table_id,))
            row = cur.fetchone()
            if row:
                return dict(zip([col[0] for col in cur.description], row))
            return None


def update_table(table_id: int, number: int = None, capacity: int = None, location: str = None,
                 is_outdoor: bool = None, is_reserved: bool = None, description: str = None) -> bool:
    with PostgresDriver() as db:
        with db.conn.cursor() as cur:
            cur.execute("""UPDATE tables SET number=COALESCE(%s, number), capacity=COALESCE(%s, capacity),
                location=COALESCE(%s, location), is_outdoor=COALESCE(%s, is_outdoor),
                is_reserved=COALESCE(%s, is_reserved), description=COALESCE(%s, description)
                WHERE id = %s RETURNING id""",
                (number, capacity, location, is_outdoor, is_reserved, description, table_id))
            return cur.fetchone() is not None


def delete_table(table_id: int) -> bool:
    with PostgresDriver() as db:
        with db.conn.cursor() as cur:
            cur.execute("DELETE FROM tables WHERE id = %s RETURNING id", (table_id,))
            return cur.fetchone() is not None


def get_all_tables() -> list:
    with PostgresDriver() as db:
        with db.conn.cursor() as cur:
            cur.execute("SELECT * FROM tables ORDER BY id")
            return [dict(zip([col[0] for col in cur.description], row)) for row in cur.fetchall()]


# ==================== BOOKINGS CRUD ====================
def create_booking(user_id: int, table_id: int, start_time: datetime, end_time: datetime,
                   guests: int = None, status: str = "pending", notes: str = None) -> int:
    with PostgresDriver() as db:
        with db.conn.cursor() as cur:
            cur.execute(
                """INSERT INTO bookings (user_id, table_id, start_time, end_time, guests, status, notes)
                   VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id""",
                (user_id, table_id, start_time, end_time, guests, status, notes),
            )
            return cur.fetchone()[0]


def get_booking(booking_id: int) -> dict:
    with PostgresDriver() as db:
        with db.conn.cursor() as cur:
            cur.execute("SELECT * FROM bookings WHERE id = %s", (booking_id,))
            row = cur.fetchone()
            if row:
                return dict(zip([col[0] for col in cur.description], row))
            return None


def update_booking(booking_id: int, user_id: int = None, table_id: int = None,
                   start_time: datetime = None, end_time: datetime = None,
                   guests: int = None, status: str = None, notes: str = None) -> bool:
    with PostgresDriver() as db:
        with db.conn.cursor() as cur:
            cur.execute("""UPDATE bookings SET user_id=COALESCE(%s, user_id), table_id=COALESCE(%s, table_id),
                start_time=COALESCE(%s, start_time), end_time=COALESCE(%s, end_time),
                guests=COALESCE(%s, guests), status=COALESCE(%s, status), notes=COALESCE(%s, notes)
                WHERE id = %s RETURNING id""",
                (user_id, table_id, start_time, end_time, guests, status, notes, booking_id))
            return cur.fetchone() is not None


def delete_booking(booking_id: int) -> bool:
    with PostgresDriver() as db:
        with db.conn.cursor() as cur:
            cur.execute("DELETE FROM bookings WHERE id = %s RETURNING id", (booking_id,))
            return cur.fetchone() is not None


def get_all_bookings() -> list:
    with PostgresDriver() as db:
        with db.conn.cursor() as cur:
            cur.execute("SELECT * FROM bookings ORDER BY id")
            return [dict(zip([col[0] for col in cur.description], row)) for row in cur.fetchall()]