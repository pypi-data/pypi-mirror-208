# Copyright Formic Technologies 2023
import re
import sys
from subprocess import check_output  # nosec B404

BRANCH_TYPES_MAPPING = {
    'feature': 'feature:',
    'bugfix': 'fix:',
    'hotfix': 'fix:',
}
BRANCH_NAME_PATTERN = (
    rf'^(?P<branch_type>{"|".join(BRANCH_TYPES_MAPPING.keys())})\/'
    '(?:(?P<ticket_name>[A-Z]+-[1-9][0-9]*)|(?P<slug_name>[a-z0-9]+(?:[-]+[a-z0-9]+)*))$'
)


def get_valid_prefix(branch_name: str) -> str:
    """
    Calculates valid prefix for commit based on branch name.
    Throws exceptions if branch name is invalid.
    """
    match = re.match(BRANCH_NAME_PATTERN, branch_name)

    if match:
        matched_groups = match.groupdict()
        if prefix := matched_groups.get('ticket_name'):
            return prefix
        elif matched_groups.get('slug_name'):
            return BRANCH_TYPES_MAPPING[matched_groups['branch_type']]

    print('Invalid branch name!')
    raise SystemExit(1)


def update_commit_message(commit_message_path: str, prefix: str) -> int:
    """Opens file with commit message and adds prefix if needed"""
    with open(commit_message_path, 'r+') as f:
        commit_message = f.read()
        expected_prefix = commit_message.split()[0]
        if expected_prefix != prefix:
            f.seek(0)
            f.write(f'{prefix} {commit_message}')

        return 0


def main():
    commit_message_file_path = sys.argv[1]
    branch_name = check_output(('git', 'rev-parse', '--abbrev-ref', 'HEAD')).decode().strip()  # nosec B603
    commit_prefix = get_valid_prefix(branch_name)
    status_code = update_commit_message(
        commit_message_path=commit_message_file_path,
        prefix=commit_prefix,
    )
    return status_code


if __name__ == '__main__':
    raise SystemExit(main())
