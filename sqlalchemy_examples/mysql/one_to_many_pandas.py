import os
from typing import List, Tuple

from dotenv import load_dotenv
import pandas as pd
from sqlalchemy import ForeignKey, String, select, text
from sqlalchemy.engine import create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship


# Source environment variables
load_dotenv()


# Define our base class
class Base(DeclarativeBase):
    pass


# Define our Teacher model
class Teacher(Base):
    __tablename__ = "teachers"

    id: Mapped[int] = mapped_column(primary_key=True)
    # You have to specify a string length for MySQL
    name: Mapped[str] = mapped_column(String(100))
    subject: Mapped[str] = mapped_column(String(100))

    # Relationship: one teacher has many students
    students: Mapped[List["Student"]] = relationship(
        back_populates="teacher", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"Teacher(id={self.id}, name={self.name}, subject={self.subject})"


# Define our Student model
class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    grade: Mapped[int] = mapped_column()

    # Foreign key to link to the teacher
    teacher_id: Mapped[int] = mapped_column(ForeignKey("teachers.id"))

    # Relationship: many students have one teacher
    teacher: Mapped["Teacher"] = relationship(back_populates="students")

    def __repr__(self) -> str:
        return f"Student(id={self.id}, name={self.name}, grade={self.grade})"


def create_sample_dataframe() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Create sample pandas DataFrames for teachers and students."""

    # Create a DataFrame for teachers
    teachers_data = {
        "name": ["Ms. Johnson", "Mr. Smith", "Dr. Garcia"],
        "subject": ["Mathematics", "History", "Science"],
    }
    teachers_df = pd.DataFrame(teachers_data)

    # Create a DataFrame for students
    # Note: We include a 'teacher_name' column to link to teachers
    students_data = {
        "name": [
            "Alice",
            "Bob",
            "Charlie",
            "Diana",
            "Edward",
            "Fatima",
            "George",
            "Hannah",
        ],
        "grade": [95, 87, 91, 82, 88, 94, 79, 90],
        "teacher_name": [
            "Ms. Johnson",
            "Ms. Johnson",
            "Ms. Johnson",  # Math students
            "Mr. Smith",
            "Mr. Smith",  # History students
            "Dr. Garcia",
            "Dr. Garcia",
            "Dr. Garcia",  # Science students
        ],
    }
    students_df = pd.DataFrame(students_data)

    return teachers_df, students_df


def populate_from_dataframes(
    engine, teachers_df: pd.DataFrame, students_df: pd.DataFrame
) -> None:
    with Session(engine) as session:
        # Check if we already have data
        result = session.execute(select(Teacher)).first()
        if result is not None:
            print("ℹ️ Database already contains data")
            return

        # Step 1: Create a dictionary to map teacher names to teacher objects
        teacher_map = {}

        # Step 2: Insert teachers and build the mapping
        for _, row in teachers_df.iterrows():
            teacher = Teacher(name=row["name"], subject=row["subject"])
            session.add(teacher)
            # We need to flush to get the ID assigned by the database
            session.flush()
            # Store teacher object in our map for future reference
            teacher_map[teacher.name] = teacher

        # Step 3: Insert students, referrencing the appropriate teacher
        for _, row in students_df.iterrows():
            # Look up the teacher by name
            teacher_name = row["teacher_name"]
            teacher = teacher_map.get(teacher_name)

            if teacher is None:
                print(
                    f"❌ WARNING: Teacher '{teacher_name}' not found, \n"
                    f"    Skipping student '{row['name']}'"
                )
                continue

            # Create the student linked to the teacher
            student = Student(
                name=row["name"],
                grade=row["grade"],
                teacher=teacher,  # This sets the relationship and teacher_id
            )
            session.add(student)

        # Commit all changes
        session.commit()
        print("✅ Successfully imported teachers and students from DataFrames.")


def verify_import(engine) -> None:
    """Query the database to verify the import worked correctly."""

    with Session(engine) as session:
        # Count teachers and students
        teacher_count = session.query(Teacher).count()
        student_count = session.query(Student).count()

        print(
            "\nDatabase contains:\n"
            f"  - {teacher_count} teachers,\n"
            f"  - {student_count} students."
        )

        # Show each teacher and their students
        teachers = session.execute(select(Teacher)).scalars().all()

        for teacher in teachers:
            print(f"\nTeacher: {teacher.name} (Subject: {teacher.subject})")
            print("👇 Students:")
            for student in teacher.students:
                print(f"    - {student.name}: Grade {student.grade}")


# 🔁 Create database if not exists
def create_database_if_not_exists(engine) -> None:
    """Create the database if it doesn't exist."""
    # Extract database name from the connection string
    db_name = engine.url.database

    # Create a connection without specifying a database
    base_engine = create_engine(
        f"{engine.url.drivername}://{engine.url.username}:"
        f"{engine.url.password}@{engine.url.host}",
        echo=False,
    )

    # Create database if it doesn't exsit
    with base_engine.connect() as conn:
        conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {db_name}"))
        print(f"Ensured database '{db_name}' exists.")


def main():
    # Create sample DataFrame
    teachers_df, students_df = create_sample_dataframe()

    # Print sample data
    print("Sample Teacher Data:")
    print(teachers_df.head())
    print("\nSample Student Data:")
    print(students_df.head())

    # Create MySQL database engine
    engine = create_engine(
        f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@"
        f"{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}",
        # Logging capabilities
        echo=os.getenv("DB_ECHO", True) in ("true", "1", "t"),
        # Number of connections to keep open
        pool_size=int(os.getenv("DB_POOL_SIZE", 5)),
        # Number of additional connections to temporarily establish during high load periods
        max_overflow=int(os.getenv("DB_MAX_OVERFLOW", 10)),
        # Verify connections before use
        pool_pre_ping=True,
        # Recycle connections after one hour
        pool_recycle=int(os.getenv("DB_POOL_RECYCLE", 3_600)),
    )

    # Create database if it doesn't exist
    create_database_if_not_exists(engine)

    # Create all tables in the database
    Base.metadata.create_all(engine)

    # Populate database from DataFrames
    populate_from_dataframes(engine, teachers_df, students_df)

    # Verify the import
    verify_import(engine)


if __name__ == "__main__":
    main()
