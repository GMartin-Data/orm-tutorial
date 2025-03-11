from typing import List, Optional

from sqlmodel import Field, Relationship, Session, SQLModel, create_engine, select


# Define our Teacher model
class Teacher(SQLModel, table=True):
    __tablename__ = "teachers"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    subject: str

    # Relationship: one teacher has many students
    # In SQLModel, we don't need to specify cascade, it's automatically handled
    students: List["Student"] = Relationship(back_populates="teacher")

    def __repr__(self) -> str:
        return f"Teacher(id={self.id}), name={self.name}, subject={self.subject})"


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


def main():
    # Create SQLite database engine
    engine = create_engine("sqlite:///school_sqlmodel.db", echo=True)

    # Create all tables in the database
    SQLModel.metadata.create_all(engine)

    # Create a session to interact with the database
    with Session(engine) as session:
        # Check if we already have data
        result = session.exec(select(Teacher)).first()
        if result is None:
            # Create a teacher
            math_teacher = Teacher(name="Ms. Johnson", subject="Mathematics")

            # Create students associated with this teacher
            alice = Student(name="Alice", grade=95, teacher=math_teacher)
            bob = Student(name="Bob", grade=87, teacher=math_teacher)
            charlie = Student(name="Charlie", grade=91, teacher=math_teacher)

            # Add the teacher to the session (students will be added automatically)
            session.add(math_teacher)

            # Commit the changes
            session.commit()

            # 👇 Refresh the teacher to ensure relationships are loaded
            session.refresh(math_teacher)

        # Query and demonstrate the relationship
        # 1️⃣ Get all teachers
        print("\n1️⃣ === All Teachers ===")
        teachers = session.exec(select(Teacher)).all()
        for teacher in teachers:
            print(teacher)

        # 2️⃣ Get a specific teacher
        print("\n2️⃣ === Ms. Johnson and her students ===")
        math_teacher = session.exec(
            select(Teacher).where(Teacher.name == "Ms. Johnson")
        ).one()
        print(f"Teacher: {math_teacher.name}, Subject: {math_teacher.subject}")

        # 3️⃣ Access the students through the relationship
        print("3️⃣ Students:")
        for student in math_teacher.students:
            print(f"    - {student.name}: Grade {student.grade}")

        # 4️⃣ We can also start from students and find their teacher
        print("\n4️⃣ === Alice and her teacher ===")
        alice = session.exec(select(Student).where(Student.name == "Alice")).one()
        print(f"Student: {alice.name}, Grade: {alice.grade}")
        print(f"Teacher: {alice.teacher.name}, Subject: {alice.teacher.subject}")


if __name__ == "__main__":
    main()
