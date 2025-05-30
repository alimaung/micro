import win32com.client
import os
import time
import win32print
import win32api

OUTLOOK_NAMESPACE = "MAPI"
PRINTER_NAME = win32print.GetDefaultPrinter()  # You can set this to another printer

def connect_outlook():
    outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace(OUTLOOK_NAMESPACE)
    inbox = outlook.GetDefaultFolder(6)  # 6 refers to the inbox
    return inbox

def print_file(filepath):
    win32api.ShellExecute(
        0,
        "print",
        filepath,
        f'/d:"{PRINTER_NAME}"',
        ".",
        0
    )

def monitor_inbox(subject_filter=None):
    inbox = connect_outlook()
    messages = inbox.Items
    messages.Sort("[ReceivedTime]", True)  # Sort descending by time

    for message in messages:
        if subject_filter and subject_filter not in message.Subject:
            continue

        attachments = message.Attachments
        if attachments.Count > 0:
            for i in range(1, attachments.Count + 1):
                attachment = attachments.Item(i)
                filename = os.path.join(os.getcwd(), attachment.FileName)
                attachment.SaveAsFile(filename)
                print_file(filename)
            break  # Remove this if you want to keep scanning

if __name__ == "__main__":
    while True:
        monitor_inbox(subject_filter="PrintMe")
        time.sleep(60)  # Check every 60 seconds
