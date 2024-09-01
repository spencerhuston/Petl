import sys
import traceback
from typing import Dict, Any, Optional, List

from src.phases.environment import InterpreterEnvironment
from src.phases.interpreter import Interpreter, load_builtins
from src.phases.lexer import Lexer
from src.phases.parser import Parser
from src.semantic_defintions.petl_expression import Expression, UnknownExpression
from src.semantic_defintions.petl_value import PetlValue
from src.tokens.petl_token import Token
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
    if file_path.endswith(".petl"):
        with open("programs/" + file_path, "r") as petl_file:
            petl_file_str = petl_file.read()
            logger.debug_block("RAW SCRIPT", petl_file_str)
    else:
        logger.error(f"Petl script {file_path} requires extension \x1b[3m.petl\x1b[0m")
    return petl_file_str


def execute_petl_script(petl_raw_str: str, debug: bool) -> bool:
    lexer: Lexer = Lexer(debug)
    tokens: Optional[List[Token]] = lexer.scan(petl_raw_str)
    if tokens and not lexer.logger.errors_occurred():
        parser: Parser = Parser(debug)
        root: Expression = parser.parse(tokens)
        if root and not parser.logger.errors_occurred() and not isinstance(root, UnknownExpression):
            interpreter: Interpreter = Interpreter(debug)
            environment: InterpreterEnvironment = load_builtins(parser.builtins)
            result_value: PetlValue = interpreter.interpret(root, environment)
            logger.debug(result_value.to_string())
    else:
        return False


def run_petl_repl(logger: Log):
    banner_str = "=" * 9
    logger.info(f"{banner_str}\nPetl REPL\n{banner_str}")
    interpreter_input: str = ""
    ended_with_slash: bool = False
    while True:
        repl_input = input("> " if not ended_with_slash else "> \t")
        ended_with_slash = False
        if repl_input == "quit":
            logger.info("Quitting REPL...")
            break
        elif not repl_input:
            continue

        if repl_input.endswith("\\"):
            repl_input = repl_input.replace("\\", "")
            interpreter_input += repl_input + "\n"
            ended_with_slash = True
        elif repl_input.endswith(";"):
            repl_input = repl_input.replace(";", "")
            interpreter_input += repl_input + "\n"
        else:
            interpreter_input += repl_input
            execute_petl_script(interpreter_input, logger.debug_enabled())
            interpreter_input = ""


if __name__ == "__main__":
    arguments: Dict[str, Any] = parse_arguments()
    debug: bool = arguments["debug"]

    logger: Log = Log(debug)
    try:
        if arguments["file"]:
            petl_raw_str = read_petl_file(arguments["file"], logger)
            if petl_raw_str:
                execute_petl_script(petl_raw_str, debug)
        else: # start REPL
            run_petl_repl(logger)
    except Exception as main_exception:
        logger.error(f"Unhandled exception occurred: {main_exception}, {traceback.format_exc()}")
