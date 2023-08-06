from argparse import SUPPRESS, Action


class BooleanOptionalAction(Action):
    """
    Creates --[no-]option style bool options.

    Defined here since it doesn't exist in argparse in Python 3.8.

    Copied from:
    https://github.com/python/cpython/blob/c33aaa9d559398bbf2b80e891bf3ae6a716e4b8c/Lib/argparse.py#L863-L901
    """

    def __init__(
        self,
        option_strings,
        dest,
        default=None,
        type=None,  # pylint: disable=redefined-builtin
        choices=None,
        required=False,
        help=None,  # pylint: disable=redefined-builtin
        metavar=None,
    ):
        _option_strings = []
        for option_string in option_strings:
            _option_strings.append(option_string)

            if option_string.startswith("--"):
                option_string = "--no-" + option_string[2:]
                _option_strings.append(option_string)

        if help is not None and default is not None and default is not SUPPRESS:
            help += " (default: %(default)s)"

        super().__init__(
            option_strings=_option_strings,
            dest=dest,
            nargs=0,
            default=default,
            type=type,
            choices=choices,
            required=required,
            help=help,
            metavar=metavar,
        )

    def __call__(self, parser, namespace, values, option_string=None):
        if option_string in self.option_strings:
            setattr(namespace, self.dest, not option_string.startswith("--no-"))

    def format_usage(self):
        return " | ".join(self.option_strings)
