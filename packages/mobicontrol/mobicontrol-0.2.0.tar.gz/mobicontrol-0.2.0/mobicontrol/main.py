from mobicontrol.scripts.fetch_token import fetch_token
from mobicontrol.scripts.upload_apk import get_apk_upload_data
from mobicontrol.utils import get_file_contents, get_filename_from_path
import click
import json
import os
import requests


class Storage(object):
    def __init__(self):
        self.access_token = None
        self.url = None

    @classmethod
    def unserialize(cls, obj):
        inst = cls()
        inst.access_token = obj["access_token"]
        inst.url = obj["url"]
        return inst

    def _serialize(self):
        return {"access_token": self.access_token, "url": self.url}

    def store(self):
        path = os.path.dirname(os.path.abspath(__file__))
        with open(f"{path}/store.json", "w") as file:
            file.write(json.dumps(self._serialize()))


@click.group(invoke_without_command=True)
@click.option("--url", envvar="MC_URL")
@click.pass_context
def mobicontrol(ctx, url):
    try:
        path = os.path.dirname(os.path.abspath(__file__))
        with open(f"{path}/store.json", "r") as file:
            obj = json.loads(file.read())
            ctx.obj = Storage.unserialize(obj)
    except Exception:
        ctx.obj = Storage()

    if ctx.invoked_subcommand is None:
        if url:
            ctx.obj.url = url

        ctx.obj.store()

        click.echo(f"Welcome to Mobicontrol CLI")
        click.echo(f"Your deployment server is located at {url}")

    if ctx.obj.url is None:
        click.echo("Sorry, you need to configure the URL before using the CLI")


@mobicontrol.command()
@click.option("--client_id", envvar="CLIENT_ID")
@click.option("--client_secret", envvar="CLIENT_SECRET")
@click.option("--username", envvar="MC_USERNAME")
@click.option("--password", envvar="MC_PASSWORD")
@click.pass_context
def login(ctx, client_id, client_secret, username, password):
    click.echo(f"Logging in as {username}")
    try:
        url = ctx.obj.url
        token = fetch_token(url, client_id, client_secret, username, password)
        ctx.obj.access_token = token
        ctx.obj.store()
    except Exception as e:
        click.echo("Could not log in")
        click.echo(e)

    click.echo("Successfully logged in!")


@mobicontrol.command()
@click.option("--file")
@click.pass_context
def package(ctx, file):
    click.echo("Uploading package")
    token = ctx.obj.access_token
    url = ctx.obj.url
    try:
        filename = get_filename_from_path(file)
        content = get_file_contents(file)
        headers, body = get_apk_upload_data(url, token, content, filename)

        response = requests.post(f"{url}/packages", headers=headers, data=body)

        if "ErrorCode" in response:
            click.echo(f"Failed with error {response['ErrorCode']}")
            click.echo(response["Message"])
        else:
            click.echo("Upload successful")

    except FileNotFoundError:
        click.echo(f"File {file} does not exist")


@mobicontrol.command()
@click.option("--file")
@click.pass_context
def enterprise_app(ctx, file):
    # click.echo("Uploading enterprise app")
    token = ctx.obj.access_token
    url = ctx.obj.url

    try:
        filename = get_filename_from_path(file)
        content = get_file_contents(file)
        headers, body = get_apk_upload_data(url, token, content, filename)

        response = requests.post(
            f"{url}/appManagement/android/apps/enterprise/internal", headers=headers, data=body
        ).json()

        app_reference = response["ReferenceId"]

        if "ErrorCode" in response:
            click.echo(f"Failed with error {response['ErrorCode']}")
            click.echo(response["Message"])
            raise click.ClickException(f"Upload failed with message: {response['Message']}")

    except FileNotFoundError:
        raise click.ClickException(f"File {file} does not exist")

    click.echo(app_reference)


@mobicontrol.command()
@click.option("--policy-reference")
@click.option("--app-reference")
@click.pass_context
def enterprise_app_install(ctx, policy_reference, app_reference):
    token = ctx.obj.access_token
    url = ctx.obj.url

    response = requests.post(
        f"{url}/appManagement/android/policies/{policy_reference}/enterpriseReferenceId",
        headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
        data={"EnterpriseReferenceId": app_reference},
    ).json()

    if "ErrorCode" in response:
        click.echo(f"Failed with error {response['ErrorCode']}")
        click.echo(response["Message"])
        raise click.ClickException(f"Upload failed with message: {response['Message']}")

    click.echo(f"Successfully assigned app {app_reference} to policy {policy_reference}.")
