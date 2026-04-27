import os
from dotenv import load_dotenv
from copyleaks.copyleaks import Copyleaks

load_dotenv()

email = os.getenv("COPYLEAKS_EMAIL")
api_key = os.getenv("COPYLEAKS_API_KEY")

token = Copyleaks.login(email, api_key)

print("Login successful")
print(token)