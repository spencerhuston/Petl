import functools
import sys
import traceback
from datetime import datetime
from os import getcwd
from pathlib import Path
from typing import Dict, Any, Optional, List

from src.phases.interpreter.definitions.value import PetlValue
from src.phases.interpreter.environment import InterpreterEnvironment
from src.phases.interpreter.interpreter import TreeWalkInterpreter, load_builtins
from src.phases.lexer.definitions.token_petl import Token
from src.phases.lexer.lexer import Lexer
from src.phases.parser.defintions.expression import Expression, UnknownExpression
from src.phases.parser.parser import Parser
from src.utils.log import Log


def parse_arguments():
    import argparse
    parser: argparse.ArgumentParser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", required=False, metavar="{file}", help="Petl file to run")
    parser.add_argument("-d", "--debug", action="store_true", help="Enable debugging output")
    parser.add_argument("--no-debug", dest="debug", metavar="{debug}", help="Enable debugging output")
    parser.set_defaults(debug=False)
    return vars(parser.parse_known_args(sys.argv)[0])


def read_petl_file(file_path: str, logger: Log) -> Optional[str]:
    petl_file_str: Optional[str] = None
    try:
        if file_path.endswith(".petl"):
            full_path = Path(getcwd()) / file_path
            with open(full_path, "r") as petl_file:
                petl_file_str = petl_file.read()
                logger.debug_block("RAW SCRIPT", petl_file_str)
        else:
            logger.error(f"Petl script {file_path} requires extension \x1b[3m.petl\x1b[0m")
    except Exception as file_exception:
        logger.error(f"File exception: {file_exception}")
    return petl_file_str


def execute_petl_script(petl_raw_str: str, debug: bool, logger: Log) -> bool:
    start: datetime = datetime.now()
    lexer: Lexer = Lexer(debug)
    tokens: Optional[List[Token]] = lexer.scan(petl_raw_str)
    if tokens and not lexer.logger.errors_occurred():
        parser: Parser = Parser(debug)
        root: Expression = parser.parse(tokens)
        if root and not parser.logger.errors_occurred() and not isinstance(root, UnknownExpression):
            interpreter: TreeWalkInterpreter = TreeWalkInterpreter(debug)
            environment: InterpreterEnvironment = load_builtins(parser.builtins)
            result_value: PetlValue = interpreter.interpret(root, environment)
            logger.debug(f"DEBUG: {result_value.to_string()}")
            end: datetime = datetime.now()
            delta = end - start
            logger.debug(str(delta.total_seconds()))
    else:
        return False


def read_repl_input(history: List[str], history_index: int, logger: Log) -> Optional[str]:
    GREEN: str = "\033[1;33m"
    RESET: str = "\033[00m"

    def print_input_banner(text: str):
        print(f"> {GREEN}\x1B[3m{text}{RESET}", end="")

    last_input: str = ""
    while True:
        if not last_input:
            print_input_banner("")
        repl_input = input()

        if repl_input == "@quit":
            logger.info("Quitting REPL...")
            return None
        elif repl_input == "@help":
            logger.info(f"{GREEN}REPL commands:\n" + \
                        "\t@quit    - Quit the REPL\n" + \
                        "\t@help    - Display this help message\n" + \
                        "\t@prev    - Show previous input in history\n" + \
                        "\t@next    - Show next input in history\n" + \
                        "\t@clear   - Clear all input history\n" + \
                        f"\t@history - Display all input history{RESET}")
        elif repl_input == "@prev" or repl_input == "@next":
            if history:
                if repl_input == "@prev":
                    history_index = len(history) - 1 if history_index == 0 else history_index - 1
                elif repl_input == "@next":
                    history_index = 0 if history_index >= len(history) - 1 else history_index + 1
                last_input = history[history_index]
                print_input_banner(f"{history[history_index]} - ")
        elif repl_input == "@clear":
            return "@clear"
        elif repl_input == "@history":
            if history:
                logger.info(f"{GREEN}" + functools.reduce(lambda i1, i2: f"{i1}\n{i2}", history) + f"{RESET}")
        elif not repl_input:
            if last_input:
                return last_input
        else:
            return repl_input


def run_petl_repl(logger: Log):
    banner_str = "=" * 9
    logger.info(f"{banner_str}\nPetl REPL\n{banner_str}")

    interpreter_input: str = ""
    history: List[str] = []
    history_index: int = 0

    while True:
        repl_input: Optional[str] = read_repl_input(history, history_index, logger)
        if not repl_input:
            break
        elif repl_input == "@clear":
            history = []
            history_index = 0
        elif repl_input.endswith("\\"):
            repl_input = repl_input.replace("\\", "")
            interpreter_input += repl_input + "\n"
        elif repl_input.endswith(";"):
            repl_input = repl_input.replace(";", "")
            interpreter_input += repl_input + "\n"
        else:
            interpreter_input += repl_input
            history.append(interpreter_input)
            history_index = len(history)
            execute_petl_script(interpreter_input, logger.debug_enabled())
            interpreter_input = ""


def main():
    arguments: Dict[str, Any] = parse_arguments()
    debug: bool = arguments["debug"]

    logger: Log = Log(debug)
    try:
        if arguments["file"]:
            petl_raw_str = read_petl_file(arguments["file"], logger)
            if petl_raw_str:
                execute_petl_script(petl_raw_str, debug, logger)
        else:
            run_petl_repl(logger)
    except Exception as main_exception:
        logger.error(f"Unhandled exception occurred: {main_exception}, {traceback.format_exc()}")


if __name__ == "__main__":
    main()
