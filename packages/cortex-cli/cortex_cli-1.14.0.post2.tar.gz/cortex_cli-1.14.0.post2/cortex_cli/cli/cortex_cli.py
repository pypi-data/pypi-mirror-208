from plumbum.cli import Application

# Setup custom import schema
# cortex_cli.cli
# cortex_cli.core
import os
import sys
current = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.dirname(os.path.dirname(current)))

import cortex_cli
from cortex_cli.cli.configure import ConfigureCli
from cortex_cli.cli.clients import ClientsCli
from cortex_cli.cli.generic_get import GetCli
from cortex_cli.cli.inferences import InferencesCli
from cortex_cli.cli.models import ModelsCli
from cortex_cli.cli.pipelines import PipelinesCli


class CortexCli(Application):
    VERSION = cortex_cli.__version__


def main():
    CortexCli.subcommand('configure', ConfigureCli)
    CortexCli.subcommand('clients', ClientsCli)
    CortexCli.subcommand('inferences', InferencesCli)
    CortexCli.subcommand('models', ModelsCli)
    CortexCli.subcommand('pipelines', PipelinesCli)

    CortexCli.run()


if __name__ == '__main__':
    main()
