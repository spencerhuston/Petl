import io
from contextlib import redirect_stdout
from datetime import datetime
from typing import Optional, List

from petllang.phases.interpreter.definitions.value import PetlValue, NoneValue
from petllang.phases.interpreter.environment import InterpreterEnvironment
from petllang.phases.interpreter.interpreter import TreeWalkInterpreter, load_builtins
from petllang.phases.lexer.definitions.token_petl import Token
from petllang.phases.lexer.lexer import Lexer
from petllang.phases.parser.defintions.expression import Expression, UnknownExpression
from petllang.phases.parser.parser import Parser
from petllang.utils.log import Log
from backend.utils.server_utils import escape_ansi


async def execute_petl_script_direct(petl_input: str) -> str:
    debug = False
    logger: Log = Log(debug)

    stdout_buffer = io.StringIO()
    with redirect_stdout(stdout_buffer):
        program_return_value: PetlValue = execute_petl_script(petl_input, debug, logger)

    result = escape_ansi(stdout_buffer.getvalue())
    if not isinstance(program_return_value, NoneValue):
        result += program_return_value.to_string()

    logger.debug(f"Interpreter Output:\n{result}\n")
    return result


def execute_petl_script(petl_raw_str: str,
                        debug: bool,
                        logger: Log,
                        environment: Optional[InterpreterEnvironment] = None) -> Optional[PetlValue]:
    start: datetime = datetime.now()

    lexer: Lexer = Lexer(debug)
    tokens: Optional[List[Token]] = lexer.scan(petl_raw_str)

    result_value: Optional[PetlValue] = None

    if tokens and not lexer.logger.errors_occurred():
        parser: Parser = Parser(debug)
        root: Expression = parser.parse(tokens)

        if root and not parser.logger.errors_occurred() and not isinstance(root, UnknownExpression):
            interpreter: TreeWalkInterpreter = TreeWalkInterpreter(debug)

            if not environment:
                environment = InterpreterEnvironment()
            environment = load_builtins(parser.builtins, environment)

            result_value = interpreter.interpret(root, environment)

            logger.debug(f"DEBUG: {result_value.to_string()}")
            end: datetime = datetime.now()
            delta = end - start
            logger.debug(str(delta.total_seconds()))

    return result_value
