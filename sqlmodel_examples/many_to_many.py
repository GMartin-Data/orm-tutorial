from datetime import datetime
from typing import List, Optional

from sqlmodel import Field, Relationship, Session, SQLModel, create_engine, select


# Association model for the many-to-many relationship
class StudentCourseLink(SQLModel, table=True):
    __tablename__ = "student_course_links"

    student_id: int = Field(foreign_key="students.id", primary_key=True)
    course_id: int = Field(foreign_key="courses.id", primary_key=True)
    enrollment_date: datetime = Field(default_factory=datetime.now)

    # Define relationships
    student: "Student" = Relationship(back_populates="course_links")
    course: "Course" = Relationship(back_populates="student_links")

    def __repr__(self) -> str:
        return f"StudentCourseLink(student_id={self.student_id}, course_id={self.course_id})"


# Student model
class Student(SQLModel, table=True):
    __tablename__ = "students"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: str = Field(unique=True)

    # Relationship to the link table
    course_links: List[StudentCourseLink] = Relationship(back_populates="student")

    # Convenience property to access courses directly
    @property
    def courses(self) -> List["Course"]:
        return [link.course for link in self.course_links]

    def __repr__(self) -> str:
        return f"Student(id={self.id}, name={self.name}, email={self.email})"


# Course model
class Course(SQLModel, table=True):
    __tablename__ = "courses"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: Optional[str] = None

    # Relationship to the link table
    student_links: List[StudentCourseLink] = Relationship(back_populates="course")

    # Convenience property to access students directly
    @property
    def students(self) -> List[Student]:
        return [link.student for link in self.student_links]

    def __repr__(self) -> str:
        return f"Course(id={self.id}, title={self.title})"


def main():
    # Create SQLite database engine
    engine = create_engine("sqlite:///university_sqlmodel.db", echo=True)

    # Create all tables in the database
    SQLModel.metadata.create_all(engine)

    # Create a session to interact with the database
    with Session(engine) as session:
        # Check if we already have data
        result = session.exec(select(Course)).first()
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

            # Refresh objects to ensure relationships are loaded
            session.refresh(python_course)
            session.refresh(bob)

        # Query and demonstrate the relationship

        # 1️⃣ Get all courses
        print("\n1️⃣=== All Courses ===")
        courses = session.exec(select(Course)).all()
        for course in courses:
            print(course)

        # 2️⃣ Get a specific course and its students
        print("\n2️⃣=== Python Course and its students ===")
        python_course = session.exec(
            select(Course).where(Course.title == "Python Programming")
        ).one()
        print(f"Course: {python_course.title}")
        print(f"Description: {python_course.description}")
        print("👇 Students enrolled:")
        for student in python_course.students:
            print(f"    - {student.name} ({student.email})")

        # 3️⃣ Get a specific student and their courses
        print("\n3️⃣=== Bob and his courses ===")
        bob = session.exec(select(Student).where(Student.name == "Bob Johnson")).one()
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
