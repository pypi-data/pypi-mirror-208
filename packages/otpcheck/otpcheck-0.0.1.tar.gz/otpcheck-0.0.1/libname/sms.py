import random

def optcheck():
    sms = random.randint(1000,9999)
    print(sms)

    otp = int(input("Enter the OTP \n"))
    if otp == sms:
        print("Entered OTP is valid")
    else:
        print("Entered OTP is invalid, try again")
optcheck()