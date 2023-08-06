import re
import textwrap
from pathlib import Path
from typing import Dict, Tuple, List

import sqlparse
from typing_extensions import TypeAlias

DirectivesType: TypeAlias = Dict[str, str]
LeadingCommentType: TypeAlias = str
SqlType: TypeAlias = str


# -- depends: 1 2
def parse_metadata_from_sql_comments(
    s: str = None, directive_names: List[str] = None
) -> Tuple[DirectivesType, LeadingCommentType, SqlType]:
    comment_or_empty = re.compile(r"^(\s*|\s*--.*)$").match
    directive_pattern = re.compile(
        r"^\s*--\s*({})\s*:\s*(.*)$".format("|".join(map(re.escape, directive_names)))
    )

    lineending = re.search(r"\n|\r\n|\r", s + "\n").group(0)  # type: ignore
    lines = iter(s.split(lineending))
    directives = {}  # type: DirectivesType
    leading_comments = []
    sql = []
    for line in lines:
        match = directive_pattern.match(line)
        if match:
            k, v = match.groups()
            if k in directives:
                directives[k] += f" {v}"
            else:
                directives[k] = v
        elif comment_or_empty(line):
            decommented = line.strip().lstrip("--").strip()
            leading_comments.append(decommented)
        else:
            sql.append(line)
            break
    sql.extend(lines)
    return (
        directives,
        textwrap.dedent(lineending.join(leading_comments)),
        lineending.join(sql),
    )


def read_sql_migration_metadata(
    file: Path = None, directive_names: List[str] = None
) -> Tuple[DirectivesType, LeadingCommentType, List[str]]:
    # Credit: yoyo-migration
    directives = {}  # type: DirectivesType
    leading_comment = ""
    statements = []
    if file.exists():
        with open(file, encoding="UTF-8") as f:
            statements = sqlparse.split(f.read())
            if statements:
                (
                    directives,
                    leading_comment,
                    sql,
                ) = parse_metadata_from_sql_comments(
                    s=statements[0], directive_names=directive_names
                )
                statements[0] = sql
    statements = [s for s in statements if s.strip()]
    return directives, leading_comment, statements
