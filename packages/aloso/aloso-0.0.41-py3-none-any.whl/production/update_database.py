from output.models.user_database import UserData

if __name__ == "__main__":
    user = UserData(username="admin", password="admin", admin=True)
    user.create()