from typing import List, Dict, Union

import argunparse


def to_arg_unparse(
    argunparser_kwargs: Dict = None,
    command: str = None,
    sub_command: str = None,
    options: Union[Dict, List] = None,
    arguments: List = None,
) -> List[str]:
    """
    Usage:
    to_arg_unparse(command="cmd", sub_command="sub", options={'foo':True, 'bar':'baz}, args=['file.txt'])
    > cmd sub --foo --bar=baz file.txt

    to_arg_unparse(command="cmd", sub_command="sub", options=['foo', True, 'bar', 'baz', 'bar', 'baz'], args=['file.txt'])
    > cmd sub --foo --bar=baz --bar=baz2 file.txt

    """
    unparser = argunparse.ArgumentUnparser(**(argunparser_kwargs or {}))

    data = list()
    if isinstance(options, Dict):
        data = unparser.unparse_options_and_args(options, arguments, to_list=True)
    elif isinstance(options, List):
        # Convert options in list of tuple
        it = iter(options)
        for k, v in list(zip(it, it)):
            if k is None:
                continue

            if isinstance(v, bool) and v is True:
                data.append(f"--{k}")
            elif isinstance(v, bool) and v is False:
                pass
            elif not isinstance(v, bool) and v is not None:
                data.append(f"--{k}={v}")

        data.extend(arguments or [])

    data = [command, sub_command] + data
    return list(filter(lambda x: x is not None, iter(data)))
