import json
import os
from pathlib import Path

import click
import yaml

from .config.logging import logger
from .generators.etl_generator import ETLGenerator


def read_entities(source, source_extension, target_extension):
    extension_file = os.path.splitext(source)[1]
    is_folder = not extension_file
    if is_folder:
        sources = [
            f"{source}/{file}"
            for file in filter(
                lambda file: source_extension in file, os.listdir(source)
            )
        ]
    else:
        sources = [source]
    method = {
        ".json": json.load,
        ".yaml": yaml.safe_load,
    }.get(source_extension, lambda textio: textio.read())

    for src in sources:
        try:
            with open(src, "r", encoding="utf-8") as file:
                yield (
                    f"{os.path.splitext(os.path.basename(src))[0]}{target_extension}",
                    method(file),
                )
        except Exception as err:
            logger.error("Um erro ocorreu na leitura dos arquivos: %s", err)


@click.version_option(message="Sefazetllib (v%(version)s)")
@click.group(invoke_without_command=True)
@click.option(
    "-t",
    "--type",
    type=click.Choice(["json", "yaml"]),
    default="json",
    help="File Type",
)
@click.option(
    "--template",
    type=click.Choice(["sefazetllib"]),
    default="sefazetllib",
    help="Template",
)
@click.pass_context
def cli(ctx, type, template):
    ctx.ensure_object(dict)
    ctx.obj["extension"] = f".{type}"
    ctx.obj["generator"] = ETLGenerator


@cli.command()
@click.argument("source", type=click.Path(exists=True))
@click.argument("target")
@click.pass_context
def generate(ctx, source, target):
    entities = read_entities(source, ctx.obj["extension"], ".py")
    generator = ctx.obj["generator"](list(entities), target=target)
    generator.generate()


@cli.command()
@click.argument("source", type=click.Path(exists=True))
@click.argument("target")
@click.pass_context
def derive(ctx, source, target):
    entities = read_entities(source, ".py", ctx.obj["extension"])
    generator = ctx.obj["generator"](list(entities), target=target)
    generator.derive()


@cli.command()
@click.pass_context
def derive_all(ctx):
    for path in Path(Path.cwd()).rglob("*.py"):
        entities = read_entities(str(path.absolute()), ".py", ctx.obj["extension"])
        generator = ctx.obj["generator"](list(entities), target=f"doc")
        generator.derive()


@cli.command()
@click.pass_context
def dependencias(ctx):
    def verify_optional(extract):
        try:
            extract["optional"]
            return False
        except:
            return True

    for path in Path(f"{Path.cwd()}/doc").rglob("*.json"):
        dependencys = {}

        with open(path) as jsonfile:
            file_json = json.load(jsonfile)
            extracts = list(
                map(
                    lambda extract: f"{extract['schema']}/{extract['entity']}",
                    filter(
                        verify_optional,
                        filter(lambda etl: etl["type"] == "extract", file_json["ETL"]),
                    ),
                )
            )

            dependencys[file_json["platform"]["name"]] = {
                extract: False for extract in extracts
            }

            folder = str(path).replace("doc", "dependencias")

            os.makedirs(os.path.dirname(folder), exist_ok=True)
            with open(folder, "w+") as f:
                json.dump(dependencys, f, ensure_ascii=False, indent=4)
