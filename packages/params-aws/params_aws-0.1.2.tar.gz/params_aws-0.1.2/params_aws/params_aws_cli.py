import click
from params_aws import params_aws
from params_aws.model import DBConfig, GGAPIConfig, HashID
import os
import traceback
from asyncio.log import logger
import uuid
import json

DEFAULT_EDITOR = "/usr/bin/nano"
KNOWN_TYPES = [DBConfig.__name__, GGAPIConfig.__name__, HashID.__name__]

@click.group()
def cli():
  pass

@cli.command(help="Get known types")
def types():
  for known_type in KNOWN_TYPES:
    click.echo(known_type)

@cli.command(help="Get all names at root path")
def names():
  names = params_aws.get_parameter_names()
  for name in names:
    click.echo(name)

@cli.command(help="Get raw secret value")
@click.argument('name', nargs=1)
def get_value(name):
  click.echo(params_aws.get_parameter_value(name=name))


@cli.command(help="Get secret value")
@click.argument('name', nargs=1)
@click.argument('model', nargs=1)
def get(name, model):
  if model not in KNOWN_TYPES:
    click.echo(f"Unknown type: {model}")
    exit(-1)

  pd_class = globals()[model]

  param_value = params_aws.get_parameter(name=name, modelType=pd_class)

  click.echo(param_value)

def _open_file(path: str):
  import subprocess
  subprocess.run([DEFAULT_EDITOR, path], check=True)

@cli.command(help="Put validated secret value")
@click.argument('name', nargs=1, type=str)
@click.argument('model', nargs=1, type=str)
def put(name, model):
  if model not in KNOWN_TYPES:
    click.echo(f"Unknown type: {model}")
    exit(-1)

  pd_class = globals()[model]
  
  param_obj = params_aws.get_parameter(name, pd_class, cached=False)
  if not param_obj:
    param = pd_class.get_example()
  else:
    param = json.dumps(param_obj.dict(), indent=2)

  tmp_file = "/tmp/secret-" + uuid.uuid4().hex

  try:
    with open(tmp_file, "w") as f:
      f.write(param)

    valid_value = False
    file_changed = False

    while not valid_value:
      tmp_file_mtime_before = os.path.getmtime(tmp_file)
      _open_file(tmp_file)
      tmp_file_mtime_after = os.path.getmtime(tmp_file)

      file_changed = tmp_file_mtime_before != tmp_file_mtime_after
      if file_changed:
        print("changed")
        try:
          pd_class.parse_file(tmp_file)
        except:
          traceback.print_exc()
          input("Invalid File Content. Press Enter to edit...")
          continue # valid_value still False
      else:
        logger.warning("No content changed")
      valid_value = True

    if file_changed and valid_value:
      logger.info(f"Saving value for: {name}")
      with open(tmp_file, "r") as f:
        params_aws.put_parameter(name=name, modelType=pd_class, value_str=f.read())

  except Exception as e:
      logger.error(e)
  finally:
    if not os.path.exists(tmp_file):
      os.remove(tmp_file)

cli()