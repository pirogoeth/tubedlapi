# -*- coding: utf-8 -*-

import base64
import os

import click


@click.command()
def cli_make_secret():
    ''' Generate a secret suitable for use as env:CRYPTO_SECRET.
    '''

    secret: bytes = base64.b64encode(os.urandom(32))
    click.echo(
        secret.decode('utf-8'),
    )


@click.command()
def cli_make_salt():
    ''' Generate a salt suitable for use as env:CRYPTO_SALT.
    '''

    salt: bytes = base64.b64encode(os.urandom(16))
    click.echo(
        salt.decode('utf-8'),
    )
