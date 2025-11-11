"""
Script to create a sample HR database with realistic data.
Run this to set up the initial database for testing.
"""

import random
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

# Database file path
DB_PATH = Path(__file__).parent.parent / "hr_data.db"


def create_sample_database():
    """Create sample HR database with tables and data"""

    # Connect to database (creates file if doesn't exist)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print(f"Creating sample database at {DB_PATH}...")

    # Create Employees table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            employee_id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            department TEXT NOT NULL,
            position TEXT NOT NULL,
            hire_date DATE NOT NULL,
            salary REAL NOT NULL,
            manager_id INTEGER,
            status TEXT DEFAULT 'Active',
            FOREIGN KEY (manager_id) REFERENCES employees(employee_id)
        )
    """)

    # Create Departments table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS departments (
            department_id INTEGER PRIMARY KEY AUTOINCREMENT,
            department_name TEXT UNIQUE NOT NULL,
            head_employee_id INTEGER,
            budget REAL,
            location TEXT,
            FOREIGN KEY (head_employee_id) REFERENCES employees(employee_id)
        )
    """)

    # Create Leave Records table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leave_records (
            leave_id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER NOT NULL,
            leave_type TEXT NOT NULL,
            start_date DATE NOT NULL,
            end_date DATE NOT NULL,
            days_count INTEGER NOT NULL,
            status TEXT DEFAULT 'Pending',
            reason TEXT,
            approved_by INTEGER,
            approved_date DATE,
            FOREIGN KEY (employee_id) REFERENCES employees(employee_id),
            FOREIGN KEY (approved_by) REFERENCES employees(employee_id)
        )
    """)

    # Create Attendance table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            attendance_id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER NOT NULL,
            date DATE NOT NULL,
            check_in_time TIME,
            check_out_time TIME,
            hours_worked REAL,
            status TEXT DEFAULT 'Present',
            FOREIGN KEY (employee_id) REFERENCES employees(employee_id),
            UNIQUE(employee_id, date)
        )
    """)

    # Create Performance Reviews table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS performance_reviews (
            review_id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER NOT NULL,
            review_date DATE NOT NULL,
            reviewer_id INTEGER NOT NULL,
            rating INTEGER CHECK(rating >= 1 AND rating <= 5),
            comments TEXT,
            goals_met INTEGER,
            areas_of_improvement TEXT,
            FOREIGN KEY (employee_id) REFERENCES employees(employee_id),
            FOREIGN KEY (reviewer_id) REFERENCES employees(employee_id)
        )
    """)

    print("Tables created successfully")

    # Insert sample data

    # Sample employees
    employees_data = [
        (
            "John",
            "Doe",
            "john.doe@company.com",
            "Engineering",
            "Software Engineer",
            "2020-01-15",
            75000,
            None,
            "Active",
        ),
        (
            "Jane",
            "Smith",
            "jane.smith@company.com",
            "HR",
            "HR Manager",
            "2019-03-20",
            85000,
            None,
            "Active",
        ),
        (
            "Mike",
            "Johnson",
            "mike.j@company.com",
            "Engineering",
            "Senior Developer",
            "2018-06-10",
            95000,
            1,
            "Active",
        ),
        (
            "Sarah",
            "Williams",
            "sarah.w@company.com",
            "Marketing",
            "Marketing Specialist",
            "2021-02-01",
            65000,
            None,
            "Active",
        ),
        (
            "Robert",
            "Brown",
            "robert.b@company.com",
            "Finance",
            "Financial Analyst",
            "2020-08-15",
            70000,
            None,
            "Active",
        ),
        (
            "Emily",
            "Davis",
            "emily.d@company.com",
            "Engineering",
            "Junior Developer",
            "2022-04-01",
            60000,
            3,
            "Active",
        ),
        (
            "David",
            "Martinez",
            "david.m@company.com",
            "Sales",
            "Sales Manager",
            "2019-11-10",
            90000,
            None,
            "Active",
        ),
        (
            "Lisa",
            "Anderson",
            "lisa.a@company.com",
            "HR",
            "HR Specialist",
            "2021-07-15",
            55000,
            2,
            "Active",
        ),
        (
            "James",
            "Taylor",
            "james.t@company.com",
            "Engineering",
            "DevOps Engineer",
            "2020-12-01",
            80000,
            1,
            "Active",
        ),
        (
            "Maria",
            "Garcia",
            "maria.g@company.com",
            "Marketing",
            "Content Writer",
            "2022-01-10",
            50000,
            4,
            "Active",
        ),
    ]

    cursor.executemany(
        """
        INSERT INTO employees (first_name, last_name, email, department, position, hire_date, salary, manager_id, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
        employees_data,
    )

    print(f"Inserted {len(employees_data)} employees")

    # Sample departments
    departments_data = [
        ("Engineering", 3, 500000, "Building A"),
        ("HR", 2, 200000, "Building B"),
        ("Marketing", 4, 150000, "Building B"),
        ("Finance", 5, 300000, "Building C"),
        ("Sales", 7, 400000, "Building A"),
    ]

    cursor.executemany(
        """
        INSERT INTO departments (department_name, head_employee_id, budget, location)
        VALUES (?, ?, ?, ?)
    """,
        departments_data,
    )

    print(f"Inserted {len(departments_data)} departments")

    # Sample leave records
    leave_types = ["Sick Leave", "Vacation", "Personal Leave", "Maternity Leave"]
    leave_statuses = ["Approved", "Approved", "Pending", "Rejected"]  # More approved

    leave_records = []
    for i in range(1, 11):  # For each employee
        for _ in range(random.randint(2, 5)):  # 2-5 leave records per employee
            leave_type = random.choice(leave_types)
            start_date = datetime.now() - timedelta(days=random.randint(1, 365))
            days = random.randint(1, 10)
            end_date = start_date + timedelta(days=days)
            status = random.choice(leave_statuses)
            approved_by = 2 if status == "Approved" else None

            leave_records.append(
                (
                    i,
                    leave_type,
                    start_date.strftime("%Y-%m-%d"),
                    end_date.strftime("%Y-%m-%d"),
                    days,
                    status,
                    f"Reason for {leave_type}",
                    approved_by,
                    start_date.strftime("%Y-%m-%d") if status == "Approved" else None,
                )
            )

    cursor.executemany(
        """
        INSERT INTO leave_records (employee_id, leave_type, start_date, end_date, days_count, status, reason, approved_by, approved_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """,
        leave_records,
    )

    print(f"Inserted {len(leave_records)} leave records")

    # Sample attendance records (last 30 days)
    attendance_records = []
    for employee_id in range(1, 11):
        for day_offset in range(30):
            date = datetime.now() - timedelta(days=day_offset)
            if date.weekday() < 5:  # Weekdays only
                check_in = "09:00:00"
                check_out = "18:00:00"
                hours = 9.0 + random.uniform(-0.5, 0.5)
                status = random.choice(
                    ["Present", "Present", "Present", "Late", "Half Day"]
                )

                attendance_records.append(
                    (
                        employee_id,
                        date.strftime("%Y-%m-%d"),
                        check_in,
                        check_out,
                        hours,
                        status,
                    )
                )

    cursor.executemany(
        """
        INSERT INTO attendance (employee_id, date, check_in_time, check_out_time, hours_worked, status)
        VALUES (?, ?, ?, ?, ?, ?)
    """,
        attendance_records,
    )

    print(f"Inserted {len(attendance_records)} attendance records")

    # Sample performance reviews
    reviews = []
    for employee_id in range(1, 11):
        review_date = datetime.now() - timedelta(days=random.randint(30, 180))
        rating = random.randint(3, 5)
        reviewer_id = 2  # HR Manager

        reviews.append(
            (
                employee_id,
                review_date.strftime("%Y-%m-%d"),
                reviewer_id,
                rating,
                f"Good performance with rating {rating}",
                random.randint(5, 10),
                "Continue improving communication skills",
            )
        )

    cursor.executemany(
        """
        INSERT INTO performance_reviews (employee_id, review_date, reviewer_id, rating, comments, goals_met, areas_of_improvement)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """,
        reviews,
    )

    print(f"Inserted {len(reviews)} performance reviews")

    # Commit and close
    conn.commit()
    conn.close()

    print(f"\n✅ Sample database created successfully at {DB_PATH}")
    print(f"Total records:")
    print(f"  - Employees: {len(employees_data)}")
    print(f"  - Departments: {len(departments_data)}")
    print(f"  - Leave Records: {len(leave_records)}")
    print(f"  - Attendance Records: {len(attendance_records)}")
    print(f"  - Performance Reviews: {len(reviews)}")


if __name__ == "__main__":
    create_sample_database()
