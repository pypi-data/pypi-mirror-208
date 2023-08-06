import os
import subprocess
import click


class SingletonClass(object):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(SingletonClass, cls).__new__(cls)
        return cls.instance


singleton = SingletonClass()
singleton.PROJECT_ROOT_DIR = os.path.dirname(__file__)

@click.group()
def main():
    """Claudia says hi! Please choose a command to perform an action. A command can have multiple sub-commands and options. Use '--help' option for more information."""


@main.group()
@click.pass_context
def run(context):
    """This command allows you to run XRPL automated tests."""


@main.group()
@click.pass_context
def build(context):
    """TO BE IMPLEMENTED: This command allows you to build Rippled on demand. Please choose your options wisely."""


@main.group()
@click.pass_context
def network(context):
    """TO BE IMPLEMENTED: This command allows you to build a local network. Please choose your options wisely."""


@run.command()
@click.pass_context
@click.option('--client_type', default='websocket',
              help="The type of client to be used. Allowed values are 'websocket' and 'jsonrpc' and is defaulted to 'websocket'. More information: \n\nhttps://xrpl.org/get-started-using-http-websocket-apis.html#differences-between-json-rpc-and-websocket")
@click.option('--network', default='local',
              help="The type of client to be used. Allowed values are 'websocket' and 'jsonrpc' and is defaulted to 'local'. More information: \n\nhttps://xrpl.org/get-started-using-http-websocket-apis.html#differences-between-json-rpc-and-websocket")
@click.option('--tag', default='smoke',
              help="Tag name of the all the tests to be included in the test run. Allowed values are 'smoke', 'regression' and 'time_intensive' and is defaulted to 'smoke'. More information: \n\nhttps://behave.readthedocs.io/en/latest/tag_expressions.html")
@click.option('--feature', default='payments',
              help="Feature file to be used for the test run. Allowed values are 'payments', 'trustline', 'nft_mint_burn', and 'all' and is defaulted to 'payments''. More information: \n\nhttps://behave.readthedocs.io/en/latest/tutorial.html?highlight=feature#feature-files")
def python(context, client_type, network, tag, feature):
    """Launch XRPL Automated tests using the Python client. Please choose your options wisely."""
    set_to_py_wd()
    try:
        set_python_launch_vars(network, client_type)
        load_feature_files()
        launch_behave(tag, feature)
        unload_feature_files()
    except Exception as e:
        set_to_project_root_wd()
        raise e


@run.command()
@click.pass_context
@click.option('--network', default='local',
              help="The type of client to be used. Allowed values are 'websocket' and 'jsonrpc' and is defaulted to 'local'. More information: \n\nhttps://xrpl.org/get-started-using-http-websocket-apis.html#differences-between-json-rpc-and-websocket")
@click.option('--tag', default='smoke',
              help="Tag name of the all the tests to be included in the test run. Allowed values are 'smoke', 'regression' and 'time_intensive' and is defaulted to 'smoke'. More information: \n\nhttps://behave.readthedocs.io/en/latest/tag_expressions.html")
@click.option('--feature', default='payments',
              help="Feature file to be used for the test run. Allowed values are 'payments', 'trustline', 'nft_mint_burn', and 'all' and is defaulted to 'payments''. More information: \n\nhttps://behave.readthedocs.io/en/latest/tutorial.html?highlight=feature#feature-files")
@click.option('--invalidate_cache', default='false',
              help="Forces ignoring cache, and reinstalling dependencies. Allowed values are 'true' and 'false' and is defaulted to 'false'.")
def javascript(context, network, tag, feature, invalidate_cache):
    """Launch XRPL Automated tests using the Javascript client. Please choose your options wisely."""
    set_to_js_wd()
    try:
        if invalidate_cache != 'false':
            invalidate_cache_and_rebuild()
        elif not os.path.isdir('./node_modules'):
            first_time_build()
        set_javascript_launch_vars(network)
        load_feature_files()
        launch_cucumber(tag, feature)
        unload_feature_files()
        set_to_project_root_wd()
    except Exception as e:
        set_to_project_root_wd()
        raise e


@run.command()
@click.pass_context
@click.argument("text")
def customcommand(context, text):
    """Run a debug command"""
    click.echo("Running command: {}".format(text))
    subprocess.call(text, shell=True)


def invalidate_cache_and_rebuild():
    print("Invalidating cache...")
    os.popen('rm -rf ./node_modules')
    install_js_dependencies_if_needed()


def first_time_build():
    print("Need to install missing dependencies. It is a one time action. Please wait...")
    install_js_dependencies_if_needed()


def set_python_launch_vars(network, client_type):
    if network == "local":
        if client_type == "websocket":
            connectionScheme = "ws"
            connectionURL = "127.0.0.5:6001"
            connectionType = "websocket"
        elif client_type == "jsonrpc":
            connectionScheme = "http"
            connectionURL = "127.0.0.5:5001"
            connectionType = "jsonrpc"
        else:
            raise Exception("{} is not a valid connectionType".format(client_type))
    elif network == "devnet":
        if client_type == "websocket":
            connectionScheme = "wss"
            connectionURL = "s.devnet.rippletest.net:51233"
            connectionType = "websocket"
        elif client_type == "jsonrpc":
            connectionScheme = "https"
            connectionURL = "s.devnet.rippletest.net:51234"
            connectionType = "jsonrpc"
        else:
            raise Exception("{} is not a valid connectionType".format(client_type))
    elif network == "testnet":
        if client_type == "websocket":
            connectionScheme = "wss"
            connectionURL = "s.altnet.rippletest.net:51233"
            connectionType = "websocket"
        elif client_type == "jsonrpc":
            connectionScheme = "https"
            connectionURL = "s.altnet.rippletest.net:51234"
            connectionType = "jsonrpc"
        else:
            raise Exception("{} is not a valid connectionType".format(client_type))
    else:
        raise Exception("{} is not a valid network".format(network))

    os.environ['CONNECTION_SCHEME'] = connectionScheme
    os.environ['CONNECTION_URL'] = connectionURL
    os.environ['CONNECTION_TYPE'] = connectionType
    click.echo("Setting CONNECTION_SCHEME='{}', CONNECTION_URL='{}' and CONNECTION_TYPE='{}'".format(connectionScheme,
                                                                                                     connectionURL,
                                                                                                     connectionType))


def set_javascript_launch_vars(network):
    if network == "local":
        connectionScheme = "ws"
        connectionURL = "127.0.0.5:6006"
        connectionType = "websocket"
    elif network == "devnet":
        connectionScheme = "wss"
        connectionURL = "s.devnet.rippletest.net:51233"
        connectionType = "websocket"
    elif network == "testnet":
        connectionScheme = "wss"
        connectionURL = "s.altnet.rippletest.net:51233"
        connectionType = "websocket"
    else:
        raise Exception("{} is not a valid network".format(network))

    os.environ['CONNECTION_SCHEME'] = connectionScheme
    os.environ['CONNECTION_URL'] = connectionURL
    os.environ['CONNECTION_TYPE'] = connectionType
    click.echo("Setting CONNECTION_SCHEME='{}', CONNECTION_URL='{}' and CONNECTION_TYPE='{}'".format(connectionScheme,
                                                                                                     connectionURL,
                                                                                                     connectionType))


def load_feature_files():
    unload_feature_files()
    os.popen("cp -fr ../features/*.feature ./features")


def unload_feature_files():
    os.popen("rm -rf ./features/*.feature")


def launch_behave(tag, feature):
    if feature == "all":
        command = "behave --no-skipped --tags={}".format(tag)
    else:
        command = "behave --no-skipped --tags={} ./features/{}.feature".format(tag, feature)
    os.system(command)


def install_js_dependencies_if_needed():
    command = "sh ./runSetup"
    subprocess.call(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def set_to_js_wd():
    os.chdir("{}/javascript/".format(singleton.PROJECT_ROOT_DIR))


def set_to_py_wd():
    os.chdir("{}/python/".format(singleton.PROJECT_ROOT_DIR))


def set_to_project_root_wd():
    os.chdir(singleton.PROJECT_ROOT_DIR)


def launch_cucumber(tag, feature):
    if feature == "all":
        command = "npx cucumber-js --format @cucumber/pretty-formatter --tags @{}".format(tag)
    else:
        command = "npx cucumber-js --format @cucumber/pretty-formatter --tags @{} ./features/{}.feature".format(tag,
                                                                                                                feature)
    subprocess.call(command, shell=True)


if __name__ == '__main__':
    main(context, obj={})



