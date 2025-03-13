"""
Local development with Auth Proxy
"""

import os
from typing import List

from dotenv import load_dotenv
from sqlalchemy import ForeignKey, String, create_engine, text
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship

load_dotenv()


class Base(DeclarativeBase):
    pass


class Teacher(Base):
    __tablename__ = "teachers"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))  # Explicit length for MySQL
    subject: Mapped[str] = mapped_column(String(100))

    students: Mapped[List["Student"]] = relationship(
        back_populates="teacher", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"Teacher(id={self.id}, name={self.name}, subject={self.subject})"


class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    grade: Mapped[int] = mapped_column()

    teacher_id: Mapped[int] = mapped_column(ForeignKey("teachers.id"))
    teacher: Mapped["Teacher"] = relationship(back_populates="students")

    def __repr__(self) -> str:
        return f"Student(id={self.id}, name={self.name}, grade={self.grade})"


# Switch between the versions according to the environment
# Think about commenting/uncommenting what's relevant in the .env file
def get_engine():
    """Get SQLAlchemy engine configured for Cloud SQL via Auth Proxy."""
    engine = create_engine(
        f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@"
        f"127.0.0.1:{os.getenv('DB_PORT', '13306')}/{os.getenv('DB_NAME')}",
        echo=True,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,
        pool_recycle=3600,
    )
    return engine


# def get_engine():
#     """Get SQLAlchemy engine for direct connection within GCP."""
#     engine = create_engine(
#         f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@"
#         f"{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}?ssl_ca={os.getenv('SSL_CA_PATH')}",
#         echo=True,
#         pool_size=5,
#         max_overflow=10,
#         pool_pre_ping=True,
#         pool_recycle=3600,
#     )
#     return engine


def main():
    engine = get_engine()
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        result = session.execute(text("SHOW TABLES;")).fetchall()
        print("👇 Available tables:")
        for row in result:
            print(f"    - {row[0]}")


if __name__ == "__main__":
    main()
