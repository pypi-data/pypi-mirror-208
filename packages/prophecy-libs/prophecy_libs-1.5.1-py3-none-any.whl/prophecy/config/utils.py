import argparse
from pyhocon import ConfigFactory, ConfigTree


def parse_args():
    parser = argparse.ArgumentParser(description="Spark Application")
    parser.add_argument(
        "-C",
        "--config",
        nargs="+",
        help=(
            "Property of the config that needs to be overridden. Set a number of key-value "
            "pairs(do not put spaces before or after the = sign). Ex: -C fabricName=dev "
            'dbConnection="db.prophecy.io" dbUserName="prophecy"'
        ),
    )
    parser.add_argument(
        "-d",
        "--defaultConfFile",
        help="Full path of default hocon config file. Ex: -d dbfs:/some_path/default.json",
        default=None
    )
    parser.add_argument(
        "-f",
        "--file",
        help="Location of the hocon config file. Ex: -f /opt/prophecy/dev.json",
    )
    parser.add_argument(
        "-i",
        "--confInstance",
        help="Config instance name present in config directory. Ex.: -i default",
    )
    parser.add_argument(
        "-O",
        "--overrideJson",
        type=str,
        help="Overridden values in json format"
    )
    args = parser.parse_args()

    return args


def parse_config(args):
    if args.file is not None:
        if hasattr(args, "defaultConfFile"):
            default_config = ConfigFactory.parse_file(
                args.defaultConfFile) if args.defaultConfFile is not None else ConfigFactory.parse_string("{}")
            conf = ConfigFactory.parse_file(args.file).with_fallback(default_config)
        else:
            conf = ConfigFactory.parse_file(args.file)
    elif args.confInstance is not None:
        try:
            # python 3.7+
            import importlib.resources
            with importlib.resources.open_text(
                    "prophecy_config_instances",
                    "{instance}.json".format(instance=args.confInstance),
            ) as file:
                data = file.read()
                conf = ConfigFactory.parse_string(data)
        except:
            # python < 3.7
            import importlib.util
            config_instances_path = importlib.util.find_spec("prophecy_config_instances").submodule_search_locations[0]
            config_file_path = f"{config_instances_path}/{args.confInstance}.json"
            with open(config_file_path, 'r') as file:
                data = file.read()
                conf = ConfigFactory.parse_string(data)
    else:
        conf = ConfigFactory.parse_string("{}")

    if args.overrideJson is not None:
        # Override fields
        conf = ConfigTree.merge_configs(conf, ConfigFactory.parse_string(args.overrideJson))
    # override the file config with explicit value passed
    if args.config is not None:
        for config in args.config:
            c = config.split("=", 1)
            conf.put(c[0], c[1])

    return conf
