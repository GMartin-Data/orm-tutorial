# ORM Relationships Tutorial

## Part 1: One-to-Many Relationship with SQLAlchemy 2.0

Let's first understand what a one-to-many relationship means in database terms.

In a one-to-many relationship, one record in a table can be associated with multiple record in another table.

### Example

A teacher can have many students, but each student has only one teacher.

### Implementation With SQLAlchemy 2.0

👉 `sqlalchemy_examples/one_to_many.py`

Let''s break down what's happening in this example:

#### 1. **Base Class**: We create a base class that inherits from SQLAlchemy 2.0's

`DeclarativeBase` rather than the older `declarative_base()` function.

#### 2. **Model Definitions**:

- `Teacher` has basic attributes like `id`, `name`, and `subject`.
- `Student` has attributes plus a `teacher_id` foreign key.

#### 3. **Relationship Definition**:

- In the `Teacher` class, we **define a one-to-many relationship** using the `relationship()` function.
- We specify `back_populates="teacher"` to **create a bidirectional relationship**.
- The `cascade="all, delete-orphan"` option means that **operations on the teacher will cascade to the associated students**.

#### 4. **Type Hints with `Mapped[]`**:

- SQLAlchemy 2.0 uses the `Mapped[]` type to **provide better type hints**.
- `Mapped[List["Student"]]` indicates a collection of `Student` objects.
- The quotes around "Student" handle forward references.

#### 5. **Demonstration**:

- We create a teacher and associated students.
- We query for a teacher and access their students through the relationship.
- We also demonstrate accessing a student's teacher through the relationship.

You can run this script with:

```bash
python -m sqlalchemy_examples.one_to_many
```

## Part 2: One-to-Many Relationships With SQLModel

### Foreword

Now, let's implement the same relationships using SQLModel.

SQLModel is built on top of SQLAlchemy and Pydantic, providing a more streamlined
API with better type checking.

Let's examine how SQLModel handles one-to-many relationships differently from
pure SQLAlchemy.

#### 1. Class Definition

- SQLModel classes inherit from `SQLModel` with `table=True` to indicate they are
  database tables
- We don't need separate `Base` class

#### 2. Fields and Types

- We use `Field` from SQLModel to define columns and attributes
- `Optional[int]` is used for the ID to indicate it can be `None` **before being
  assigned to the database**.

#### 3. Relationship Definition

- We use `Relationship()` from SQLModel instead of SQLAlchemy's `relationship()`
- The API is cleaned and more intuitive

#### 4. Querying

- We use `session.exex()` instead of `session.execute()`
- We use `.one()` instead of `.scalar_one()` for single results

#### 5. Session Management

- We call `session_refresh(math_teacher)` to ensure relationships are loaded
  properly

### Implementation with SQLModel

👉 `sqlmodel_examples/one_to_many.py`

You can run this script with:

```bash
python -m sqlmodel_examples/one_to_many
```
