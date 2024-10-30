import psycopg2


class DatabaseConnection:
    def __init__(self):
        self.connection = None

    def __enter__(self):
        self.connection = psycopg2.connect(user="postgres", password="admin@123", host="127.0.0.1", port="5432", database="tevisa")
        return self.connection
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type or exc_val or exc_tb:
            self.connection.close()
        else:
            self.connection.commit()
            self.connection.close()