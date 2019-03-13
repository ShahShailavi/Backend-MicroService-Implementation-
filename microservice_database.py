import sqlite3
connection = sqlite3.connect('microservice.db')
c=connection.cursor()
c.execute("""create table if not exists users_table(name TEXT,
                                    username TEXT PRIMARY KEY,
                                    userpassword TEXT)""")
c.execute("""create table if not exists articles_table (article_id INTEGER PRIMARY KEY AUTOINCREMENT,
                                            article_title text,
                                            article_content text,
                                            article_author text,
                                            FOREIGN KEY(article_author) REFERENCES users_table(username)
                                            createdDate text,
                                            modifiedDate text)""")                                        
connection.commit()
connection.close()
