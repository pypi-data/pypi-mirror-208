import platform
import subprocess
import time
import os
def destroy_me():
    system = platform.system()
    answer = input("Are you sure you want to destroy yourself computer? (y/n)")
    if answer == "y" or answer == "Y":
        print("Destroying computer...")
    else:
        print("Aborting destroy...")
        return None

    if system == "Windows":
        subprocess.call(["shutdown", "/s", "/t", "0"])
    elif system == "Linux" or system == "Darwin":
        subprocess.call(["shutdown", "-h", "now"])
    else:
        print("Unsupported operating system.")


def HanG():
    print("Ma aa gya maa. Meri shaktiyun ka galat istamal ho gya.")


def surprise_me():
    exp = False
    x = 10
    while x > 0:
        try:
            if exp:
                time.sleep(2)
            os.system('clear')
            print("💣💣💣 Your whole data will be erased in: ")
            print(x)
            time.sleep(1)
            x -= 1
            exp = False

        except KeyboardInterrupt:
            print("⛔⛔⛔ You can not undone this process. ⛔⛔⛔")
            exp = True
    print("Haha I'm joking 😂😂😂😂.")

surprise_me()