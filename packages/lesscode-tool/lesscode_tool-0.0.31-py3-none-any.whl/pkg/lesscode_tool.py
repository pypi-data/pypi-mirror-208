import os

import click
from requests import get

from pkg.tool.new import create_lesscode_project
from pkg.tool.swagger_tool import swagger_convert
from pkg.tool.table_model_gen import table_model_gen
from pkg.version import __version__

"""
Usage: lesscodeTool [OPTIONS] COMMAND [ARGS]...

  低代码构建工具.

Options:
  --help  Show this message and exit.

Commands:
  new          新建一个项目,目前进支持lesscode-py模板
  sqlacodegen  生成SQLALCHEMY模型类
  subcommand   执行系统命令
  swagger      swagger api转换
"""


@click.version_option(version=__version__, message="%(version)s", help="查看版本号")
@click.help_option(*['-h', '-–help'], help="查看命令帮助")
@click.group(help="低代码构建工具.", context_settings=dict(help_option_names=['-–help', '-h']))
def cli():
    pass


@cli.command()
@click.option('-d', '--dir', type=str, default='.', show_default=True, help='项目目录')
@click.option('-p', '--project', type=str, default='lesscode-py', show_default=True, help='项目模板名称')
@click.help_option('-h', '--help', help='查看子命令new的帮助')
def new(dir, project):
    """新建一个项目,目前进支持lesscode-py模板"""
    if project == "lesscode-py":
        create_lesscode_project(dir)
    else:
        click.echo(f'暂不上支持这个项目模板,请通过子命令subcommand实现')


@cli.command()
@click.option('-u', '--url', type=str, required=True, help='数据库连接')
@click.option('-s', '--schemas', type=str, help='库名，用英文逗号连接多个库')
@click.option('-t', '--tables', type=str, help='表名，用英文逗号连接多个表')
@click.option('-o', '--out', type=str, help='表结构类输出文件')
@click.option('-a', '--add', type=bool, default=False, show_default=True, help='生成model是否带库名')
@click.option('-i', '--ignore', type=bool, default=True, show_default=True, help='忽略字段的None属性')
@click.help_option('-h', '--help', help='查看子命令sqlacodegen的帮助')
def sqlacodegen(url, schemas, tables, out, add, ignore):
    """生成SQLALCHEMY模型类"""
    if schemas:
        schemas = schemas.split(",")
    if tables:
        tables = tables.split(",")
    table_model_gen(url, schemas, tables, out, add, ignore)


@cli.command()
@click.option('-u', '--url', type=str, required=True, help='swagger api地址')
@click.option('-o', '--out_type', type=str, default="md", help='输出类型，支持md,markdown,yaml,yml')
@click.option('-f', '--file', type=str, help='输出到文件的地址')
@click.option('-b', '--base', type=str, default="http://127.0.0.1", help='接口基地址')
@click.help_option('-h', '--help', help='swagger api转换')
def swagger(url, out_type, file, base):
    """swagger api转换"""
    json_data = get(url).json()
    swagger_convert(json_data, out_type, file, base)


@cli.command()
@click.option('-c', '--command', type=str, required=True, help='数据库连接')
@click.help_option('-h', '--help', help='查看子命令subcommand的帮助')
def subcommand(command):
    """执行系统命令"""
    os.system(command)


def main():
    cli()


if __name__ == '__main__':
    main()
