import argparse
import logging
import sys
from pathlib import Path

from prometheus_client import write_to_textfile

from backup_github.backup import Backup
from backup_github.metrics import git_size, meta_size, registry, success, time
from backup_github.parse_args import parse_args

logging.basicConfig(level=logging.INFO)


def main():
    parsed_args = None
    try:
        parsed_args = parse_args(sys.argv[1:])
        backup = Backup(
            parsed_args.token,
            parsed_args.organization,
            parsed_args.output_dir,
            parsed_args.repository,
        )
        logging.info("Start backup of repos content")
        backup.backup_repositories()
        logging.info("Finish backup of repos content")
        if parsed_args.members or parsed_args.all:
            logging.info("Start backup of members")
            backup.backup_members()
            logging.info("Finish backup of members")
        if parsed_args.issues or parsed_args.all:
            logging.info("Start backup of issues")
            backup.backup_issues()
            logging.info("Finish backup of issues")
        if parsed_args.pulls or parsed_args.all:
            logging.info("Start backup of pulls")
            backup.backup_pulls()
            logging.info("Finish backup of pulls")
        success.set(1)
    except argparse.ArgumentError as e:
        logging.error(e.message)
        success.set(0)
    except AttributeError as e:
        logging.error(e)
        success.set(0)
    finally:
        time.set_to_current_time()
        meta_size.set(
            sum(p.stat().st_size for p in Path(parsed_args.output_dir).rglob("*"))
            - git_size._value.get()
        )
        write_to_textfile("backup_github.prom", registry)


if __name__ == "__main__":
    main()
