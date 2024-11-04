from instabot import Bot
import os
import random
import time


# Function to add a random delay to avoid rate limiting
def random_delay():
    delay = random.randint(30, 60)  # Change the delay range if needed
    print(f"Sleeping for {delay} seconds to avoid rate limit.")
    time.sleep(delay)


# Function to fetch followers
def fetch_followers(bot, username):
    print(f"Fetching followers for user: {username}")
    followers = bot.get_user_followers(username)
    print(f"Total followers fetched: {len(followers)}")
    return followers


# Function to remove followers (placeholder)
def remove_followers(bot, followers):
    print("Starting to remove followers...")
    for follower in followers:
        print(f"Processing follower: {follower}")
        random_delay()  # Delay between actions to avoid rate limiting
        # Here you would add logic to remove each follower


# Load login credentials
username = os.getenv('INSTAGRAM_USERNAME', 'engaged_ape')
password = os.getenv('INSTAGRAM_PASSWORD', 'Sonofhapu33')

# Create bot instance and login
bot = Bot()

try:
    print("Attempting to log in...")
    bot.login(username=username, password=password, use_cookie=False)
    print("Login successful.")
    random_delay()  # Avoiding rate limit
except Exception as e:
    print(f"Login failed: {e}")
    exit()

# Run the actual script logic here.
try:
    # Fetch followers
    followers = fetch_followers(bot, username)
    random_delay()  # Avoiding rate limit

    # Provide options for next action
    while True:
        print("\nWhat would you like to do next?")
        print("1. Remove followers")
        print("2. View followers (print IDs)")
        print("3. Logout and exit")

        choice = input("Enter your choice (1, 2, or 3): ")

        if choice == '1':
            remove_followers(bot, followers)
        elif choice == '2':
            print("Followers:", followers)
        elif choice == '3':
            break
        else:
            print("Invalid choice, please try again.")

except Exception as e:
    print(f"An error occurred: {e}")

# Log out after actions are done
try:
    print("Logging out...")
    bot.logout()
    print("Logout successful.")
except Exception as e:
    print(f"Logout failed: {e}")
