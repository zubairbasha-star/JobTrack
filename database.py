import os
import mysql.connector
from mysql.connector import Error
import bcrypt
from dotenv import load_dotenv

load_dotenv()

# =====================================
# DATABASE CONNECTION
# =====================================

def get_connection():
    try:
        print("Connecting to MySQL...", flush=True)

        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME", "jobtrack"),
            port=int(os.getenv("DB_PORT", "3306")),
            connection_timeout=5,
            use_pure=True
        )

        print("MySQL connected successfully!", flush=True)
        return connection

    except Error as e:
        print("MySQL Connection Error:", e, flush=True)
        return None


# =====================================
# CREATE USERS TABLE
# =====================================

def create_users_table():
    connection = get_connection()
    print("DEBUG: Connection function finished", flush=True)

    if connection is None:
        raise Exception("Could not connect to MySQL database.")

    cursor = None

    try:
        cursor = connection.cursor()
        print("DEBUG: Cursor created", flush=True)

        query = """
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(100) NOT NULL UNIQUE,
                email VARCHAR(255) NOT NULL UNIQUE,
                password_hash VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """

        cursor.execute(query)
        connection.commit()

    except Error as e:
        connection.rollback()
        print("Error creating users table:", e)
        raise

    finally:
        if cursor is not None:
            cursor.close()
        connection.close()


# =====================================
# SIGNUP
# =====================================

def create_user(username, email, password):
    username = username.strip()
    email = email.strip().lower()

    if not username or not email or not password:
        return False, "All fields are required."

    if len(username) > 100:
        return False, "Username must be 100 characters or fewer."

    if len(email) > 255:
        return False, "Email must be 255 characters or fewer."

    if len(password) < 8:
        return False, "Password must contain at least 8 characters."

    if len(password.encode("utf-8")) > 72:
        return False, "Password must be 72 bytes or fewer."

    # Hash the password before storing it.
    password_hash = bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

    connection = get_connection()

    if connection is None:
        return False, "Could not connect to MySQL database."

    cursor = None

    try:
        cursor = connection.cursor()

        query = """
            INSERT INTO users (username, email, password_hash)
            VALUES (%s, %s, %s)
        """

        cursor.execute(
            query,
            (username, email, password_hash)
        )

        connection.commit()

        return True, "Account created successfully!"

    except Error as e:
        connection.rollback()

        if e.errno == 1062:
            return False, "Username or email already exists."

        print("Signup database error:", e)
        return False, "Could not create account. Please try again."

    finally:
        if cursor is not None:
            cursor.close()
        connection.close()


# =====================================
# LOGIN
# =====================================

def login_user(username, password):
    username = username.strip()

    if not username or not password:
        return None, "Enter username and password."

    connection = get_connection()

    if connection is None:
        return None, "Could not connect to MySQL database."

    cursor = None

    try:
        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT id, username, email, password_hash
            FROM users
            WHERE username = %s
        """

        cursor.execute(query, (username,))
        user = cursor.fetchone()

        if user is None:
            return None, "Invalid username or password."

        stored_hash = user["password_hash"].encode("utf-8")

        if bcrypt.checkpw(password.encode("utf-8"), stored_hash):
            # Never return the password hash to the app.
            safe_user = {
                "id": user["id"],
                "username": user["username"],
                "email": user["email"]
            }

            return safe_user, "Login successful!"

        return None, "Invalid username or password."

    except Error as e:
        print("Login database error:", e)
        return None, "Login failed. Please try again."

    finally:
        if cursor is not None:
            cursor.close()
        connection.close()


# =====================================
# ADD JOB APPLICATION
# =====================================

def add_application(
    company_name,
    job_role,
    application_date,
    source,
    status,
    interview_date,
    notes,
    user_id
):
    connection = get_connection()

    if connection is None:
        raise Exception("Could not connect to MySQL database.")

    cursor = None

    try:
        cursor = connection.cursor()

        query = """
            INSERT INTO job_applications
            (
                company_name, job_role, application_date,
                source, status, interview_date, notes, user_id
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """

        values = (
            company_name,
            job_role,
            application_date,
            source,
            status,
            interview_date,
            notes,
            user_id
        )

        cursor.execute(query, values)
        connection.commit()

        return True

    except Error as e:
        connection.rollback()
        print("Error adding application:", e)
        raise

    finally:
        if cursor is not None:
            cursor.close()
        connection.close()


# =====================================
# GET ALL APPLICATIONS
# =====================================

def get_applications():
    connection = get_connection()
    print("DEBUG: get_applications connected", flush=True)

    if connection is None:
        raise Exception("Could not connect to MySQL database.")

    cursor = None

    try:
        cursor = connection.cursor()
        print("DEBUG: cursor created", flush=True)

        query = """
            SELECT
                id, company_name, job_role, application_date,
                source, status, interview_date, notes
            FROM job_applications
            ORDER BY id DESC
        """

        cursor.execute(query)
        return cursor.fetchall()

    except Error as e:
        print("Error fetching applications:", e)
        raise

    finally:
        if cursor is not None:
            cursor.close()
        connection.close()


# =====================================
# UPDATE APPLICATION STATUS
# =====================================

def update_status(application_id, new_status):
    connection = get_connection()

    if connection is None:
        raise Exception("Could not connect to MySQL database.")

    cursor = None

    try:
        cursor = connection.cursor()

        query = """
            UPDATE job_applications
            SET status = %s
            WHERE id = %s
        """

        cursor.execute(query, (new_status, application_id))
        connection.commit()

        return cursor.rowcount > 0

    except Error as e:
        connection.rollback()
        print("Error updating status:", e)
        raise

    finally:
        if cursor is not None:
            cursor.close()
        connection.close()


# =====================================
# EDIT APPLICATION DETAILS
# =====================================

def update_application(
    application_id,
    company_name,
    job_role,
    application_date,
    source,
    status,
    interview_date,
    notes
):
    connection = get_connection()

    if connection is None:
        raise Exception("Could not connect to MySQL database.")

    cursor = None

    try:
        cursor = connection.cursor()

        query = """
            UPDATE job_applications
            SET
                company_name = %s,
                job_role = %s,
                application_date = %s,
                source = %s,
                status = %s,
                interview_date = %s,
                notes = %s
            WHERE id = %s
        """

        values = (
            company_name,
            job_role,
            application_date,
            source,
            status,
            interview_date,
            notes,
            application_id
        )

        cursor.execute(query, values)
        connection.commit()

        return cursor.rowcount > 0

    except Error as e:
        connection.rollback()
        print("Error editing application:", e)
        raise

    finally:
        if cursor is not None:
            cursor.close()
        connection.close()


# =====================================
# DELETE APPLICATION
# =====================================

def delete_application(application_id):
    connection = get_connection()

    if connection is None:
        raise Exception("Could not connect to MySQL database.")

    cursor = None

    try:
        cursor = connection.cursor()

        query = """
            DELETE FROM job_applications
            WHERE id = %s
        """

        cursor.execute(query, (application_id,))
        connection.commit()

        return cursor.rowcount > 0

    except Error as e:
        connection.rollback()
        print("Error deleting application:", e)
        raise

    finally:
        if cursor is not None:
            cursor.close()
        connection.close()


# =====================================
# SEARCH APPLICATIONS
# =====================================

def search_applications(company_name):
    connection = get_connection()

    if connection is None:
        raise Exception("Could not connect to MySQL database.")

    cursor = None

    try:
        cursor = connection.cursor()

        query = """
            SELECT
                id, company_name, job_role, application_date,
                source, status, interview_date, notes
            FROM job_applications
            WHERE company_name LIKE %s
            ORDER BY id DESC
        """

        cursor.execute(query, (f"%{company_name}%",))
        return cursor.fetchall()

    except Error as e:
        print("Error searching applications:", e)
        raise

    finally:
        if cursor is not None:
            cursor.close()
        connection.close()


# =====================================
# DASHBOARD STATISTICS
# =====================================

def get_statistics():
    connection = get_connection()

    if connection is None:
        raise Exception("Could not connect to MySQL database.")

    cursor = None

    try:
        cursor = connection.cursor()

        query = """
            SELECT
                COUNT(*) AS total,
                COALESCE(SUM(status = 'Applied'), 0) AS applied,
                COALESCE(SUM(status = 'Interview'), 0) AS interview,
                COALESCE(SUM(status = 'Rejected'), 0) AS rejected,
                COALESCE(SUM(status = 'Selected'), 0) AS selected
            FROM job_applications
        """

        cursor.execute(query)
        result = cursor.fetchone()

        return {
            "total": result[0],
            "applied": result[1],
            "interview": result[2],
            "rejected": result[3],
            "selected": result[4]
        }

    except Error as e:
        print("Error getting statistics:", e)
        raise

    finally:
        if cursor is not None:
            cursor.close()
        connection.close()