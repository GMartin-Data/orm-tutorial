from datetime import datetime
from typing import List, Optional, Tuple

import pandas as pd
from sqlmodel import Field, Relationship, Session, SQLModel, create_engine, select


# Association table for the many-to-many relationships
class StudentCourseLink(SQLModel, table=True):
    __tablename__ = "student_course_links"

    student_id: int = Field(foreign_key="students.id", primary_key=True)
    course_id: int = Field(foreign_key="courses.id", primary_key=True)
    enrollment_date: datetime = Field(default=datetime.now)

    # Relationships to both sides
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

    # Relationship to the association table
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

    # Relationship to the association table
    student_links: List[StudentCourseLink] = Relationship(back_populates="course")

    # Convenience property to access students directly
    @property
    def students(self) -> List[Student]:
        return [link.student for link in self.student_links]

    def __repr__(self) -> str:
        return f"Course(id={self.id}, title={self.title})"


def create_sample_dataframes() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Create sample pandas DataFrames for students, courses, and enrollments."""

    # Create a DataFrame for students
    students_data = {
        "name": [
            "Alice Smith",
            "Bob Johnson",
            "Charlie Brown",
            "Diana Prince",
            "Edward Stark",
        ],
        "email": [
            "alice@example.com",
            "bob@example.com",
            "charlie@example.com",
            "diana@example.com",
            "edward@example.com",
        ],
    }
    students_df = pd.DataFrame(students_data)

    # Create a DataFrame for courses
    courses_data = {
        "title": [
            "Python Programming",
            "Data Science Fundamentals",
            "Machine Learning",
            "Database Design",
            "Web Development",
        ],
        "description": [
            "Learn Python from basics to advanced concepts.",
            "Introduction to data analysis and visualization.",
            "Algorithms and techniques for predictive modeling.",
            "Relational database theory and SQL.",
            "HTML, CSS, and JavaScript fundamentals.",
        ],
    }
    courses_df = pd.DataFrame(courses_data)

    # Create a DataFrame for enrollments (the many-to-many relationship)
    # Each row represents a student enrolled in a course
    enrollments_data = {
        "student_email": [
            "alice@example.com",
            "alice@example.com",  # Alice takes 2 courses
            "bob@example.com",
            "bob@example.com",
            "bob@example.com",  # Bob takes 3 courses
            "charlie@example.com",
            "charlie@example.com",  # Charlie takes 2 courses
            "diana@example.com",
            "diana@example.com",  # Diana takes 2 courses
            "edward@example.com",  # Edward takes 1 course
        ],
        "course_title": [
            "Python Programming",
            "Data Science Fundamentals",  # Alice's courses
            "Python Programming",
            "Data Science Fundamentals",
            "Machine Learning",  # Bob's courses
            "Machine Learning",
            "Database Design",  # Charlie's courses
            "Database Design",
            "Web Development",  # Diana's courses
            "Web Development",  # Edward's courses
        ],
        "enrollment_date": [
            "2025-01-15",
            "2025-01-15",  # Alice enrolled on Jan 15
            "2025-01-20",
            "2025-01-20",
            "2025-02-01",  # Bob's enrollment dates
            "2025-01-25",
            "2025-02-10",  # Charlie's enrollment dates
            "2025-02-05",
            "2025-02-05",  # Diana enrolled on Feb 5
            "2025-02-15",  # Edward enrolled on Feb 15
        ],
    }
    enrollments_df = pd.DataFrame(enrollments_data)

    return students_df, courses_df, enrollments_df


def populate_from_dataframes(
    engine,
    students_df: pd.DataFrame,
    courses_df: pd.DataFrame,
    enrollments_df: pd.DataFrame,
) -> None:
    """Populate the database from pandas DataFrames."""

    with Session(engine) as session:
        # Check if we already have data
        result = session.exec(select(Course)).first()
        if result:
            print("☝️ Database already contains data. Skipping import")
            return

        # Step 1: Create mappings to track objects by their natural keys
        student_map = {}
        course_map = {}

        # Step 2: Insert students and build the student mapping
        for _, row in students_df.iterrows():
            student = Student(name=row["name"], email=row["email"])
            session.add(student)
            session.flush()  # Get the database assigned id
            student_map[student.email] = student

        # Step 3: Insert courses and build the course mapping
        for _, row in courses_df.iterrows():
            course = Course(title=row["title"], description=row["description"])
            session.add(course)
            session.flush()
            course_map[course.title] = course

        # Step 4: Create the enrollments (many-to-many links)
        for _, row in enrollments_df.iterrows():
            student_email = row["student_email"]
            course_title = row["course_title"]
            enrollment_date = datetime.strptime(row["enrollment_date"], "%Y-%m-%d")

            # Look up the student and course by their natural keys
            student = student_map.get(student_email)
            course = course_map.get(course_title)

            # ⚠️ Skip if either is not found
            if student is None:
                print(f"❌ Warning: Student with email '{student_email}' not found")
                continue
            if course is None:
                print(f"❌ Warning: Course with title '{course_title}' not found")
                continue

            # Create the link
            link = StudentCourseLink(
                student=student, course=course, enrollment_date=enrollment_date
            )
            session.add(link)

        # Commit all changes
        session.commit()
        print(
            "✅ Successfully imported students, courses and enrollments from DataFrames"
        )


def verify_import(engine) -> None:
    """Query the database to verify the import worked correctly."""

    with Session(engine) as session:
        # 1️⃣ Count records in each table
        student_count = len(session.exec(select(Student)).all())
        course_count = len(session.exec(select(Course)).all())
        enrollment_count = len(session.exec(select(StudentCourseLink)).all())

        print("\n1️⃣ Database contains:")
        print(f"- {student_count} students")
        print(f"- {course_count} courses")
        print(f"- {enrollment_count} enrollments")

        # 2️⃣ Show courses for each student
        print("\n2️⃣=== Students and Their Courses ===")
        students = session.exec(select(Student)).all()

        for student in students:
            print(f"\nStudent: {student.name} ({student.email})")
            print("\n👇 Courses enrolled")
            for link in student.course_links:
                print(
                    f"    - {link.course.title} "
                    f"(enrolled on {link.enrollment_date.strftime('%Y-%m-%d')})"
                )

        # 3️⃣ Show students for each course
        print("\n3️⃣=== Courses and Enrolled Students ===")
        courses = session.exec(select(Course)).all()

        for course in courses:
            print(f"\nCourse: {course.title}")
            print("👇 Students enrolled:")
            for link in course.student_links:
                print(
                    f"  - {link.student.name} "
                    f"(enrolled on {link.enrollment_date.strftime('%Y-%m-%d')})"
                )


def main() -> None:
    # Create sample DataFrames
    students_df, courses_df, enrollments_df = create_sample_dataframes()

    # Print sample data
    print("Sample Student Data:")
    print(students_df.head())

    print("\nSample Course Data:")
    print(courses_df.head())

    print("\nSample Enrollment Data:")
    print(enrollments_df.head())

    # Create SQLite database engine
    engine = create_engine("sqlite:///university_from_pandas_sqlmodel.db", echo=True)

    # Create all tables in the database
    SQLModel.metadata.create_all(engine)

    # Populate database from DataFrames
    populate_from_dataframes(engine, students_df, courses_df, enrollments_df)

    # Verify the import
    verify_import(engine)


if __name__ == "__main__":
    main()
