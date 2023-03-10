from bot import MyBot


def main():
    with open("TOKEN.txt", "r") as f:
        TOKEN = f.read()
    discord_bot = MyBot(command_prefix="-", self_bot=False)
    discord_bot.run(TOKEN)


if __name__ == "__main__":
    main()
