import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import datetime
import time
from colorama import Fore, Back, Style
from randfacts import get_fact

cred_path = 'chatterbot-760c0-firebase-adminsdk-9dwdl-d1b8eb0121.json'
database_link = 'https://chatterbot-760c0-default-rtdb.europe-west1.firebasedatabase.app'


class FirebaseConnection:
    def __init__(self, cred, database_url):
        self.listener = None
        self.cred = cred
        self.database_url = database_url
        self.username = 'RASA-CHATBOT'
        self.initialize_app_to_firebase()
        self.ref = db.reference('session/user')
        self.sessionID = ''

    def initialize_app_to_firebase(self):
        # Use a service account
        cred_obj = credentials.Certificate(self.cred)
        default_app = firebase_admin.initialize_app(cred_obj, {'databaseURL': self.database_url})
        print('######################################')
        print(Fore.RED + 'Rasa Fire connecting initialized', Style.RESET_ALL)

    def create_message(self, content_of_message):
        now = datetime.datetime.now()
        message = {
            'message': content_of_message,
            'username': self.username,
            "timestamp": time.time(),
            "date": now.strftime('%Y-%m-%d %H:%M:%S.%f'),
        }
        return message

    def write_data_to_firebase(self, message, session_id):
        session_ref = self.ref.child(f'{session_id}/message')
        session_ref.push(message)
        # print(f'Message sent to firebase : {message}')
        return None

    def write_data_to_firebase_to_RASA(self, message, session_id):
        session_ref = self.ref.child(f'{session_id}/message/RASA')
        session_ref.set(message)
        # print(f'Message sent to firebase : {message}')
        return None

    def add_session_data_to_firebase(self,session_id):
        message = {
            'RasaBotName': self.username,
            'RasaBotStatus': 'Online'
        }
        # self.ref = db.reference('session/user')

        session_ref = db.reference(f'session/user/{session_id}')
        session_ref.update(message)
        # print(f'Message sent to firebase : {message}')
        return None

    def listen_for_new_data(self):
        # Define the function to handle new data events
        print(Fore.CYAN + 'Listening for new session...', Style.RESET_ALL)
        self.ref.listen(self.on_session_change)

    def on_session_change(self, event):
        data = event.data
        if data is not None and 'sessionID' in data:
            name = data['username']
            self.sessionID = data['sessionID']
            print('######################################')
            print(f'You are now connected to the session: {self.sessionID}')
            print('--------------------------------------')
            self.add_session_data_to_firebase(session_id=self.sessionID)
            self.write_data_to_firebase(message=self.create_message(content_of_message=f'Hello {name} I am {self.username}. How can I help you?'), session_id=self.sessionID)
            self.write_data_to_firebase_to_RASA(message=self.create_message(
                content_of_message=f'Hello {name} I am {self.username}. How can I help you?'),
                                        session_id=self.sessionID)
        if data is not None and 'username' and 'message' in data:
            formatted_data = f"{Back.WHITE + data['username']} ({Back.WHITE + data['date']}):{Style.RESET_ALL} {Fore.GREEN + data['message'] + Style.RESET_ALL}"
            print(formatted_data)
            # print(self.create_message(data['message']))
            if data['username'] == self.sessionID[:self.sessionID.index("-")]:
                name = data['username']
                self.write_data_to_firebase(message=self.create_message(
                    content_of_message=f'Hello {name} - Rasa response'), session_id=self.sessionID)
                self.write_data_to_firebase_to_RASA(message=self.create_message(
                    content_of_message=f'Here is a random fact :  {get_fact(only_unsafe=False)}'), session_id=self.sessionID)


def main():
    firebase_obj = FirebaseConnection(cred=cred_path, database_url=database_link)
    firebase_obj.listen_for_new_data()


if __name__ == '__main__':
    main()
