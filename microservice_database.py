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

c.execute("""create table if not exists comments_table (comment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                                             comment text,
                                             username TEXT,
                                             article_id INTEGER,
                                             createdDate text,
                                             FOREIGN KEY(article_id) REFERENCES articles_table(article_id))""")

c.execute("""CREATE TABLE tag_master (
                    tagId INTEGER PRIMARY KEY AUTOINCREMENT,
                    tagName TEXT,
                    createdTime DATETIME,
                    updatedTime DATETIME)""")

c.execute("""CREATE TABLE tag_detail (
                    article_id INTEGER,
                    tagId INTEGER NOT NULL REFERENCES tag_master(tagId),
                    createdTime DATETIME,
                    updatedTime DATETIME,
                    PRIMARY KEY(article_id,tagId),
                    FOREIGN KEY (article_id) REFERENCES articles_table(article_id))""")

connection.commit()
connection.close()
