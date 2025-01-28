from my_bot import MYBot


class Users:
    _instances = None

    def __new__(cls):
        if cls._instances is None:
            cls._instances = super(Users, cls).__new__(cls)
            cls.list_users = []

        return cls._instances

    def locate_user(self, user_id) -> MYBot:
        index = next((i for i, data in enumerate(self.list_users) if data.user_id == user_id), None)
        if index is not None:
            return self.list_users[index]
        else:
            self.list_users.append(MYBot(user_id))
            return self.list_users[-1]
