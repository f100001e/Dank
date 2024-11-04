import os
import time
import random
import instaloader
from instabot import Bot
import concurrent.futures
from alive_progress import alive_bar
from colorama import init, Fore, Style
import shutil

# Initialize color settings
init(autoreset=True)
red = Fore.RED + Style.BRIGHT
green = Fore.GREEN + Style.BRIGHT
magenta = Fore.MAGENTA + Style.BRIGHT
white = Fore.WHITE + Style.BRIGHT


# Random delay function to avoid rate limiting
def random_delay():
    delay = random.randint(300, 600)
    print(f"Sleeping for {delay} seconds to avoid rate limiting.")
    time.sleep(delay)


# Create banner with colored ASCII art
def banner():
    banner_ascii = '''
      _             _      _           _              _              _ 
   __| | __ _ _ __ | | __ (_)_ __  ___| |_ __ _      | |_ ___   ___ | |
  / _` |/ _` | '_ \\| |/ / | | '_ \\/ __| __/ _` |_____| __/ _ \\ / _ \\| |
 | (_| | (_| | | | |   < _| | | | \\__ \\ || (_| |_____| || (_) | (_) | |
  \\__,_|\\__,_|_| |_|_|\\_(_)_|_| |_|___/\\__\\__,_|      \\__\\___/ \\___/|_|
    '''
    bad_colors = ['BLACK', 'WHITE', 'LIGHTBLACK_EX', 'LIGHTWHITE_EX', 'RESET']
    colors = [getattr(Fore, color) for color in vars(Fore) if color not in bad_colors]
    colored_banner = ''.join(random.choice(colors) + char for char in banner_ascii)

    try:
        width = shutil.get_terminal_size().columns
    except OSError:
        width = 80
    banner_lines = [line.center(width) for line in colored_banner.splitlines()]
    return '\n'.join(banner_lines)


# Multithread handler
def multithread(function, items):
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        futures = [executor.submit(function, item) for item in items]
        with alive_bar(len(futures)) as bar:
            for future in concurrent.futures.as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    print(f"\n{red}Error: {e}")
                bar()


# Fetch and save followers, likers, and commenters
def one():
    login_username = input(f"\n  {white}> {magenta}Enter your Instagram username{white}: {magenta}").lower()

    # Instaloader login
    L = instaloader.Instaloader()
    L.load_session_from_file(login_username)
    profile = instaloader.Profile.from_username(L.context, login_username)
    random_delay()

    liked_users, commented_users, followers = set(), set(), []

    def get_users(post):
        try:
            liked_users.update(str(like.username) for like in post.get_likes())
            commented_users.update(str(comment.owner.username) for comment in post.get_comments())
            random_delay()
        except Exception as e:
            print(f"\n  {red}Error fetching users for post: {e}")

    print(f"\n  {white}> {magenta}Fetching likers and commenters from posts. Please wait...\n")
    multithread(get_users, profile.get_posts())

    print(f"\n  {white}> {magenta}Fetching followers. Please wait...\n")

    def get_follower_usernames(follower):
        try:
            followers.append(str(follower.username))
            random_delay()
        except Exception as e:
            print(f"\n  {red}Error fetching follower: {e}")

    multithread(get_follower_usernames, profile.get_followers())

    # Identify ghosts and non-ghosts
    non_ghosts = [user for user in followers if user in liked_users or user in commented_users]
    ghosts = [user for user in followers if user not in liked_users and user not in commented_users]

    # Save results to files
    print(f"\n  {white}> {magenta}Saving results to files...\n")
    with open('non_ghosts.txt', 'w') as file:
        file.write('\n'.join(non_ghosts))
    with open('ghosts.txt', 'w') as file:
        file.write('\n'.join(ghosts))
    print(f"\n  {green}Task completed! Ghosts saved to ghosts.txt.")
    random_delay()


# Remove ghost followers
def two():
    try:
        with open("ghosts.txt", "r") as file:
            ghosts = list(set(file.read().splitlines()))
    except FileNotFoundError:
        print(f"\n  {red}The file ghosts.txt does not exist! Run option 1 first!")
        time.sleep(5)
        return

    bot = Bot()
    try:
        bot.login()
        random_delay()
    except Exception as e:
        print(f"\n  {red}Login failed: {e}")
        return

    removed_ghosts, unremoved_ghosts = [], []

    def remove_follower(user):
        errors = 0
        while errors < 4:
            try:
                user_id = bot.get_user_id_from_username(user)
                bot.api.remove_follower(user_id)
                removed_ghosts.append(user)
                print(f"\n  {green}Removed {user}!")
                random_delay()
                return
            except Exception as e:
                errors += 1
                print(f"\n  {red}Error removing {user}, retrying... ({errors}/4)")
                time.sleep(10)
        unremoved_ghosts.append(user)

    print(f"\n  {white}> {magenta}Removing {white}{len(ghosts)} ghosts...\n")
    multithread(remove_follower, ghosts)

    with open('removed_ghosts.txt', 'w') as file:
        file.write('\n'.join(removed_ghosts))
    with open('unremoved_ghosts.txt', 'w') as file:
        file.write('\n'.join(unremoved_ghosts))
    print(f"\n  {green}Removed {len(removed_ghosts)} ghosts. Failed to remove {len(unremoved_ghosts)}.")


# Main loop with menu
while True:
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

    print(banner())

    print(f"\n  {white}> {magenta}1. Get and save {white}ghosts {magenta}/ {white}non-ghosts")
    print(f"\n  {white}> {magenta}2. Remove {white}ghost {magenta}followers")
    print(f"\n  {white}> {magenta}3. Bulk {white}unfollow (Not Implemented)")
    print(f"\n  {white}> {magenta}4. Exit")

    try:
        choice = int(input(f"\n  {white}> {magenta}Enter Choice{white}: {magenta}"))
    except ValueError:
        print(f"\n  {red}Invalid input! Please enter a number.")
        continue

    if choice == 1:
        one()
    elif choice == 2:
        two()
    elif choice == 3:
        print(f"\n  {red}Bulk unfollow option not implemented yet.")
    elif choice == 4:
        print(f"\n  {green}Exiting. Goodbye!")
        break
    else:
        print(f"\n  {red}Invalid choice! Please enter a number between 1 and 4.")
