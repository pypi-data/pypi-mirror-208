from . import app, audit, backup, helpers, security
from .configs import Config


def main(args) -> int:
    if not hasattr(args, 'which'):
        print(
            helpers.bcolors.FAIL
            + 'Can not parse action use --help'
            + helpers.bcolors.ENDC
        )
        return 1

    if hasattr(args, 'debug') and args.debug:
        print(args)

    config = Config(working_dir=args.working_dir)

    if args.which == 'security':
        return security.cli_main(args, config)
    elif args.which == 'audit':
        return audit.cli_main(args, config)
    elif args.which == 'backup':
        return backup.cli_main(args, config)
    elif args.which == 'app':
        return app.cli_main(args, config)

    return 0
