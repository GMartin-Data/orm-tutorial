# I. ORM Relationships Tutorial

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

# II. Populating ORM Models with Pandas DataFrames

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

## Part 8: Populating Many-to-Many Relationships from DataFrames With SQLModel

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

# III. Migrating from SQLite to MySQL

This guide covers the essential steps to migrate your ORM project from SQLite to MySQL/MariaDB.

## 1. Database Connection Setup

Replace the SQLite engine with a MySQL-compatible one:

```python
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Create MySQL engine
engine = create_engine(
    f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}",
    echo=True,                                    # Log all SQL
    pool_size=5,                                  # Maintain 5 connections
    max_overflow=10,                              # Allow 10 extra temp connections
    pool_pre_ping=True,                           # Verify connections before use
    pool_recycle=3600                             # Recycle connections after 1 hour
)
```

Key connection parameters:

- `pool_size`: Number of permanent connections to maintain
- `max_overflow`: Additional temporary connections allowed during high load
- `pool_pre_ping`: Tests if connections are alive before using them
- `pool_recycle`: Maximum age of connections in seconds (prevents "stale connection" errors)

## 2. Database Creation

SQLite automatically creates databases as files, but MySQL requires explicit creation:

```python
from sqlalchemy import text

def create_database_if_not_exists(engine):
    """Create the database if it doesn't exist."""
    db_name = engine.url.database

    # Create a connection without specifying a database
    base_engine = create_engine(
        f"{engine.url.drivername}://{engine.url.username}:{engine.url.password}@{engine.url.host}",
        echo=False
    )

    # Create database if it doesn't exist
    with base_engine.connect() as conn:
        conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {db_name}"))
        print(f"Ensured database '{db_name}' exists")
```

Call this function before creating tables: `create_database_if_not_exists(engine)`

## 3. User Authentication

MariaDB/MySQL on Linux systems typically uses `unix_socket` authentication for root. Create a dedicated database user:

```sql
# Connect to MariaDB as root
sudo mariadb

# Create a dedicated user
CREATE USER 'devuser'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON *.* TO 'devuser'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

Store these credentials in your `.env` file:

```
DB_USER=devuser
DB_PASSWORD=your_password
DB_HOST=localhost
DB_NAME=your_database
```

## 4. MySQL Dialect Requirements

MySQL has stricter type requirements than SQLite:

1. **String lengths**: MySQL requires explicit VARCHAR lengths

   ```python
   from sqlalchemy import String

   # SQLite (works but not in MySQL)
   name: Mapped[str] = mapped_column()

   # MySQL compatible
   name: Mapped[str] = mapped_column(String(100))
   ```

2. **Text columns**: For longer text, use Text type

   ```python
   from sqlalchemy import Text

   description: Mapped[str] = mapped_column(Text)
   ```

3. **Default values**: More restrictive in MySQL, especially with dates

   ```python
   # Use default_factory for dates rather than default
   from datetime import datetime

   created_at: Mapped[datetime] = mapped_column(default_factory=datetime.now)
   ```

## 5. Dependencies

Install required packages:

```bash
uv pip install pymysql python-dotenv
```

Add these to your `pyproject.toml`:

```toml
[project.optional-dependencies]
mysql = ["pymysql>=1.0.2", "python-dotenv>=1.0.0"]
```

# IV. ☁️ Cloud SQL

## Setting Up Cloud SQL on GCP for Your ORM Project

### 0. Table of Contents

1. **GCP Project Setup**

   - Creating/selecting a project
   - Enabling Cloud SQL API
   - Setting up billing

2. **Configuring Cloud SQL Instance**

   - Creating a MySQL instance
   - Basic configuration
   - Network setup

3. **Database Setup**

   - Creating database
   - User management

4. **Connecting to Cloud SQL**

   - From local environment
   - Cloud SQL Auth Proxy
   - Connection strings

5. **Security Configuration**

   - Access control
   - Private vs Public IP
   - Using IAM

6. **Application Integration**

   - Updating SQLAlchemy connection
   - Environment variables
   - Testing connectivity

7. **Monitoring and Maintenance**
   - Monitoring setup
   - Backups
   - Cost management

## 1. GCP Project Setup

### 1.1 Creating/Selecting a Project

- 🖥️ **Via GCP Console:**

  1. Log in to [Google Cloud Console](https://console.cloud.google.com/).
  2. Click the project dropdown at the top and select **"New Project"**.
  3. Enter a project name that reflects your application (e.g., `cloud-mysql-orm`).
  4. Click **"Create"** and wait for the project to initialize (~30 seconds).
  5. Select your new project from the dropdown menu at the top.

- ⌨️ **Via gcloud CLI:** (create, then set the current project)
  ```bash
  gcloud projects create your-project-id --name="cloud-mysql-orm"
  gcloud config set project your-project-id
  ```

### 1.2 Enabling Cloud SQL API

- 🖥️ **Via GCP Console:**

  1. Navigate to **"APIs & Services" > "Library"** in the left menu.
  2. Search for **"Cloud SQL Admin API"**.
  3. Click on the result and then click **"Enable"**.

- ⌨️ **Via gcloud CLI:**
  ```bash
  gcloud services enable sqladmin.googleapis.com
  ```

### 1.3 Setting Up Billing

- 🖥️ **Via GCP Console:**

  1. Navigate to **"Billing"** in the left menu..
  2. Link an existing billing account or create a new one.
  3. Note: Cloud SQL will incur charges (~$20-200/month depending on configuration).

- ⌨️ **Verification via gcloud CLI:**
  ```bash
  gcloud beta billing projects describe your-project-id
  ```

### 1.4 ✅ Verifying the Setup

- 1️⃣ **Project Verification:**

  - Confirm that your new project appears in the [Google Cloud Console Projects list](https://console.cloud.google.com/projectselector2/home/dashboard).
  - Alternatively, run:
    ```bash
    gcloud projects list
    ```
    to ensure your project is listed.

- 2️⃣ **Cloud SQL API Verification:**

  - In the Cloud Console, navigate to **"APIs & Services" > "Dashboard"** and check that the **Cloud SQL Admin API** is enabled.
  - Alternatively, run:
    ```bash
    gcloud services list --enabled | grep sqladmin
    ```
    to confirm that the Cloud SQL API is active.

- 3️⃣ **Billing Verification:**
  - Open the **"Billing"** section in the Cloud Console and verify that your project is linked to an active billing account.
  - You can also use the CLI:
    ```bash
    gcloud beta billing projects describe your-project-id
    ```
    to check that billing is properly configured.

## 2. Configuring Cloud SQL Instance

### 2.1 Network Configuration

Cloud SQL instances can use Public IP, Private IP, or both:

- **Public IP**: Accessible from anywhere with authorized networks
- **Private IP**: Accessible only within your VPC network (more secure)

For this tutorial, we'll set up Private IP using the default VPC:

1. Navigate to "VPC Network" > "VPC Networks"
2. Enable **Compute Engine API**
3. Scroll down to see the **VPC networks** list to confirm the `default` network exists
4. Click on it, and go, on the right, click on the **PRIVATE SERVICES ACCESS** tab
5. Click on the blue button **ENABLE API** to enable Service Networking API
6. Under **ALLOCATED IP RANGES FOR SERVICES** tab, click on the **ALLOCATED IP RANGE** button, and specify:

- Name: `google-managed-services-range`
- IP range (under _custom_): `10.0.0.0/24`
- Click on **ALLOCATE**

7. Under **PRIVATE CONNECTIONS TO SERVICES** tab, click on the **CREATE CONNECTION** button, and:

- Keep "Google Cloud Platform" for Connected service producer
- Check the box for "google-managed-services-range" and click on **OK**
- Click on **CONNECT**

### 2.2 Creating a MySQL Instance

Once you've confirmed that the default VPC is available, the next step is to create
a Cloud SQL instance running MySQL.

#### 🖥️ Using the GCP Console:

> **NOTE**: On the right panel, you will see an **updating estimated of the incurred costs**

1. Navigate to **"SQL"** in the left menu.
2. Click **"Create Instance" > "MySQL" > "Choose MySQL"**.
3. Choose **"Enterprise"** for the Cloud SQL Edition and **"Sandbox"** as Edition preset.
4. As **Instance info**, choose MySQL 8.0 (latest) as **Database version**
5. Below **SHOW MINOR VERSIONS**:

- choose `mysql-orm-1` (must be unique)
- choose and store a strong secure password

6. Below **Choose Region and Zonal Availability**:

- choose `europe-west1 (Belgium)` as a **Region**
- choose Single zone for **Zonal availibility** (useless to unroll **SPECIFY ZONES**, keep "Any")

7. Under **Customize Your Instance**:

- unroll **SHOW CONFIGURATION OPTIONS**
- unroll **Machine Configuration** and choose the "smallest"
- unroll **Storage** and choose HDD to spare some costs (keep the rest untouched)
- unroll **Connections** and:
  - check **Private IP** box
  - that's all! Everything else is already done with the `default` network
  - unckeck **Public IP** box (unless you want external access)
- Finally, click on the blue button **CREATE INSTANCE** (it will take some time)

#### ⌨️ Via GCP Console

```bash
gcloud sql instances create mysql-instance-1 \
  --database-version=MYSQL_8_0 \
  --cpu=1 \
  --memory=3840MB \
  --region=us-central1 \
  --root-password=YOUR_PASSWORD \
  --storage-type=SSD \
  --storage-size=10GB \
  --availability-type=zonal \
  --backup-start-time=04:00 \
  --enable-bin-log \
  --network=default \
  --no-assign-ip
```

#### ✅ Verifying the instance

- **GCP Console**: Ensure the new instance appears in the Cloud SQL instances list
  and its status is **"Runnable"** (on the round, green checkbox)
- **gcloud CLI**: Run
  ```bash
  gcloud sql instances describe mysql-instance-1
  ```
  to confirm the instance is active and properly configured
- **Connection Test**: Once running, test connectivity with:

  ```bash
  gcloud sql connect mysql-instance-1 --user=root
  ```

  > ☝️ **NOTE**
  >
  > You may experience issues with connecting, which can be solved the following way:
  > (Within Cloud Shell launched on the Web)
  >
  > 1. Add a public IP to your instance
  >
  > ```bash
  > gcloud sql instances patch mysql-instance-1 --assign-ip
  > ```
  >
  > 2. Authorise Cloud Shell IP
  >
  > ```bash
  > # Get your Cloud Shell IP
  > export CLOUD_SHELL_IP=$(curl -s ifconfig.me)
  > # Add it to authorized networks
  > gcloud sql instances patch mysql-instance-1 --authorized-networks=$CLOUD_SHELL_IP/32
  > ```
  >
  > 3. Try connecting again:
  >
  > ```bash
  > gcloud sql connect mysql-instance-1 --user=root
  > ```
  >
  > You'll be then prompted for the root password you earlier set

## 3. Database Setup

### 3.1. Creating a Database

Now that your Cloud SQL MySQL instance is running, let's create a database:

⌨️ **Using Cloud Shell:**

Assuming you're already connected, create a database, check creation, then use it.

```bash
CREATE DATABASE university_db;
SHOW DATABASES;
USE university_db;
```

### 3.2. User Management

It's best practise not to use the root user for application connections. Let's
create a dedicated user.

⌨️ **Using Cloud Shell:**

Assuming you're already connected...

1. Create a new user

```bash
CREATE USER 'app_user'@'%' IDENTIFIED BY 'strong-password-here';
```

2. Grant privileges to the user

```bash
GRANT ALL PRIVILEGES ON university_db.* TO 'app_user'@'%';
FLUSH PRIVILEGES;
```

3. Verify the user was created

```bash
SELECT User, Host
  FROM mysql.user
 WHERE User='app_user';
```

4. Exit and test the user can connect

```bash
EXIT;
gcloud sql connect mysql-instance-1 --user=app_user
```

5. Check if the user can access the database

```bash
USE university_db;
```

### 3.3 ✅ Verification Checklist

- Database exists and is accessible
- App user created with proper permissions
- Both `root` and `app_user` can connect to the instance

## 4. Connecting to Cloud SQL

### 4.1. Connection Options Overview

There are three main ways to connect to your Cloud SQL Instance:

1. **Direct connection** (using Public IP - excluded here)
2. **Cloud SQL Auth Proxy** (most secure option)
3. **Private IP** (within VPC)

For your SQLAlchemy/SQLModel application, we'll focus on the **Auth Proxy** method

### 4.2. Setting Up Cloud SQL Auth Proxy

The Auth Proxy provides secure access to your Cloud SQL instance without requiring
a public IP.

#### Local Development environment

1. Download the Cloud SQL Auth Proxy

```bash
wget https://storage.googleapis.com/cloud-sql-connectors/cloud-sql-proxy/v2.8.1/cloud-sql-proxy.linux.amd64 -O cloud_sql_proxy
chmod +x cloud_sql_proxy
```

2. Create a service account for the proxy:

```bash
# Switch to your project if needed
gcloud config set project your-project-id

# Create service account
gcloud iam service-accounts create cloud-sql-proxy \
  --description="Cloud SQL Auth Proxy service account" \
  --display-name="Cloud SQL Auth Proxy"

# Grant necessary permissions
gcloud projects add-iam-policy-binding your-project-id \
  --member="serviceAccount:cloud-sql-proxy@your-project-id.iam.gserviceaccount.com" \
  --role="roles/cloudsql.client"

# Create and download key file
gcloud iam service-accounts keys create cloud-sql-proxy-key.json \
  --iam-account=cloud-sql-proxy@your-project-id.iam.gserviceaccount.com
```

These commands create and configure a service account specifically for Cloud SQL Auth Proxy:

a. **Set project context**:

    - Ensures all commands target your specific project

b. **Create service account**:

    - Creates a dedicated technical identity for the proxy
    - Better security than using your personal account
    - Names and describes it for easy identification

c. **Grant permissions**:

    - Gives the service account "Cloud SQL Client" role
    - Allows connecting to Cloud SQL instances but nothing else
    - Applies least-privilege security principle

d. **Create key file**:

    - Generates credentials (JSON key file) for the proxy to authenticate
    - Acts like a password for the service account
    - ☝️ **IMPORTANT**:
      - The service account key (`cloud-sql-proxy-key.json`) is downloaded to your current directory when you run the `gcloud iam service-accounts keys create` command.
      - It doesn't get stored in the console.
      - Keep this file secure; anyone with it can access your databases

These steps establish a secure, isolated identity specifically for database connectivity.

> You can manage existing keys in the GCP Console:
>
> 1. Navigate to "IAM & Admin" > "Service Accounts"
> 2. Find your service account (`cloud-sql-proxy`)
> 3. Click on it > "Keys" tab
> 4. Here you can view, disable, or delete existing keys
>
> **Best practices:**
>
> - Store keys securely (e.g., in secret management systems)
> - Rotate keys periodically
> - Delete keys when no longer needed
> - Never commit keys to version control
>
> If you lose the key file, you'll need to create a new one and delete the old one.

3. Get your instance connection name

```bash
gcloud sql instances describe mysql-instance-1 --format="value(connectionName)"
```

This will output something like: `your-project-id:your-region:mysql-instance-1`

4. Start the proxy:

```bash
# Linux/macOS
export GOOGLE_APPLICATION_CREDENTIALS=./cloud-sql-proxy-key.json
./cloud_sql_proxy YOUR_CONNECTION_NAME --port 13306
```

(13306 was tested as an alternative port, though 3306 is the standard port for MariaDB)

Keep this terminal open while you need the connection

### 4.3. Testing the Connection

1. Open a new terminal window (keep the proxy running)
2. Connect to the database using a standard MySQL client

```bash
mysql -u app_user -p -h 127.0.0.1 -P 13306
```

(You don't have to specify the port if this is the standard one for MariaDB.
As we had to change it previously, it's then necessary to specify it.)

3. Verify you can access the database

```sql
USE university_db;
SHOW TABLES;
```
