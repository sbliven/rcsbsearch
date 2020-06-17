"""Generates the attr modules from the schema.

This is not intended to be called directly. It is used when updating the rcsbsearch
source.
"""
import sys
import argparse
import logging
from io import StringIO

INDENTSTR = "    "


def write_class(classname, contents, docstring=None):
    def write(out, indent=0):
        out.write(INDENTSTR * indent)
        out.write(f"class {classname}:\n")
        if docstring is not None:
            out.write(INDENTSTR * (indent + 1))
            out.write(repr(docstring))
            out.write("\n")
        contents(out, indent + 1)

    return write


def write_pass():
    def write(out, indent=0):
        out.write(INDENTSTR * indent)
        out.write("pass\n")

    return write


def write_property(name, attribute, docstring=None):
    def write(out, indent=0):
        out.write(INDENTSTR * indent)
        out.write("@property\n")
        out.write(INDENTSTR * indent)
        out.write(f"def {name}():\n")
        if docstring is not None:
            out.write(INDENTSTR * (indent + 1))
            out.write(repr(docstring))
            out.write("\n")
        out.write(INDENTSTR * (indent + 1))
        out.write(f"return Attr({attribute!r})")

    return write


def main(args=None):
    parser = argparse.ArgumentParser(description="Overwrite attr module")
    parser.add_argument(
        "-v",
        "--verbose",
        help="Long messages",
        dest="verbose",
        default=False,
        action="store_true",
    )
    parser.add_argument(
        "-b", "--black", help="format with black", default=False, action="store_true"
    )
    parser.add_argument(
        "outfile",
        nargs="?",
        help="Output file",
        type=argparse.FileType("w"),
        default=sys.stdout,
    )
    args = parser.parse_args(args)

    logging.basicConfig(
        format="%(levelname)s: %(message)s",
        level=logging.DEBUG if args.verbose else logging.WARN,
    )

    file = write_class(
        "Foo",
        write_class("Bar", write_property("prop", "rcsb_prop"), docstring="a Bar"),
        docstring="a Foo",
    )

    if args.black:
        try:
            import black
        except ImportError:
            logging.error("Please install black")
            sys.exit(1)

        tmp = StringIO()
        file(tmp)
        unformated = tmp.getvalue()

        try:
            # >19.10b0
            mode = black.Mode()
        except AttributeError:
            mode = black.FileMode()
        formated = black.format_str(unformated, mode=mode)

        args.outfile.write(formated)
    else:
        file(args.outfile)


if __name__ == "__main__":
    main()
