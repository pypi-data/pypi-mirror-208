import ast
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import click

from pydoclint.violation import Violation
from pydoclint.visitor import Visitor


@click.command(
    context_settings={'help_option_names': ['-h', '--help']},
    # While Click does set this field automatically using the docstring, mypyc
    # (annoyingly) strips them, so we need to set it here too.
    help='Yes',
)
@click.option(
    '-s',
    '--src',
    type=str,
    help='The source code to check',
)
@click.option(
    '-th',
    '--check-type-hint',
    type=bool,
    show_default=True,
    default=True,
    help='Whether to check type hints in docstrings',
)
@click.option(
    '-ao',
    '--check-arg-order',
    type=bool,
    show_default=True,
    default=True,
    help='Whether to check docstring argument order against function signature',
)
@click.option(
    '-scsd',
    '--skip-checking-short-docstrings',
    type=bool,
    show_default=True,
    default=True,
    help='If True, skip checking if the docstring only has a short summary.',
)
@click.option(
    '-scr',
    '--skip-checking-raises',
    type=bool,
    show_default=True,
    default=False,
    help='If True, skip checking docstring "Raises" section against "raise" statements',
)
@click.argument(
    'paths',
    nargs=-1,
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=True,
        readable=True,
        allow_dash=True,
    ),
    is_eager=True,
)
@click.pass_context
def main(
        ctx: click.Context,
        src: Optional[str],
        paths: Tuple[str, ...],
        check_type_hint: bool,
        check_arg_order: bool,
        skip_checking_short_docstrings: bool,
        skip_checking_raises: bool,
) -> None:
    """Command-line entry point of pydoclint"""
    ctx.ensure_object(dict)

    if paths and src is not None:
        click.echo(
            main.get_usage(ctx)
            + "\n\n'paths' and 'src' cannot be passed simultaneously."
        )
        ctx.exit(1)

    if not paths and src is None:
        click.echo(
            main.get_usage(ctx) + "\n\nOne of 'paths' or 'src' is required."
        )
        ctx.exit(1)

    violationsInAllFiles: Dict[str, List[Violation]] = _checkPaths(
        paths=paths,
        checkTypeHint=check_type_hint,
        checkArgOrder=check_arg_order,
        skipCheckingShortDocstrings=skip_checking_short_docstrings,
        skipCheckingRaises=skip_checking_raises,
    )

    if len(violationsInAllFiles) > 0:
        counter = 0
        for filename, violationsInThisFile in violationsInAllFiles.items():
            counter += 1
            if len(violationsInThisFile) > 0:
                if counter > 1:
                    print('')

                click.echo(click.style(filename, fg='yellow', bold=True))
                for violation in violationsInThisFile:
                    fourSpaces = '    '
                    click.echo(fourSpaces, nl=False)
                    click.echo(f'{violation.line}: ', nl=False)
                    click.echo(
                        click.style(
                            f'{violation.fullErrorCode}',
                            fg='red',
                            bold=True,
                        ),
                        nl=False,
                    )
                    click.echo(f': {violation.msg}')

        ctx.exit(1)

    ctx.exit(0)


def _checkPaths(
        paths: Tuple[str, ...],
        checkTypeHint: bool = True,
        checkArgOrder: bool = True,
        skipCheckingShortDocstrings: bool = True,
        skipCheckingRaises: bool = False,
) -> Dict[str, List[Violation]]:
    filenames: List[Path] = []

    for path_ in paths:
        path = Path(path_)
        if path.is_file():
            filenames.append(path)
        elif path.is_dir():
            filenames.extend(sorted(path.rglob('*.py')))

    allViolations: Dict[str, List[Violation]] = {}

    for filename in filenames:
        violationsInThisFile: List[Violation] = _checkFile(
            filename,
            checkTypeHint=checkTypeHint,
            checkArgOrder=checkArgOrder,
            skipCheckingShortDocstrings=skipCheckingShortDocstrings,
            skipCheckingRaises=skipCheckingRaises,
        )
        allViolations[filename.as_posix()] = violationsInThisFile

    return allViolations


def _checkFile(
        filename: Path,
        checkTypeHint: bool = True,
        checkArgOrder: bool = True,
        skipCheckingShortDocstrings: bool = True,
        skipCheckingRaises: bool = False,
) -> List[Violation]:
    with open(filename) as fp:
        src: str = ''.join(fp.readlines())

    tree: ast.Module = ast.parse(src)
    visitor = Visitor(
        checkTypeHint=checkTypeHint,
        checkArgOrder=checkArgOrder,
        skipCheckingShortDocstrings=skipCheckingShortDocstrings,
        skipCheckingRaises=skipCheckingRaises,
    )
    visitor.visit(tree)
    return visitor.violations


if __name__ == '__main__':
    main()
