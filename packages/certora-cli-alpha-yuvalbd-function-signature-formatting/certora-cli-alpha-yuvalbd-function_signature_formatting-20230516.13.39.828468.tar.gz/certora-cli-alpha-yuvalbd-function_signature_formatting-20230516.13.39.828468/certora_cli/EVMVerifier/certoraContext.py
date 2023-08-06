import argparse
import json
import logging
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any


scripts_dir_path = Path(__file__).parent.resolve()  # containing directory
sys.path.insert(0, str(scripts_dir_path))

from EVMVerifier.certoraContextClass import CertoraContext
from Shared import certoraUtils as Util
from EVMVerifier.certoraConfigIO import read_from_conf_file, current_conf_to_file
import EVMVerifier.certoraContextValidator as Cv
import EVMVerifier.certoraContextAttribute as Attr
from EVMVerifier.certoraValidateFuncs import RunSources

context_logger = logging.getLogger("context")

CLI_DOCUMENTATION_URL = 'https://docs.certora.com/en/latest/docs/prover/cli/options.html'

def collect_jar_args(context: CertoraContext) -> List[str]:
    """
    construct the jar flags. For each attribute with non-empty value in the context, we check if a jar flag was
    declared for that attribute. The jar command is a list of strings the first string is the flag (jar_flag). If
    the flag comes with a value we construct the value as the second string, based on the type of the attribute
    (Boolean, String or List of Strings)
    """
    return_list = []
    for arg in Attr.ContextAttribute:
        conf_key = arg.get_conf_key()
        attr = getattr(context, conf_key, None)
        if not attr or arg.value.jar_flag is None:
            continue
        return_list.append(arg.value.jar_flag)
        if not arg.value.jar_no_value:
            if type(attr) is list:
                return_list.append(','.join(attr))
            elif type(attr) is bool:
                return_list.append('true')
            elif type(attr) is str:
                return_list.append(attr)
            else:
                raise RuntimeError(f"{arg.name}: {arg.value.arg_type} - unknown arg type")
    return return_list


def get_local_run_cmd(context: CertoraContext) -> str:
    """
    Assembles a jar command for local run
    @param context: A namespace including all command line input arguments
    @return: A command for running the prover locally
    """
    run_args = []
    if context.mode == Util.Mode.TAC:
        run_args.append(context.files[0])
    if context.cache is not None:
        run_args.extend(['-cache', context.cache])

    if Util.is_new_api():
        jar_args = collect_jar_args(context)
        run_args.extend(jar_args)
    else:
        # DEPRECATED
        if context.settings is not None:
            for setting in context.settings:
                run_args.extend(setting.split('='))
        if context.coinbaseMode:
            run_args.append(Attr.ContextAttribute.COINBASE_MODE.value.jar_flag)
        if context.skip_payable_envfree_check:
            run_args.append("-skipPayableEnvfreeCheck")
        if context.no_calltrace_storage_information:
            run_args.append("-noCalltraceStorageInformation")
        if context.tool_output is not None:
            run_args.extend(['-json', context.tool_output])

    run_args.extend(['-buildDirectory', str(Util.get_certora_internal_dir())])
    if context.jar is not None:
        jar_path = context.jar
    else:
        certora_root_dir = Util.get_certora_root_directory().as_posix()
        jar_path = f"{certora_root_dir}/emv.jar"

    """
    This flag prevents the focus from being stolen from the terminal when running the java process.
    Stealing the focus makes it seem like the program is not responsive to Ctrl+C.
    Nothing wrong happens if we include this flag more than once, so we always add it.
    """
    java_args = ""

    if context.java_args is not None:
        java_args = f"{context.java_args} {java_args}"

    return " ".join(["java", java_args, "-jar", jar_path] + run_args)


def __get_argparser() -> argparse.ArgumentParser:

    def formatter(prog: Any) -> argparse.HelpFormatter:
        return argparse.HelpFormatter(prog, max_help_position=100, width=200)
    parser = argparse.ArgumentParser(prog="certora-cli arguments and options", allow_abbrev=False,
                                     formatter_class=formatter,
                                     epilog="  -*-*-*   "
                                            "You can find detailed documentation of the supported options in "
                                            f"{CLI_DOCUMENTATION_URL}   -*-*-*")

    if Util.is_new_api():
        arg_groups = {i.name: parser.add_argument_group(i.value) for i in Attr.ArgGroups}
    else:
        arg_groups = \
            {i.name: parser.add_argument_group(i.value) for i in Attr.ArgGroups if
             i.name is not Attr.ArgGroups.ENV.name}

        """
        IMPORTANT: This argument group must be last!
        There is a known bug in generating the help text when adding a mutually exclusive group with all its options as
        suppressed. For details, see:
        https://stackoverflow.com/questions/60565750/python-argparse-assertionerror-when-using-mutually-exclusive-group
        """
        arg_groups[Attr.ArgGroups.ENV.name] = parser.add_mutually_exclusive_group()

    if Util.is_new_api():
        args = list(Attr.ContextAttribute)
    else:
        args = [arg for arg in Attr.ContextAttribute if (arg.value.arg_status != Attr.ArgStatus.NEW)]

    for arg in args:
        flag = arg.get_flag()
        if arg.value.group is None:
            parser.add_argument(flag, help=arg.value.help_msg, **arg.value.argparse_args)
        else:
            if arg == Attr.ContextAttribute.RULE and not Util.is_new_api():
                arg_groups[arg.value.group.name].add_argument('--rule', '--rules',
                                                              help=arg.value.help_msg, **arg.value.argparse_args)
            else:
                arg_groups[arg.value.group.name].add_argument(flag, help=arg.value.help_msg, **arg.value.argparse_args)
    return parser


def get_args(args_list: Optional[List[str]] = None) -> Tuple[CertoraContext, Dict[str, Any]]:
    if args_list is None:
        args_list = sys.argv

    """
    Compiles an argparse.Namespace from the given list of command line arguments.
    Additionally returns the prettified dictionary version of the input arguments as generated by current_conf_to_file
    and printed to the .conf file in .lastConfs.

    Why do we handle --version before argparse?
    Because on some platforms, mainly CI tests, we cannot fetch the installed distribution package version of
    certora-cli. We want to calculate the version lazily, only when --version was invoked.
    We do it pre-argparse, because we do not care bout the input validity of anything else if we have a --version flag
    """
    handle_version_flag(args_list)

    pre_arg_fetching_checks(args_list)
    parser = __get_argparser()

    # if there is a --help flag, we want to ignore all parsing errors, even those before it:
    if any(string in [arg.strip() for arg in args_list] for string in ['--help', '-h']):
        parser.print_help()
        exit(0)

    try:
        import argcomplete
        argcomplete.autocomplete(parser)
    except ImportError:
        pass

    args = parser.parse_args(args_list)
    context = CertoraContext(**vars(args))

    __remove_parsing_whitespace(args_list)
    format_input(context)

    Cv.check_mode_of_operation(context)  # Here context.mode is set

    if context.mode == Util.Mode.CONF:
        read_from_conf_file(context)

    validator = Cv.CertoraContextValidator(context)
    validator.validate()
    current_build_directory = Util.get_certora_internal_dir()
    if context.build_dir is not None and current_build_directory != context.build_dir:
        Util.reset_certora_internal_dir(context.build_dir)
        os.rename(current_build_directory, context.build_dir)

    last_conf_dir = Util.get_last_confs_directory().resolve()
    Util.safe_create_dir(last_conf_dir)

    # Store current options (including the ones read from .conf file)
    conf_options = current_conf_to_file(context)

    Cv.check_args_post_argparse(context)
    setup_cache(context)  # Here context.cache, context.user_defined_cache are set

    # Setup defaults (defaults are not recorded in conf file)
    if context.expected_file is None:
        context.expected_file = "expected.json"
    if context.run_source is None:
        context.run_source = RunSources.COMMAND.name.upper()

    context_logger.debug("parsed args successfully.")
    context_logger.debug(f"args= {context}")
    if context.check_args:
        sys.exit(0)
    return context, conf_options


def print_version() -> None:
    installed, package_name, version = Util.get_package_and_version()
    if installed:
        print(f"{package_name} {version}")
    else:
        print("local script version")


def handle_version_flag(args_list: List[str]) -> None:
    for arg in args_list:
        if arg == "--version":
            print_version()  # exits the program
            exit(0)


def __remove_parsing_whitespace(arg_list: List[str]) -> None:
    """
    Removes all whitespaces added to args by __alter_args_before_argparse():
    1. A leading space before a dash (if added)
    2. space between commas
    :param arg_list: A list of options as strings.
    """
    for idx, arg in enumerate(arg_list):
        arg_list[idx] = arg.strip().replace(', ', ',')


def __alter_args_before_argparse(args_list: List[str]) -> None:
    """
    This function is a hack so we can accept the old syntax and still use argparse.
    This function alters the CL input so that it will be parsed correctly by argparse.

    Currently, it fixes two issues:

    1. We want to accept --javaArgs '-a,-b'
    By argparse's default, it is parsed as two different arguments and not one string.
    The hack is to preprocess the arguments, replace the comma with a commaspace.

    2. A problem with --javaArgs -single_flag. The fix is to add a space before the dash artificially.

    NOTE: Must use remove_parsing_whitespace() to undo these changes on argparse.ArgumentParser.parse_args() output!
    :param args_list: A list of CLI options as strings
    """
    for idx, arg in enumerate(args_list):
        if isinstance(arg, str):
            if ',' in arg:
                args_list[idx] = arg.replace(",", ", ")
                arg = args_list[idx]
            if len(arg) > 1 and arg[0] == "-" and arg[1] != "-":  # fixes a problem with --javaArgs -single_flag
                args_list[idx] = " " + arg


def pre_arg_fetching_checks(args_list: List[str]) -> None:
    """
    This function runs checks on the raw arguments before we attempt to read them with argparse.
    We also replace certain argument values so the argparser will accept them.
    NOTE: use remove_parsing_whitespace() on argparse.ArgumentParser.parse_args() output!
    :param args_list: A list of CL arguments
    :raises CertoraUserInputError if there are errors (see individual checks for more details):
        - There are wrong quotation marks “ in use
    """
    Cv.__check_no_pretty_quotes(args_list)
    __alter_args_before_argparse(args_list)


def format_input(context: CertoraContext) -> None:
    """
    Formats the input as it was parsed by argParser. This allows for simpler reading and treatment of context
    * Removes whitespace from input
    * Flattens nested lists
    * Removes duplicate values in lists
    * Sorts values in lists in alphabetical order
    :param context: Namespace containing all command line arguments, generated by get_args()
    """
    flatten_arg_lists(context)
    __cannonize_settings(context)
    Cv.sort_deduplicate_list_args(context)


def flatten_arg_lists(context: CertoraContext) -> None:
    """
    Flattens lists of lists arguments in a given namespace.
    For example,
    [[a], [b, c], []] -> [a, b, c]

    This is applicable to all options that can be used multiple times, and each time get multiple arguments.
    For example: --assert and --link
    @param context: Namespace containing all command line arguments, generated by get_args()
    """
    for arg_name in vars(context):
        arg_val = getattr(context, arg_name)
        # We assume all list members are of the same type
        if isinstance(arg_val, list) and len(arg_val) > 0 and isinstance(arg_val[0], list):
            flat_list = Util.flatten_nested_list(arg_val)
            flat_list.sort()
            setattr(context, arg_name, flat_list)


def __cannonize_settings(context: CertoraContext) -> None:
    """
    Converts the context.settings into a standard form.
    The standard form is a single list of strings, each string contains no whitespace and represents a single setting
    (that might have one or more values assigned to it with an = sign).

    @dev - --settings are different from all other list arguments, which are formatted by flatten_list_arg(). This is
           because while settings can be inserted multiple times, each time it gets a single string argument (which
           contains multiple settings, separated by commas).

    @param context: Namespace containing all command line arguments, generated by get_args()
    """
    if not hasattr(context, 'settings') or context.settings is None:
        return

    all_settings = list()

    for setting_list in context.settings:
        # Split by commas followed by a dash UNLESS they are inside quotes. Each setting will start with a dash.
        for setting in Util.split_by_delimiter_and_ignore_character(setting_list, ", -", '"',
                                                                    last_delimiter_chars_to_include=1):

            """
            Lines below remove whitespaces inside the setting argument.
            An example for when this might occur:
            -m 'foo(uint, uint)'
            will result in settings ['-m', 'foo(uint, uint)']
            We wish to replace it to be ['-m', '-foo(uint,uint)'], without the space after the comma
            """
            setting_split = setting.strip().split('=')
            for i, setting_word in enumerate(setting_split):
                setting_split[i] = setting_word.replace(' ', '')

            setting = '='.join(setting_split)
            all_settings.append(setting)

    context.settings = all_settings


def setup_cache(context: CertoraContext) -> None:
    """
    Sets automatic caching up, unless it is disabled (only relevant in VERIFY and ASSERT modes).
    The list of contracts, optimistic loops and loop iterations are determining uniquely a cache key.
    If the user has set their own cache key, we will not generate an automatic cache key, but we will also mark it
    as a user defined cache key.

    This function first makes sure to set user_defined_cache to either True or False,
    and then if necessary, sets up the cache key value.
    """

    # we have a user defined cache key if the user provided a cache key
    context.user_defined_cache = context.cache is not None
    if not context.disable_auto_cache_key_gen and not os.environ.get("CERTORA_DISABLE_AUTO_CACHE") is not None:
        if context.mode == Util.Mode.VERIFY or context.mode == Util.Mode.ASSERT:
            if context.cache is None:
                optimistic_loop = context.optimistic_loop
                loop_iter = context.loop_iter
                files = sorted(context.files)
                context.cache = '-'.join(files) + f"-optimistic{optimistic_loop}-iter{loop_iter}"

                """
                We append the cloud env and the branch name (or None) to the cache key to make it different across
                branches to avoid wrong cloud cache collisions.
                """
                if Util.is_new_api():
                    branch = context.prover_version if context.prover_version else ''
                    context.cache += f'-{context.server}-{branch}'
                    pass
                else:
                    if context.cloud is not None:
                        context.cache += f'-cloud-{context.cloud}'
                    elif context.staging:
                        context.cache += f'-staging-{context.staging}'
                    context_logger.debug(f"setting cache key to {context.cache}")


"""
dually-defined argumentsb are command line arguments that can also be passed as a setting.
For example, we can use either '--rule law' or '--settings -rule=law'
Another example is: '--loop_iter 2' or '--settings -b=2'

The argparser does not handle the value of --settings at all. This is so that jar developers can add flags quickly
 without changing the scripts.
"""

# Note: we do not check if the argument is defined in the ArgumentParser.
val_arg_to_setting = {
    'loop_iter': 'b',
    'hashing_length_bound': 'hashingLengthBound',
    'rule_sanity': 'ruleSanityChecks',
    'multi_example': 'multipleCEX',
    'max_graph_depth': 'graphDrawLimit',
    'method': 'method',
    'smt_timeout': 't',
    'bytecode_spec': 'spec',
    'dynamic_bound': 'dynamicCreationBound',
    'tool_output': 'json'
}

val_arg_to_list_setting = {
    'bytecode_jsons': 'bytecode',
    'rule': 'rule'
}

setting_aliases = {
    'rule': 'rules',
    'rules': 'rules',
}

"""
The options below are boolean, and their default in the CVT is False. If in the future, the CVT default of an options
will change, we should remove that option from the dictionary.
"""
bool_arg_to_implicit_setting = {
    "optimistic_loop": "assumeUnwindCond",
    "multi_assert_check": "multiAssertCheck"
}

"""
The options below are boolean, their default in the CVT is False, and require to explicitly set their value to true.
If in the future, the CVT default of an options will change, we should remove that option from the dictionary.
"""
bool_arg_to_explicit_setting = {
    'short_output': 'ciMode',
    'optimistic_hashing': 'optimisticUnboundedHashing',
    "dynamic_dispatch": "dispatchOnCreated",
    "include_empty_fallback": "includeEmptyFallback"
}


def __check_single_arg_and_setting_consistency(context: CertoraContext, arg_name: str, setting_name: str,
                                               is_list_setting: bool) -> None:
    """
    We accept two syntaxes for settings: --rule or --settings -rule.
    This function checks that:
    1. The two syntaxes are consistent within the same command line (do not have contradicting values)
    2. The --settings syntax is consistent (gets a single setting -setting_name at most)
    3. If we use both the setting and the argument, warn of the redundancy

    After running this function, the value will be stored both in the settings and in context.
    The arguments in settings may now be unsorted.

    @param context: a namespace containing command line arguments
    @param arg_name: name of the argument, for example: --rule or --loop_iterations
    @param setting_name: name of the setting, for example: -rule or -b
    @raises CertoraUserInputError if there is an inconsistent use of the argument.
    """
    setting_value = None
    all_settings_vals = set()
    setting_names = [setting_name]
    if setting_name in setting_aliases:
        setting_names.append(setting_aliases[setting_name])
    if context.settings is not None:
        for setting in context.settings:
            for sname in setting_names:
                setting_match = re.search(r'^-' + sname + r'(\S*)', setting)
                if setting_match is not None:
                    curr_val = setting_match[1]
                    if curr_val == "" or curr_val == "=":
                        raise Util.CertoraUserInputError(f"No value was provided for setting {sname}")
                    if re.search(r"^=[^=\s]+", curr_val):
                        if curr_val in all_settings_vals:
                            context_logger.warning(
                                f"Used --settings -{sname} more than once with the same value: {setting}"
                            )
                        all_settings_vals.add(curr_val[1:])  # remove the leading =
                    elif not re.search(r"^\w+(=[^=\s]+)?$", curr_val):
                        # there might a setting for which this setting is a substring, like -rule and -ruleSanityChecks
                        raise Util.CertoraUserInputError(f"wrong syntax for --settings -{arg_name}: {setting}")
        if len(all_settings_vals) > 1:
            all_vals_str = ' '.join(sorted(list(all_settings_vals)))
            raise Util.CertoraUserInputError(
                f"Multiples values were given to setting {setting_name}: {all_vals_str}")
        if len(all_settings_vals) > 0:
            setting_value = list(all_settings_vals)[0]

    arg_val = getattr(context, arg_name, None)
    if arg_val is not None:
        if is_list_setting:
            arg_val = ','.join(arg_val)
        else:
            arg_val = arg_val.replace(' ', '')
            # needed in case where we have --method foo(bool,address),
            # as we include an artificial space after the comma inside the parenthesis

    if arg_val is None and setting_value is None:
        return

    # given both as an argument and as a setting
    if arg_val is not None and setting_value is not None and arg_val != setting_value:
        raise Util.CertoraUserInputError(
            f"There is a conflict between argument {arg_name} value of {arg_val} "
            f"and --settings -{setting_name} value of {setting_value}")

    if arg_val is None:  # backfill argument
        if arg_name in ['rule', 'rules']:  # this is temporary until we remove dual attributes
            list_val = [setting_value]
            setattr(context, arg_name, list_val)
        else:
            setattr(context, arg_name, setting_value)  # settings value is not None

    if setting_value is None:  # backfill settings
        settings_str = f'-{setting_name}={arg_val}'
        if context.settings is None:
            context.settings = list()
        context.settings.append(settings_str)  # it is now unsorted!


def __check_bool_arg_and_implicit_setting_consistency(context: CertoraContext, arg_name: str,
                                                      setting_name: str) -> None:
    """
    We accept two syntaxes for settings: --rule or --settings -rule.
    This function checks boolean settings, that can either appear, or not.
    This function reverts if a value is erroneously given to the boolean setting.

    If we use both the setting and the argument syntaxes, we warn of the redundancy. We also warn if the setting is
     given more than once.

    After running this function, the value will be stored both in the settings and in the argument namespace.
    The order of flags in settings may now no longer be sorted alphabetically.

    @param context: a namespace containing command line arguments
    @param arg_name: name of the argument, for example: --optimistic_loop or --rule_sanity
    @param setting_name: name of the setting, for example: -assumeUnwindCondition or -ruleSanityChecks
    @raises CertoraUserInputError if there is an inconsistent use of the argument.
    """
    setting_appeared = False
    all_warnings = set()

    if context.settings is not None:
        for setting in context.settings:
            setting_match = re.search(r'^-' + setting_name + r'(=[^=]+)?$', setting)
            if setting_match is not None:
                if '=' in setting_match[0]:
                    raise Util.CertoraUserInputError(
                        f"Boolean setting {setting_name} cannot get a value, given {setting_match[1]}")
                if setting_appeared:
                    all_warnings.add(f"Setting {setting_name} appeared more than once, this is redundant")
                else:
                    setting_appeared = True

    arg_val = getattr(context, arg_name, None)
    if arg_val is not None and not isinstance(arg_val, bool):
        raise Util.CertoraUserInputError(f"value of {arg_name} must be a boolean (true or false) (was {arg_val})")
    arg_appeared = arg_val is not None and arg_val

    if not arg_appeared and not setting_appeared:
        return

    if not arg_appeared and setting_appeared:
        setattr(context, arg_name, True)
    elif arg_appeared and not setting_appeared:  # add value to settings
        settings_str = f'-{setting_name}'
        if context.settings is None:
            context.settings = list()
        context.settings.append(settings_str)  # the settings are now no longer sorted alphabetically
    else:  # both a setting and an argument were used
        if context.mode != Util.Mode.CONF:
            all_warnings.add(f"Redundant use of argument {arg_name} and setting {setting_name}")

    for warning in all_warnings:
        context_logger.warning(warning)


def __check_bool_arg_and_explicit_setting_consistency(context: CertoraContext, arg_name: str,
                                                      setting_name: str) -> None:
    """
    We accept two syntaxes for settings: --rule or --settings -rule.
    This function checks boolean settings, that can appear with explicit value, like -ci_mode=true, or -ci_mode=false.
    We assume that by default the value of the setting is false. One can use -ci_mode=false, even though it should have
    no effect. --short_output, without any arguments, is the equivalent of -ci_mode=true.

    This function raises an exception if any of the following holds:
    1. The setting has no argument
    2. The setting has a non-boolean argument
    3. The settings appears multiple times with conflicting truth values, like --settings -ci_mode=false,-ci_mode=true
    4. The option appears, but also a setting with truth value false: --short_output --settings -ci_mode=false

    This function warns if it does not raise an exception, in each of the following redundant scenarios:
    1. The setting has truth value false
    2. We use both an option and a setting with truth value true

    After running this function, the value will be stored both in the settings and in the argument namespace.
    The order of flags in settings may now no longer be sorted alphabetically.

    @param context: a namespace containing command line arguments
    @param arg_name: name of the argument, for example: --optimistic_loop or --rule_sanity
    @param setting_name: name of the setting, for example: -assumeUnwindCondition or -ruleSanityChecks
    @raises CertoraUserInputError if there is an inconsistent use of the argument.
    """
    setting_truth_val = None
    all_warnings = set()

    if context.settings is not None:
        for setting in context.settings:
            setting_match = re.search(r'^-' + setting_name + r'(=[^=]+)?$', setting)
            if setting_match is not None:
                setting_expr = setting_match[0]
                if '=' not in setting_expr:
                    raise Util.CertoraUserInputError(
                        f"Setting {setting_name} must get a boolean value: {setting_name}=true/false")
                else:
                    curr_truth_val = setting_match[0].split('=')[1].lower()
                    if curr_truth_val == 'true':
                        if setting_truth_val is None:
                            setting_truth_val = True
                        elif setting_truth_val:
                            all_warnings.add(f"setting {setting_name} was given the same value more than once: true")
                        else:
                            raise Util.CertoraUserInputError(
                                f"setting {setting_name} was given two conflicting values: true and false")
                    elif curr_truth_val == 'false':
                        if setting_truth_val is None:
                            setting_truth_val = False
                        elif not setting_truth_val:
                            all_warnings.add(f"setting {setting_name} was given the same value more than once: false")
                        else:
                            raise Util.CertoraUserInputError(
                                f"setting {setting_name} was given two conflicting values: true and false")
                    else:
                        raise Util.CertoraUserInputError(
                            f"Setting {setting_name} must get a boolean value: {setting_name}=true/false")

    arg_val = getattr(context, arg_name, None)
    if arg_val is not None and not isinstance(arg_val, bool):
        raise Util.CertoraUserInputError(f"value of {arg_name} must be a boolean (true or false) (was {arg_val})")

    arg_appeared = arg_val is not None and arg_val

    if not arg_appeared and setting_truth_val is None:
        return

    if not arg_appeared and setting_truth_val is not None:  # Add value to context
        setattr(context, arg_name, setting_truth_val)
    elif arg_appeared and setting_truth_val is None:  # add value to settings
        settings_str = f'-{setting_name}=true'
        if context.settings is None:
            context.settings = list()
        context.settings.append(settings_str)  # the settings are now no longer sorted alphabetically
    else:  # both a setting and an argument were used
        if not setting_truth_val:
            raise Util.CertoraUserInputError(f"{arg_name} and --setting -{setting_name}=false conflict each other")
        if context.mode != Util.Mode.CONF:
            all_warnings.add(f"Redundant use of argument {arg_name} and setting {setting_name} with value false")

    for warning in all_warnings:
        context_logger.warning(warning)


def check_arg_and_setting_consistency(context: CertoraContext) -> None:
    """
    Check consistency for all dually-defined arguments.
    An argument is consistent if it has at most a single value.
    If an argument is defined both as a command-line argument and inside settings, we warn the user.
    At the end of this functions, all the dually-defined argument values will appears in both the argument namespace and
     inside the settings list in the namespace.
    context.settings will be sorted in ascending order.
    @param context: a namespace containing command line arguments
    @raises CertoraUserInputError if there is a dually-defined argument.
    """
    for (argument, setting) in val_arg_to_setting.items():
        __check_single_arg_and_setting_consistency(context, argument, setting, False)

    for (argument, setting) in val_arg_to_list_setting.items():
        __check_single_arg_and_setting_consistency(context, argument, setting, True)

    for (argument, setting) in bool_arg_to_implicit_setting.items():
        __check_bool_arg_and_implicit_setting_consistency(context, argument, setting)

    for (argument, setting) in bool_arg_to_explicit_setting.items():
        __check_bool_arg_and_explicit_setting_consistency(context, argument, setting)

    if context.settings is not None:
        context.settings.sort()

def write_output_conf_to_path(json_content: Dict[str, Any], path: Path) -> None:
    """
    Write the json object to the path
    @param json_content: the json object
    @param path: the location of the output path
    @:return: None
    """
    with path.open("w+") as out_file:
        json.dump(json_content, out_file, indent=4, sort_keys=True)


def handle_flags_in_args(args: List[str]) -> None:
    """
    For argparse flags are strings that start with a dash. Some arguments get flags as value.
    The problem is that argparse will not treat the string as a value but rather as a new flag. There are different ways
    to prevent this. One way that was used in the past in certoraRun was to surround the string value with single
    quotes, double quotes or both. This technique complicates the value syntax and is error prune. A different technique
    is to precede the dash with a white space. That is something the tool can do for the user. In addition, if the user
    did add quotes (single or double) around a value they will be removed. Examples:

        --java_args '-d'
        --java_args "-d"
        --java_args '"-d"'

    Will all be converted to " -d"

    """

    if not Util.is_new_api():
        return

    all_flags = list(map(lambda member: member.get_flag(), Attr.ContextAttribute))

    def surrounded(string: str, char: str) -> bool:
        if len(string) < 2:
            return False
        return string[0] == char and string[-1] == char

    for index, arg in enumerate(args):
        if arg in all_flags:
            continue

        while True:
            if arg and (surrounded(arg, '\'') or surrounded(arg, '\"')):
                arg = arg[1:-1]
            else:
                break
        if len(arg) > 0 and arg[0] == '-':
            arg = f" {arg}"
        if arg != args[index]:
            args[index] = arg


def is_staging(context: CertoraContext) -> bool:
    if Util.is_new_api():
        if context.server is None:
            return False
        return context.server.upper() == Util.SupportedServers.STAGING.name
    else:
        return context.staging is not None
