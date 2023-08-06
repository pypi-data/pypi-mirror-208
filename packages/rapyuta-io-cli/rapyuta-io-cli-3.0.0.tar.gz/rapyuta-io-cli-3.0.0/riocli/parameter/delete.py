# Copyright 2021 Rapyuta Robotics
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import click
from rapyuta_io.utils.rest_client import HttpMethod

from riocli.parameter.utils import _api_call


@click.command('delete')
@click.option('-f', '--force', '--silent', 'silent', is_flag=True, default=False,
              help="Skip confirmation")
@click.argument('tree', type=click.STRING)
def delete_configurations(tree: str, silent: bool = False) -> None:
    """
    Deletes the Configuration Parameter Tree.
    """
    click.secho('Configuration Parameter {} will be deleted'.format(tree))

    if not silent:
        click.confirm('Do you want to proceed?', default=True, abort=True)

    try:
        data = _api_call(HttpMethod.DELETE, name=tree)
        if data.get('data') != 'ok':
            raise Exception('Something went wrong!')

    except IOError as e:
        click.secho(str(e.__traceback__), fg='red')
        click.secho(str(e), fg='red')
        raise SystemExit(1)
