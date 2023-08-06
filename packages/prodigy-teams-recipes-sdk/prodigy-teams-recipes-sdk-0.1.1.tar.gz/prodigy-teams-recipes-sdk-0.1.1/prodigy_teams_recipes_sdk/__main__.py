# This function is exposed via the setup.cfg as the ptr commant, so don't change this!
def main():
    from .engine.cli import cli

    cli.run()


if __name__ == "__main__":
    main()
