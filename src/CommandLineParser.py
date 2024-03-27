import argparse
import logging
import keyring
import configparser
import sys
import os

# Get the directory of the script file
script_dir = os.path.dirname(os.path.realpath(__file__))
# Join the script directory with the relative path to the ini file
ini_path = os.path.join(script_dir, "config.ini")


def make_wide(formatter, w: int = 120, h: int = 36):
    """!
    Return a wider HelpFormatter, if possible

    @param formatter: The formatter class to use
    @param w The width of the formatter
    @param h The height of the formatter

    @return A wider HelpFormatter, if possible
    """
    try:
        # https://stackoverflow.com/a/5464440
        # Beware: "Only the name of this class is considered a public API."
        kwargs = {"width": w, "max_help_position": h}
        formatter(None, **kwargs)
        return lambda prog: formatter(prog, **kwargs)
    except TypeError:
        logging.error("Argparse help formatter failed, falling back.")
        return formatter


class CommandLineParser:
    """
    Command line user interface for the todoist-prioritizer
    """

    def __init__(self):
        """
        Initializes a CommandLineParser object
        """

        self.parser = argparse.ArgumentParser(
            formatter_class=make_wide(argparse.HelpFormatter, w=120, h=60)
        )
        self.__setup_args__()
        self.parse_args()

    def __setup_args__(self):
        """
        Sets up the command line arguments for the parser
        """
        self.parser.add_argument(
            "-a", "--api", type=str, metavar="API_TOKEN", help="Set api token"
        )
        self.parser.add_argument(
            "-p1", type=int, metavar="P1_SIZE", help="Maximum number of P1 tasks"
        )
        self.parser.add_argument(
            "-p2", type=int, metavar="P2_SIZE", help="Maximum number of P2 tasks"
        )
        self.parser.add_argument(
            "-p3", type=int, metavar="P3_SIZE", help="Maximum number of P3 tasks"
        )
        self.parser.add_argument(
            "-hh",
            type=int,
            metavar="RUN_HOUR",
            help="The hour to run the script, 24 hour format",
        )
        self.parser.add_argument(
            "-mm",
            type=int,
            metavar="RUN_MINUTE",
            help="The minute to run the script, 24 hour format",
        )
        self.parser.add_argument(
            "-r",
            "--reset",
            action="store_true",
            help="Reset configuration to default values",
        )
        self.parser.add_argument(
            "-d",
            "--debug",
            action="store_true",
            help="Enable debug logging level",
        )

    def parse_args(self, input: bool = False):
        """
        Parses the command line arguments and stores them in self.args

        @param input: If True use user inputted args, else use command line args
        """
        # Create the config parser
        config = configparser.ConfigParser()
        config.read(ini_path)

        if not input:
            self.args = self.parser.parse_args()

        logging.basicConfig(
            level=logging.DEBUG if self.args.debug else logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            datefmt="%d.%m.%Y %H:%M:%S",
        )

        if self.args.api is not None:
            logging.info("API token saved to keyring")
            keyring.set_password("system", "todoist-api-token", self.args.api)
        if self.args.p1 is not None:
            config.set("USER", "p1_tasks", str(self.args.p1))
            with open(ini_path, "w") as configfile:
                config.write(configfile)
        if self.args.p2 is not None:
            config.set("USER", "p2_tasks", str(self.args.p2))
            with open(ini_path, "w") as configfile:
                config.write(configfile)
        if self.args.p3 is not None:
            config.set("USER", "p3_tasks", str(self.args.p3))
            with open(ini_path, "w") as configfile:
                config.write(configfile)
        if self.args.hh is not None:
            config.set("USER", "run_hour", str(self.args.hh))
            with open(ini_path, "w") as configfile:
                config.write(configfile)
        if self.args.mm is not None:
            config.set("USER", "run_minute", str(self.args.mm))
            with open(ini_path, "w") as configfile:
                config.write(configfile)
        if self.args.reset:
            config.set("USER", "p1_tasks", config.get("DEFAULT", "p1_tasks"))
            config.set("USER", "p2_tasks", config.get("DEFAULT", "p2_tasks"))
            config.set("USER", "p3_tasks", config.get("DEFAULT", "p3_tasks"))
            config.set("USER", "run_hour", config.get("DEFAULT", "run_hour"))
            config.set("USER", "run_minute", config.get("DEFAULT", "run_minute"))
            with open(ini_path, "w") as configfile:
                config.write(configfile)
            logging.info("Reset")
            sys.exit(0)

    def user_input(self):
        """
        Prompts the user for input if no command line arguments are provided
        """
        if self.args.api is None:
            arg = input("Configure? (y/n): ")
            if arg == "y":
                self.args.reset = input("Reset? (y/n): ")
                if self.args.reset == "y":
                    self.args.reset = True
                else:
                    self.args.reset = False
                    self.args.api = input("Enter API token: ")
                    self.args.p1 = input("Enter P1 tasks: ")
                    self.args.p2 = input("Enter P2 tasks: ")
                    self.args.p3 = input("Enter P3 tasks: ")
                    self.args.hh = input("Enter run hour: ")
                    self.args.mm = input("Enter run minute: ")
                    self.args.debug = input("Debug logging? (y/n): ")
                    if self.args.debug == "y":
                        self.args.debug = True
                self.parse_args(True)
