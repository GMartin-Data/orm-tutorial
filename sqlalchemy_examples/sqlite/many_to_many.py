from datetime import datetime
from typing import List, Optional

from sqlalchemy import ForeignKey, select
from sqlalchemy.engine import create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship


# Base class for our models
class Base(DeclarativeBase):
    pass


# Association table for the many-to-many relationship
class StudentCourseLink(Base):
    __tablename__ = "student_course_links"

    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), primary_key=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"), primary_key=True)
    enrollment_date: Mapped[datetime] = mapped_column(default=datetime.now)

    # Relationships to both sides
    student: Mapped["Student"] = relationship(back_populates="course_links")
    course: Mapped["Course"] = relationship(back_populates="student_links")

    def __repr__(self) -> str:
        return f"StudentCourseLink(student_id={self.student_id}, course_id={self.course_id})"


# Student model
class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    email: Mapped[str] = mapped_column(unique=True)

    # Relationship to the association table
    course_links: Mapped[List[StudentCourseLink]] = relationship(
        back_populates="student",  # ⚠️ Corresponding relationship name
        cascade="all, delete-orphan",
    )

    # Convenience property to access courses directly
    @property
    def courses(self) -> List["Course"]:
        return [link.course for link in self.course_links]

    def __repr__(self) -> str:
        return f"Student(id={self.id}, name={self.name}, email={self.email})"


# Course model
class Course(Base):
    __tablename__ = "courses"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column()
    description: Mapped[Optional[str]] = mapped_column(nullable=True)

    # Relationship to association table
    student_links: Mapped[List[StudentCourseLink]] = relationship(
        back_populates="course", cascade="all, delete-orphan"
    )

    # Convenience property to access students directly
    @property
    def students(self) -> List["Student"]:
        return [link.student for link in self.student_links]

    def __repr__(self) -> str:
        return f"Course(id={self.id}, title={self.title})"


def main():
    # Create SQLite database engine
    engine = create_engine("sqlite:///university.db", echo=True)

    # Create all tables in the database
    Base.metadata.create_all(engine)

    # Create a session to interact with the database
    with Session(engine) as session:
        # Check if we already have data
        result = session.execute(select(Course)).first()
        if result is None:
            # Create courses
            python_course = Course(
                title="Python Programming",
                description="Learn Python from basics to advanced concepts.",
            )

            data_science_course = Course(
                title="Data Science Fundamentals",
                description="Introduction to data analysis and visualization.",
            )

            ml_course = Course(
                title="Machine Learning",
                description="Algorithms and techniques for predictive modeling.",
            )

            # Create students
            alice = Student(name="Alice Smith", email="alice@example.com")
            bob = Student(name="Bob Johnson", email="bob@example.com")
            charlie = Student(name="Charlie Brown", email="charlie@example.com")

            # Create enrollments (many-to-many links)
            # Alice takes Python and Data Science
            alice_python = StudentCourseLink(student=alice, course=python_course)
            alice_ds = StudentCourseLink(student=alice, course=data_science_course)

            # Bob takes all three courses
            bob_python = StudentCourseLink(student=bob, course=python_course)
            bob_ds = StudentCourseLink(student=bob, course=data_science_course)
            bob_ml = StudentCourseLink(student=bob, course=ml_course)

            # Charlie takes Machine Learning only
            charlie_ml = StudentCourseLink(student=charlie, course=ml_course)

            # Add everything to the session
            session.add_all(
                [
                    python_course,
                    data_science_course,
                    ml_course,
                    alice,
                    bob,
                    charlie,
                    alice_python,
                    alice_ds,
                    bob_python,
                    bob_ds,
                    bob_ml,
                    charlie_ml,
                ]
            )

            # Commit the changes
            session.commit()

        # Query and demonstrate the relationship

        # 1️⃣ Get all courses
        print("\n1️⃣=== All Courses ===")
        courses = session.execute(select(Course)).scalars().all()
        for course in courses:
            print(course)

        # 2️⃣ Get a specific course and its students
        print("\n2️⃣=== Python Course and its students ===")
        python_course = session.execute(
            select(Course).where(Course.title == "Python Programming")
        ).scalar_one()
        print(f"Course: {python_course.title}")
        print(f"Description: {python_course.description}")
        print("👇 Students enrolled:")
        for student in python_course.students:
            print(f"    - {student.name} ({student.email})")

        # 3️⃣ Get a specific student and their courses
        print("\n3️⃣=== Bob and his courses ===")
        bob = session.execute(
            select(Student).where(Student.name == "Bob Johnson")
        ).scalar_one()
        print(f"Student: {bob.name} ({bob.email})")
        print("👇 Courses enrolled:")
        for course in bob.courses:
            print(f"    - {course.title}")

        # 4️⃣ We can also access the enrollment date through the association object
        print("\n4️⃣=== Enrollment details ===")
        for link in bob.course_links:
            print(f"Bob enrolled in {link.course.title} on {link.enrollment_date}")


if __name__ == "__main__":
    main()
