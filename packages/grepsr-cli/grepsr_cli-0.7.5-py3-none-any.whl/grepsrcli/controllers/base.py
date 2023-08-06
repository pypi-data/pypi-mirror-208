from os import system
from grepsrcli.core.message_log import Log
from cement import Controller, ex
import pkg_resources
from grepsrcli.core.sdk_setup import SDKSetup
from grepsrcli.core.config import save_config


version = pkg_resources.require("grepsr-cli")[0].version

VERSION_BANNER = """
gcli: cli tool for grepsr developers verion: %s
""" % (version)


class Base(Controller):

    class Meta:
        label = 'base'

        arguments = [
            (['-v', '--version'],
             {'action': 'version',
                'version': VERSION_BANNER}),
        ]

    def _default(self):
        self.app.args.print_help()

    @ex(help="setup SDKs for crawling",
        arguments=[
            (['-t', '--type'], {'action': 'store', 'dest': 'type'}),
            (['--dryrun'], {'action': 'store_true',  'dest': 'dryrun'}),
            (['--sdk'], {'action': 'store',  'dest': 'sdk'}),
        ]
        )
    def setup_sdk(self):

        if self.app.pargs.type is not None:
            SDKSetup(self.app.pargs.type,
                     self.app.pargs.dryrun, self.app.pargs.sdk)
        else:
            Log.error(
                "Please select the platform to setup the sdk.\nExample: gcli setup-sdk -t php|php_next")

    @ex(help="Update configuration for gcli",
        arguments=[
            (['--update'], {'action': 'store_true',  'dest': 'update'}),
        ]
        )
    def configure(self):
        if(self.app.pargs.update == True):
            save_config(update=True)
        else:
            save_config(update=False)