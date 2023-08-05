import click
from .magic import get_mimetype_by_filename

@click.command()
@click.option("--disable-magic", is_flag=True, help="Don't use libmagic.")
@click.option("--disable-file-command", is_flag=True, help="Don't use file command.")
@click.option("--disable-puremagic", is_flag=True, help="Don't use puremagic.")
@click.argument("filename", nargs=-1)
def main(filename, disable_magic, disable_file_command, disable_puremagic):
    """Get file's mimetype information.
    """
    filenames = filename
    for filename in filenames:
        mimetype = get_mimetype_by_filename(
            filename,
            enable_using_magic=not disable_magic,
            enable_using_file_command=not disable_file_command,
            enable_using_puremagic=not disable_puremagic,
            )
        print("{filename}: {mimetype}".format(filename=filename, mimetype=mimetype))

if __name__ == "__main__":
    main()
