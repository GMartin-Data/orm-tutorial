from typing import List, Optional

from sqlalchemy import ForeignKey, select
from sqlalchemy.engine import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import (
    DeclarativeBase, 
    Mapped, 
    Session, 
    mapped_column, 
    relationship
)


class Base(DeclarativeBase):
    pass


# Define our teacher model
class Teacher(Base):
    __tablename__ = "teachers"
    
    # Fields
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    subject: Mapped[str] = mapped_column()
    
    # Relationship: one teacher has many students
    students: Mapped[List["Student"]] = relationship(
        back_populates="teacher",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"Teacher(id={self.id}, name={self.name}, subject={self.subject})"
    

# Define our Student model
class Student(Base):
    __tablename__ = "students"
    
    # Fields
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    grade: Mapped[int] = mapped_column()
    
    # Foreign Key
    teacher_id: Mapped[int] = mapped_column(ForeignKey("teachers.id"))
    
    # Relationship
    teacher: Mapped["Teacher"] = relationship(back_populates="students")
    
    def __repr__(self) -> str:
        return f"Student(id={self.id}, name={self.name}, grade={self.grade})"


def main():
    # Create SQLite database engine
    engine = create_engine("sqlite:///school.db", echo=True)
    
    # Create all tables in the database
    Base.metadata.create_all(engine)
    
    # Create a session to interact with the database
    with Session(engine) as session:
        # Check if we already have data
        result = session.execute(select(Teacher)).first()
        if result is None:
            # Create a teacher
            math_teacher = Teacher(name="Ms. Johnson", subject="Mathematics")
            
            # Create students associated with this teacher
            alice = Student(name="Alice", grade=95, teacher=math_teacher)
            bob = Student(name="Bob", grade=87, teacher=math_teacher)
            charlie = Student(name="Charlie", grade=91, teacher=math_teacher)
            
            # Add the teacher to the session (students will be added automatically via cascade)
            session.add(math_teacher)
            
            # Commit the changes
            session.commit()
            
        # Query and demonstrate the relationship
        
        # 1️⃣ Get all teachers
        print("\n1️⃣ === All Teachers ===")
        teachers = session.execute(select(Teacher)).scalars().all()
        for teacher in teachers:
            print(teacher)
            
        # 2️⃣ Get a specific teacher
        print("\n2️⃣ === Ms. Johnson and her students ===")
        math_teacher = session.execute(
            select(Teacher).where(Teacher.name == "Ms. Johnson")
        ).scalar_one()
        print(f"Teacher: {math_teacher.name}, Subject: {math_teacher.subject}")
        
        # 3️⃣ Access the students through the relationship
        print("3️⃣ Students:")
        for student in math_teacher.students:
            print(f"    - {student.name}: Grade {student.grade}")
            
        # 4️⃣ We can also start from students and find their teacher
        print("\n4️⃣ === Alice and her teacher ===")
        alice = session.execute(
            select(Student).where(Student.name == "Alice")
        ).scalar_one()
        print(f"Student: {alice.name}, Grade: {alice.grade}")
        print(f"Teacher: {alice.teacher.name}, Subject: {alice.teacher.subject}")


if __name__ == "__main__":
    main()
                 