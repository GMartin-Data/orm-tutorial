# ORM Relationships Tutorial

## Part 1: One-to-Many Relationship with SQLAlchemy 2.0

Let's first understand what a one-to-many relationship means in database terms.

In a one-to-many relationship, one record in a table can be associated with multiple record in another table.

### Example

A teacher can have many students, but each student has only one teacher.

### 🐍 Implementation With SQLAlchemy 2.0

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

▶️ You can run this script with:

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

### 🐍 Implementation with SQLModel

👉 `sqlmodel_examples/one_to_many.py`

▶️ You can run this script with:

```bash
python -m sqlmodel_examples/one_to_many
```

## Part 3: Many-to-Many Relationships with SQLAlchemy 2.0

Now, let's implement a many-to-many relationship with SQLAlchemy 2.0.

In this relationship type, records in both tables can be associated with
multiple records in the other table.

### Example

- Students can enroll in multiple courses
- Each course may have multiple students

### 🐍 Implementation

👉 `sqlalchemy_examples/many_to_many.py`

Let's examine how we've implemented the many-to-many relationship in SQLAlchemy 2.0

#### 1. Association Class

- Instead of using a plain association table, we've created a full `StudentCourseLink` class.
- This approach **allows us to add additional attributes to the relationship, like
  `enrollment_date`**

#### 2. Relationship Definition

- Each model has a relationship to the association class, not directly to the
  other model
- Both `Student` and `Course` have **properties** that provide convenient acces to the
  related objects.

#### 3. Primary Keys

The association class uses a composite primary key made up of both foreign keys.

#### 4. Cascading

We use `cascade="all, delete-orphan"` to **ensure that related records are properly
deleted when a parent record is deleted**.

#### 5. Access Patterns

- We can navaigate the relationship from either direction:
  - `student.courses` gives us all courses from a student
  - `course.students` gives us all students in a course
- We can also access the full link object to get additional data (like enrollment date)

▶️ You can run this script with:

```bash
python -m sqlalchemy_examples/many_to_many.py
```

## Part 4: Many-to-Many Relationship With SQLModel

Now, let's implement the same many-to-many relationship using SQLModel

### 🐍 Implementation

👉 `sqlmodel_examples/many_to_many.py`

Let's examine how SQLModel handles many-to-many relationships:

#### 1. Class Definitions

- We still define three classes: `Student`, `Course`, and the association class
  `StudentCourseLink`
- All inherit from `SQLModel`, with `table=True`

#### 2. Fields and Types

- We use `Field()` to define columns with attributes with `foreign_key` and
  `primary_key`
- For default values, we use `default_factory=datetime.now` instead of
  `default=datetime.now`

#### 3. Relationship Definition

- We use `Relationship()` instead of `relationship()`
- We still need the helper properties to directly access related objects

#### 4. Session Management

- We use `session.exec()` instead of `session.execute()`
- We use `session.refresh()` to ensure relationships are properly loaded

#### 5. Type Hints

- SQLModel integrates better with static type checking
- We don't need to use Python's `Mapped[]` type, as SQLModel handles this internally

▶️ You can run this script with:

```bash
python -m sqlmodel_examples.many_to_many
```

# Populating ORM Models with Pandas DataFrames

## Part 5: Populating One-to-Many Relationships From DataFrames With SQLAlchemy 2.0

### Understanding One-to-Many Population With SQLAlchemy

Let's break down what's happening in this example for populating a one-to-many
relationship from pandas DataFrames:

#### 1. Creating Sample Data

We first create two DataFrames:

- `teachers_df`: Contains teacher names and their subjects
- `students_df`: Contains students names, grades, and, more importantly, a
  `teacher_name` column that we'll use to link students to teachers

#### 2. Key Challenges

The main challenge is maintaining relationships.

Our DataFrames have names (like 'Ms. Johnson'), but our database needs foreign
keys (numeric IDs)

#### 3. The Solution

- We create and persist teachers first
- We build a mapping dictionary (`teacher_map`) to link teacher names to teacher
  objects.
- We flush the session to ensure teachers get their IDs from the database
- When creating students, we look up the appropriate teacher using this mapping

#### 4. Important Technique: Using `session.flush()`

- `flush()` synchronizes the session with the database without committing
- This ensures teachers get their auto-generated primary keys before we use them
  as foreign keys

#### 5. Error Handling

We include a check for missing teachers when processing students, which is
important for data quality

#### 6. Verification

After importing, we query the database to verify that the relationships were
correctly established

### 🐍 Implementation

▶️ You can run this script with

```bash
python -m sqlalchemy_examples.one_to_many_pandas
```

## Part 6: Populating One-to-Many Relationships from DataFrames With SQLModel

### SQLModel VS SQLAlchemy for DataFrame Import

The SQLModel implementation follows a similar approach to the SQLAlchemy one,
with some differences in syntax:

#### 1. Model Definition

- SQLModel combines the attributesof SQLAlchemy's models with Pydantic validation
- We use `Optional[int]` for IDs and foreign keys with `default=None`

#### 2. Session Operations

- We use `session.exec()` instead of `session.execute()`
- We use `len(session.exec(...).all())` instead of `session.query(...).count()`

#### 3. Relationship Management

- The process for maintaining relationships is identical:
  - insert teachers first
  - create a mapping between names and objects
  - link students to teachers using this mapping
- Both frameworks handle the bidirectional relationship correctly

SQLModel provides a cleaner API but the fundamental technique for importing data
from DataFrames remains the same.

### 🐍 Implementation

▶️ You can run this script with

```bash
python -m sqlmodel_examples.one_to_many_pandas
```

## Part 7: Populating Many-to-Many Relationships from DataFrames With SQLAlchemy 2.0

### Understanding Many-to-Many Population With SQLAlchemy

The key challenge with many-to-many relationships is that we need three DataFrames
instead of 2.

#### 1. A DataFrame for Each Main Entry

- `students_df`: Contains student information (name, email)
- `courses_df`: Contains course information (title, description)

#### 2. A DataFrame for the Relationship Itself

- `enrollments_df`: Contains records linking students to courses
- Each row represents a student enrolled in a course
- Includes the enrollment date to demonstrate handling addtional attributes on
  the relationship

#### 3. Natural Keys VS Database IDs

The DataFrames use natural keys (emails for students, title for courses), but
the database use numeric IDs. We manage this difference trhough:

- Creating mappings after inserting records
- Using `session.flush()` to get database-assigned IDs
- Looking up entities by their natural keys when creating relationship records

#### 4. Date Handling

- The enrollment date comes from the DataFrame as a string
- We parse it into a Python `datetime` object before storing

#### 5. Error Handling

- We check that both the student and course exist before creating a link
- That prevents orphaned relationships records

### 🐍 Implementation

▶️ You can run this script with

```bash
python -m sqlalchemy_examples.many_to_many_pandas
```

## Populating Many-to-Many Relationships from DataFrames With SQLModel

### Key Techniques For Importing DataFrames Into ORMs

Through these examples, we've covered several important techniques for working
with Pandas DataFrames and ORMs:

#### 1. Handling Natural Keys VS Database IDs

In DataFrames, we often reference entities by natural keys (names, emails, etc.)
, while databases use surrogate keys (IDs). To bridge this gap:

- Create in-memory mappings from natural keys to ORM objects
- Use `session.flush()` to get database-assigned IDs before creating relationships
- Look up objects using the mapping when creating relationships

#### 2. Managing Relationships

Both one-to-many and many-to-many relationships require careful handling:

- **One-to-Many**: Each child record (student) references a single parent (teacher)
- **Many-to-Many**: A separate "join" table (and DataFrame) links entities together

#### 3. Data Type Conversion

Converting between DataFrame and database types requires attention:

- Parse date strings into Python `datetime` objects
- Handle nullable fields appropriately
- Ensure consistent formatting of natural keys (e.g. case sensitivity)

#### 4. Transaction Management

Using a single transaction for the entire import ensures data consistency

- All data is committed at once, preventing partial imports
- If an error occurs, the entire transaction can be rolled back

#### 5. Validation and Error Handling

Before creating relationships, we validate that both entities exist:

- Check that referenced objects are present in the mappings
- Skip or report records that reference missing entities
- This prevents orphaned relationships or constraint violations

### 🐍 Implementation

▶️ You can run this script with

```bash
python -m sqlmodel_examples.many_to_many_pandas
```
