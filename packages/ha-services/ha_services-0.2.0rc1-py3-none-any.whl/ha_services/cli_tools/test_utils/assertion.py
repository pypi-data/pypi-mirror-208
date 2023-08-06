from click._compat import strip_ansi as strip_ansi_codes
from rich.console import Console

from ha_services.cli_tools.richt_utils import PanelPrinter


def assert_in(content: str, parts: tuple[str, ...], strip_ansi=True) -> None:
    """
    Check if all parts exist in content
    """
    if strip_ansi:
        content = strip_ansi_codes(content)

    missing = [part for part in parts if part not in content]
    if missing:
        console = Console()
        console.rule(title='assert_in(): Content start', characters='∨')
        print(content)
        console.rule(title='assert_in(): Content end', characters='∧')

        pp = PanelPrinter()
        pp.print_panel(
            title='assert_in(): [red]Missing parts:',
            content='\n\n'.join(missing),
        )
        raise AssertionError(f'assert_in(): {len(missing)} parts not found in content, see output above')


def assert_startswith(text, prefix):
    if not text.startswith(prefix):
        raise AssertionError(f'{text!r} does not starts with: {prefix!r}')
