import sqlite3
connection = sqlite3.connect('microservice.db')
c=connection.cursor()
c.execute("""create table if not exists users_table(name TEXT,
                                    username TEXT PRIMARY KEY,
                                    userpassword TEXT)""")
c.execute("""create table if not exists articles_table (article_id INTEGER PRIMARY KEY AUTOINCREMENT,
                                            article_title text UNIQUE,
                                            article_content text,
                                            article_author text,
                                            URL text,
                                            createdDate text,
                                            modifiedDate text,
                                            FOREIGN KEY(article_author) REFERENCES users_table(username))""")
connection.commit()
connection.close()
