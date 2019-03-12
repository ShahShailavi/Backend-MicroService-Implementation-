import sqlite3
connection = sqlite3.connect('microservice.db')
c=connection.cursor()
c.execute("""create table if not exists users_table(username TEXT,
                                    useremail TEXT PRIMARY KEY,
                                    userpassword TEXT)""")
connection.commit()
connection.close()
