from tkinter import Message

from MySQLdb import connect


class Db(object):
    def __init__(self, db_user: str = None, db_password: str = None, db_host: str = None):

        self.conn = connect(host=db_host, user=db_user, password=db_password
                            )

        self.cur = self.conn.cursor()

    def get_all_users(self):
        self.cur.execute('SELECT * FROM users')
        users = self.cur.fetchall()
        self.cur.close()
        self.conn.close()
        return users

    def find_user_by_password(self, password):
        self.cur.execute('SELECT * FROM users WHERE password=?', password)
        user = self.cur.fetchone()
        self.cur.close()
        return user

    def find_user_by_email(self, email):
        self.cur.execute('SELECT * FROM users WHERE email=?', email)
        user = self.cur.fetchone()
        self.cur.close()

        return user

    def find_user_by_phone(self, phone):
        self.cur.execute('SELECT * FROM users WHERE phone=?', phone)
        user = self.cur.fetchone()
        self.cur.close()
        self.conn.close()
        return user

    def create_user(
            self, db_name,
            statement: str, data: str

    ):
        self.conn = connect(db_name)
        self.cur = self.conn.cursor()
        self.cur.execute(statement, data)
        self.conn.commit()

        pass

    def get_user_by_email(self, email):
        self.cur.execute('SELECT * FROM users WHERE email=?', email)
        user = self.cur.fetchone()
        if user:
            self.cur.close()
            return user
        else:
            self.cur.close()
            message = "User not found"
            Message(text=message)
            return None
        pass
