from cit.core.cmd_args.parse_args import ParseArgs
from cit.core.repository import Repository

def main():
    parse_args = ParseArgs()
    parse_args.add_init_command()\
            .add_add_command()\
            .add_commit_command()\
            .add_checkout_command()\
            .add_branch_command()\
            .add_log_command()\
            .add_status_command()
    try:
        repo = Repository()
        command = parse_args.parse_cmd()
        command.execute(repo=repo, args=parse_args.parse())
    except Exception as e:
        print(f"Error: {e}")