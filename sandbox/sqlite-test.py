import sqlite3

# conn = sqlite3.connect("employee.db")
conn = sqlite3.connect(":memory:")
c = conn.cursor()

c.execute(''' CREATE TABLE employees (
            first text,
            last text,
            pay integer
            )''')

c.execute("INSERT INTO employees VALUES ('John', 'Doe', 20000)")
c.execute("INSERT INTO employees VALUES ('Dan', 'Rode', 35000)")
c.execute("INSERT INTO employees VALUES ('Susan', 'Smith', 121000)")
conn.commit()

c.execute("SELECT * FROM employees")
print(c.fetchall())

conn.commit()
conn.close()