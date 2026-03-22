from django.apps import AppConfig


class usersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'

    def ready(self):
        import users.signals 
        #this registers signals or else the receiver does not receive signals
