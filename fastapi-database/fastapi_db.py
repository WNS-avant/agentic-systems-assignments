from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, select, insert, update, delete

engine = create_engine("mysql+pymysql://root:hulk@localhost/student_db")

metadata = MetaData()

students = Table(
    "students",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(50), nullable=False),
    Column("age", Integer),
    Column("city", String(50), nullable=True)
)

metadata.create_all(engine)

with engine.connect() as conn:

    insert_query = insert(students).values([
        {"name": "Rahul", "age": 22, "city": "Delhi"},
        {"name": "Amit", "age": 19, "city": "Mumbai"},
        {"name": "Priya", "age": 21, "city": "Hyderabad"}
    ])

    conn.execute(insert_query)
    conn.commit()


with engine.connect() as conn:

    select_query = select(students)
    result = conn.execute(select_query)

    print("All Students:")
    for row in result:
        print(row)


with engine.connect() as conn:

    update_query = (
        update(students)
        .where(students.c.name == "Rahul")
        .values(city="Bangalore")
    )

    conn.execute(update_query)
    conn.commit()


with engine.connect() as conn:

    delete_query = delete(students).where(students.c.age < 20)

    conn.execute(delete_query)
    conn.commit()