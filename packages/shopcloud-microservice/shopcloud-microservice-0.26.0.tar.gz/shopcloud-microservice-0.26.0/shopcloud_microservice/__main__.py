import argparse
import sys

from . import cli

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Microservice management',
        prog='shopcloud-microservice'
    )

    subparsers = parser.add_subparsers(help='commands', title='commands')
    parser.add_argument('--debug', '-d', help='Debug', action='store_true')
    parser.add_argument('--quit', '-q', help='Quiet', action='store_true')
    parser.add_argument('--simulate', '-s', help='Simulate the process', action='store_true')
    parser.add_argument('--secrethub-token', help='Secrethub-Token', type=str)
    parser.add_argument('--working-dir', help='Working Directory', type=str, default='.')

    parser_security = subparsers.add_parser('security', help='security')
    parser_security.add_argument(
        'action',
        const='generate',
        nargs='?',
        choices=['merge-security-pull-requests', 'ci-secrets-rolling']
    )
    parser_security.add_argument('repo', const='generate', nargs='?')
    parser_security.set_defaults(which='security')

    parser_audit = subparsers.add_parser('audit', help='audit')
    parser_audit.add_argument(
        'action',
        const='generate',
        nargs='?',
        choices=['code', 'cloud', 'app']
    )
    parser_audit.add_argument('repo', const='generate', nargs='?')
    parser_audit.set_defaults(which='audit')

    backup = subparsers.add_parser('backup', help='backup')
    backup.add_argument(
        'action',
        const='generate',
        nargs='?',
        choices=['sql-init', 'sql-list-instances', 'sql-list-databases', 'sql-download', "sql-push-to-drive", "sql-dump"]

    )
    backup.add_argument('name', const='generate', nargs='?')
    backup.set_defaults(which='backup')

    app = subparsers.add_parser('app', help='app')
    app.add_argument(
        'action',
        const='generate',
        nargs='?',
        choices=['health', 'list', 'release']

    )
    app.add_argument('name', const='generate', nargs='?')
    app.set_defaults(which='app')

    args = parser.parse_args()
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)
    rc = cli.main(args)
    if rc != 0:
        sys.exit(rc)
