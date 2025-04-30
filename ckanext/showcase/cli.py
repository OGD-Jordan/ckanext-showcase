# -*- coding: utf-8 -*-

import click

from ckanext.showcase import utils
from ckanext.showcase.model import teardown

# Click commands for CKAN 2.9 and above


@click.group()
def showcase():
    '''showcase commands
    '''
    pass


@showcase.command()
def markdown_to_html():
    '''
        showcase markdown-to-html
    '''
    utils.markdown_to_html()


def get_commands():
    return [showcase]

@showcase.command()
def init_db_tables():
    utils.init_db_tables()


@showcase.command()
def delete_db():
    teardown()