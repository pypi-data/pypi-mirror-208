import configparser

def authenticate(password):
    config = configparser.ConfigParser()
    config.read('config.ini')

    stored_password = config.get('Authentication', 'password')

    if password == stored_password:
        print("Authentication successful!")
        return True
    else:
        print("Authentication failed!")
        return False

def add(x, y):
    if authenticate(input("Enter your password: ")):
        return x + y
    else:
        return None
    

def sub(x, y):
    if authenticate(input("Enter your password: ")):
        return x - y
    else:
        return None

