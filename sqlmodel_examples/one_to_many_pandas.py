# sqlmodel_examples/one_to_many_pandas.py

import pandas as pd
from typing import List, Optional

from sqlmodel import Field, Relationship, Session, SQLModel, create_engine, select


# Define our Teacher model
class Teacher(SQLModel, table=True):
    __tablename__ = "teachers"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    subject: str

    # Relationship: one teacher has many students
    students: List["Student"] = Relationship(back_populates="teacher")

    def __repr__(self) -> str:
        return f"Teacher(id={self.id}, name={self.name}, subject={self.subject})"


# Define our Student model
class Student(SQLModel, table=True):
    __tablename__ = "students"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    grade: int

    # Foreign key
    teacher_id: Optional[int] = Field(default=None, foreign_key="teachers.id")

    # Relationship: many students have one teacher
    teacher: Optional[Teacher] = Relationship(back_populates="students")

    def __repr__(self) -> str:
        return f"Student(id={self.id}, name={self.name}, grade={self.grade})"


def create_sample_dataframes():
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


def populate_from_dataframes(engine, teachers_df, students_df):
    """Populate the database from pandas DataFrames."""

    with Session(engine) as session:
        # Check if we already have data
        result = session.exec(select(Teacher)).first()
        if result is not None:
            print("Database already contains data. Skipping import.")
            return

        # Step 1: Create a dictionary to map teacher names to teacher objects
        teacher_map = {}

        # Step 2: Insert teachers and build the mapping
        for _, row in teachers_df.iterrows():
            teacher = Teacher(name=row["name"], subject=row["subject"])
            session.add(teacher)
            # We need to flush to get the ID assigned by the database
            session.flush()
            # Store teacher object in our map for later reference
            teacher_map[teacher.name] = teacher

        # Step 3: Insert students, referencing the appropriate teacher
        for _, row in students_df.iterrows():
            # Look up the teacher by name
            teacher_name = row["teacher_name"]
            teacher = teacher_map.get(teacher_name)

            if teacher is None:
                print(
                    f"❌ Warning: Teacher '{teacher_name}' not found,\n"
                    f"skipping student '{row['name']}'"
                )
                continue

            # Create the student linked to the teacher
            student = Student(
                name=row["name"],
                grade=row["grade"],
                teacher=teacher,  # This sets both the relationship and teacher_id
            )
            session.add(student)

        # Commit all changes
        session.commit()
        print("Successfully imported teachers and students from DataFrames.")


def verify_import(engine):
    """Query the database to verify the import worked correctly."""

    with Session(engine) as session:
        # Count teachers and students
        teacher_count = len(session.exec(select(Teacher)).all())
        student_count = len(session.exec(select(Student)).all())

        print(
            f"\nDatabase contains {teacher_count} teachers and {student_count} students."
        )

        # Show each teacher and their students
        teachers = session.exec(select(Teacher)).all()

        for teacher in teachers:
            print(f"\nTeacher: {teacher.name} (Subject: {teacher.subject})")
            print("👇 Students:")
            for student in teacher.students:
                print(f"  - {student.name}: Grade {student.grade}")


def main():
    # Create sample DataFrames
    teachers_df, students_df = create_sample_dataframes()

    # Print sample data
    print("Sample Teacher Data:")
    print(teachers_df.head())
    print("\nSample Student Data:")
    print(students_df.head())

    # Create SQLite database engine
    engine = create_engine("sqlite:///school_sqlmodel_from_pandas.db", echo=True)

    # Create all tables in the database
    SQLModel.metadata.create_all(engine)

    # Populate database from DataFrames
    populate_from_dataframes(engine, teachers_df, students_df)

    # Verify the import
    verify_import(engine)


if __name__ == "__main__":
    main()
