import firebase_admin
from firebase_admin import credentials, messaging

# Initialize the Firebase Admin SDK
cred = credentials.Certificate('serviceAccountKey.json')
firebase_admin.initialize_app(cred)

def send_notification(title, body, message_id):
    # Construct the message with a specific notification ID
    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body,
        ),
        token="fO7UR2aSQYOzBpj5WvrYdb:APA91bEOUc-04jhoN6CLOapGqW9DZhm-vLHRc8IwgLrio1ql3Mnq5KzqNcZKTG1VpOKoJ8AVivCzQOeQz6Tlzjfs4o4-Z1azgkghQk2uqf4gWabRkEWWi3c",
        android=messaging.AndroidConfig(
            notification=messaging.AndroidNotification(
                tag=message_id
            )
        )
    )

    # Send the message
    response = messaging.send(message)
    #print('Successfully sent message:', response)

# Example usage
if __name__ == '__main__':
    # The registration token of the device to which you want to send a notification
    registration_token = 'fO7UR2aSQYOzBpj5WvrYdb:APA91bEOUc-04jhoN6CLOapGqW9DZhm-vLHRc8IwgLrio1ql3Mnq5KzqNcZKTG1VpOKoJ8AVivCzQOeQz6Tlzjfs4o4-Z1azgkghQk2uqf4gWabRkEWWi3c'
    send_notification('test', 'This is a test notification.', 'DONE1')
