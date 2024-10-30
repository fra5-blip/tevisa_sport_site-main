from user import User


class Admin(User):
    def __init__(self, username, password, access):
        super(Admin, self).__init__(username, password)
        self.access = access


    def __repr__(self):
        return f'<Name: {self.username}, Access: {self.access}>'


    def to_dick(self):
        return {
            'username': self.username,
            'password': self.password,
            'access': self.access
        }


user1 = Admin('Anthony', 'ant@123', 'guest')

print(user1)

