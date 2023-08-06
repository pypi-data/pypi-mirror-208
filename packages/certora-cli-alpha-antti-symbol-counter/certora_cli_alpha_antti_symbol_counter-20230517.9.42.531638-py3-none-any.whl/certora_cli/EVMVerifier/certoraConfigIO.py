import json5
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

import EVMVerifier.certoraContext as Ctx
import EVMVerifier.certoraContextAttribute as Attr
from EVMVerifier.certoraContextClass import CertoraContext
from Shared.certoraUtils import Mode, get_last_confs_directory, is_new_api, CertoraUserInputError
from Shared.certoraUtils import get_certora_dump_config

"""
This file is responsible for reading and writing configuration files.
"""

# logger for issues regarding the general run flow.
# Also serves as the default logger for errors originating from unexpected places.
run_logger = logging.getLogger("run")


def current_conf_to_file(context: CertoraContext) -> Dict[str, Any]:
    """
    Saves current command line options to a configuration file
    @param context: context object
    @:return the data that was written to the file (in json/dictionary form)

    We are not saving options if they were not provided (and have a simple default that cannot change between runs).
    Why?
    1. The .conf file is shorter
    2. The .conf file is much easier to read, easy to find relevant arguments when debugging
    3. Reading the .conf file is quicker
    4. Parsing the .conf file is simpler, as we can ignore the null case
    """
    def input_arg_with_value(k: Any, v: Any) -> Any:
        return v is not None and v is not False and k in Attr.all_context_keys()
    context_to_save = {k: v for k, v in vars(context).items() if input_arg_with_value(k, v)}
    all_keys = Attr.all_context_keys()

    context_to_save = dict(sorted(context_to_save.items(), key=lambda x: all_keys.index(x[0])))

    context.conf_file = f"last_conf_{datetime.now().strftime('%d_%m_%Y__%H_%M_%S')}.conf"
    out_file_path = get_last_confs_directory() / context.conf_file
    run_logger.debug(f"Saving last configuration file to {out_file_path}")
    Ctx.write_output_conf_to_path(context_to_save, out_file_path)

    # for dumping the conf file and exit user can either call with --conf_output_file or by setting the
    # environment variable CERTORA_DUMP_CONFIG. Using CERTORA_DUMP_CONFIG let the user change the conf file path
    # without tempering with .sh files.
    # NOTE: if you want to run multiple CVT instances simultaneously,
    # you should use consider the --conf_output_file flag and not CERTORA_DUMP_CONFIG.

    conf_output_file = getattr(context, Attr.CONF_ATTR.get_conf_key(), None) or get_certora_dump_config()
    if conf_output_file:
        Ctx.write_output_conf_to_path(context_to_save, Path(conf_output_file))
        sys.exit(0)
    return context_to_save


def read_from_conf_file(context: CertoraContext) -> None:
    """
    Reads data from the configuration file given in the command line and adds each key to the context namespace if the
    key is undefined there. For more details, see the invoked method read_from_conf.
    @param context: A namespace containing options from the command line, if any (context.files[0] should always be a
        .conf file when we call this method)
    """
    assert context.mode == Mode.CONF, "read_from_conf_file() should only be invoked in CONF mode"

    conf_file_name = Path(context.files[0])
    assert conf_file_name.suffix == ".conf", f"conf file must be of type .conf, instead got {conf_file_name}"

    with conf_file_name.open() as conf_file:
        configuration = json5.load(conf_file)
        read_from_conf(configuration, context)


# features: read from conf. write last to last_conf and to conf_date.
def read_from_conf(configuration: Dict[str, Any], context: CertoraContext) -> None:
    """
    Reads data from the input dictionary [configuration] and adds each key to context if the key is
    undefined there.
    Note: a command line definition trumps the definition in the file.
    If in the .conf file solc is 4.25 and in the command line --solc solc6.10 was given, sol6.10 will be used
    @param configuration: A json object in the conf file format
    @param context: A namespace containing options from the command line, if any
    """
    for option in configuration:
        if hasattr(context, option):
            val = getattr(context, option)
            if val is None or val is False:
                setattr(context, option, configuration[option])
        elif is_new_api():
            raise CertoraUserInputError(f"{option} appears in the conf file but is not a known attribute. ")

    assert 'files' in configuration, "configuration file corrupted: key 'files' must exist at configuration"
    context.files = configuration['files']  # Override the current .conf file
