"""
Prints tag & commit info (SHA & tag) for a Git repository.

"""
import click
from pyriksprot.gitchen import GitInfo
from pyriksprot.utility import write_yaml

# pylint: disable=too-many-arguments, unused-argument


@click.command()
@click.argument('folder', type=click.STRING)
@click.option('--tag', type=click.STRING, help='Print info for specified tag (default HEAD).', default=None)
@click.option(
    '--key',
    type=click.Choice(["tag", "ref", "sha", "sha8", "tag_url", "commit_url"], case_sensitive=False),
    help='Prints value for given key',
    default=None,
)
def main(folder: str = None, tag: str = None, key: str = None):
    data: dict = GitInfo(folder).tag_info(source='workdir', tag=tag)
    if key:
        print(data.get(key, ""))
    else:
        write_yaml(data=data, file="-")


if __name__ == "__main__":
    main()
