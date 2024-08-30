import sys
from typing import Dict, Any, Optional, List

from src.phases.lexer import Lexer
from src.phases.parser import Parser
from src.phases.type_resolver import TypeResolver
from src.semantic_defintions.petl_expression import Expression, UnknownExpression
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
    if tokens:
        parser: Parser = Parser(debug)
        root: Expression = parser.parse(tokens)
        if root and not isinstance(root, UnknownExpression):
            resolver: TypeResolver = TypeResolver(debug)
            typed_root: Expression = resolver.resolve_expression(root)
    else:
        return False


if __name__ == "__main__":
    arguments: Dict[str, Any] = parse_arguments()
    debug: bool = arguments["debug"]

    logger: Log = Log(debug)

    if arguments["file"]:
        petl_raw_str = read_petl_file(arguments["file"], logger)
        if petl_raw_str:
            execute_petl_script(petl_raw_str, debug)
    else: # start REPL
        logger.info("Petl REPL\n=========")
