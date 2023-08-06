from contextlib import contextmanager
import os
import sys
import time
from typing import Any, Optional

import click
import colorama  # type: ignore
from halo import Halo


_process_start_time = time.time()


class BlockLogger:
    """
    Logger class for the CLI. Supports formatting in blocks if `block_label` is provided to
    the methods. Also supports anyscale.connect style logging if `block_label` is not
    provided.
    """

    def __init__(
        self,
        log_output: bool = True,
        t0: float = _process_start_time,
        spinner_manager: Any = None,
    ) -> None:
        self.t0 = t0
        # Flag to disable all terminal output from CLILogger (useful for SDK)
        self.log_output = log_output
        self.current_block: Optional[str] = None
        self.spinner_manager = spinner_manager

    def open_block(
        self, block_label: str, block_title: Optional[str] = None, auto_close=False
    ) -> None:
        """
        Prints block title from the given block_label and sets self.current_block. "Output"
        is a generic block that does not need to follow the standard convention.

        if auto_close is set, automatically closes the block before opening a new one
        """
        if not self.log_output:
            return
        assert (
            auto_close or self.current_block is None or self.current_block == "Output"
        ), f"Block {self.current_block} is already open. Please close before opening block {block_label}."

        if auto_close:
            self.close_block()
        self.current_block = block_label
        print(
            f"{colorama.Style.BRIGHT}{colorama.Fore.CYAN}{block_title if block_title else block_label}{colorama.Style.RESET_ALL}",
            file=sys.stderr,
        )

    def close_block(self, block_label: Optional[str] = None) -> None:
        """ Closes the current block
        If a label is specified, it must match the current open block label.
        raise an AssertionError if we try to close a different block

        Prints newline so there is separation before next block is opened.
        """
        if not self.log_output:
            return
        if block_label:
            assert (
                self.current_block == block_label
            ), f"Attempting to close block {block_label}, but block {self.current_block} is currently open."
        self.current_block = None
        print(file=sys.stderr)

    @staticmethod
    def highlight(word: str) -> str:
        return f"{colorama.Style.BRIGHT}{colorama.Fore.MAGENTA}{word}{colorama.Style.RESET_ALL}"

    def zero_time(self) -> None:
        self.t0 = time.time()

    def info(self, *msg: str, block_label: Optional[str] = None) -> None:
        if not self.log_output:
            return
        if block_label:
            # Check block_label if provided.
            assert (
                self.current_block == block_label
            ), f"Attempting to log to block {block_label}, but block {self.current_block} is currently open."
            print(
                *msg, file=sys.stderr,
            )
        else:
            print(
                "{}{}(anyscale +{}){} ".format(
                    colorama.Style.BRIGHT,
                    colorama.Fore.CYAN,
                    self._time_string(),
                    colorama.Style.RESET_ALL,
                ),
                end="",
                file=sys.stderr,
            )
            print(
                *msg, file=sys.stderr,
            )

    def debug(self, *msg: str) -> None:
        if not self.log_output:
            return
        if os.environ.get("ANYSCALE_DEBUG") == "1":
            print(
                "{}{}(anyscale +{}){} ".format(
                    colorama.Style.DIM,
                    colorama.Fore.CYAN,
                    self._time_string(),
                    colorama.Style.RESET_ALL,
                ),
                end="",
            )
            print(*msg)

    def warning(self, *msg: str) -> None:
        if not self.log_output:
            return
        print(
            "{}{}[Warning]{} ".format(
                colorama.Style.NORMAL, colorama.Fore.YELLOW, colorama.Style.RESET_ALL,
            ),
            end="",
            file=sys.stderr,
        )
        print(*msg, file=sys.stderr)

    def _time_string(self) -> str:
        delta = time.time() - self.t0
        hours = 0
        minutes = 0
        while delta > 3600:
            hours += 1
            delta -= 3600
        while delta > 60:
            minutes += 1
            delta -= 60
        output = ""
        if hours:
            output += f"{hours}h"
        if minutes:
            output += f"{minutes}m"
        output += f"{round(delta, 1)}s"
        return output

    def error(self, *msg: str) -> None:
        prefix_msg = f"(anyscale +{self._time_string()})"
        self.print_red_error_message(prefix_msg, end_char="")

        print(*msg, file=sys.stderr)

    def confirm_missing_permission(self, msg):
        if self.spinner_manager:
            self.spinner_manager.stop()

        self.warning(msg)

        self.print_red_error_message(
            "[DANGER] To continue without these permissions press 'y', or press 'N' to abort.",
            end_char="",
        )

        click.confirm(
            "", abort=True,
        )

        if self.spinner_manager:
            self.spinner_manager.start()

    def print_red_error_message(self, error_msg, end_char="\n"):
        print(
            "{}{}{} {}".format(
                colorama.Style.BRIGHT,
                colorama.Fore.RED,
                error_msg,
                colorama.Style.RESET_ALL,
            ),
            end=end_char,
            file=sys.stderr,
        )


class LogsLogger(BlockLogger):
    """ This logger is used to print customer logs to STDOUT with no decoration
    """

    def log(self, msg: str):
        print(msg)

    def is_interactive_cli_enabled(self) -> bool:
        """Check if shell is interactive
        """

        default_env_var = "1" if sys.stderr.isatty() else "0"
        return os.environ.get("ANYSCALE_CLI_INTERACTIVE_UX", default_env_var) == "1"

    @contextmanager
    def spinner(self, msg: str):
        """ Create a spinner with the starting text.
        To update the text next to the spinner, set `spinner.text = "new_text"`
        The spinner will be stopped when the context is exited.
        Spinner is only enabled for interactive shell
        """

        enable_spinner = self.is_interactive_cli_enabled()

        with Halo(
            text=msg, spinner="dots", stream=sys.stderr, enabled=enable_spinner
        ) as spinner:
            yield spinner
