"""Main file"""

import click


@click.group()
def cli():
    """Main function"""

    click.echo("""
    -- O p e n C l a s s R o o m s  (Python Path)  --
    Bienvenue dans la démonstration du projet-6 
    """)


@cli.command()
@click.option("--target", help="Create new tagret operation",
    type=click.Choice(['database', 'user', 'types', 'tables', 'all']))
def initialize(target):
    """Try to create something"""

    from pg_manager import OCPizzaCreator
    create = OCPizzaCreator()
    if target == "all":
        create.all()
    if target == "user":
        create.user()
    if target == "database":
        create.database()
    if target == 'types':
        create.types()
    if target == 'tables':
        create.tables()


@cli.command()
@click.option("--target", help='Create a new record inside target existing '
                             'table', type=str, required=True)
def create(target):
    '''Insert mode for CRUD model to record inside target table'''

    from dialog import Creator
    create_records = Creator(target)
    click.echo(create_records.messages)


@cli.command()
@click.option("--tables", help="show tables list", is_flag=True)
@click.option("--table", help="show table fields list", type=str)
@click.option("--types", help="Show types list and values", is_flag=True)
def inspect(tables, table, types):
    """Inspecte les métadonnées:
    noms de tables, colonnes d'une table, types spécifiques """

    from dialog import Inspector
    inspect = Inspector()
    if tables:
        click.echo(inspect.tables())
    if table:
        click.echo(inspect.table(table))
    if types:
        click.echo(inspect.types())


@cli.command()
@click.option("--table", help="Show table content", type=str)
@click.option("--condition",
              help="Show table content whith condition,",
              type=str)
@click.option("--inline",
              help="Show records in line instead of table view",
              is_flag=True)
def show(table, condition, inline):
    """Show SELECT statement for given table name with optional
    conditions"""

    from dialog import Reader
    if table:
        read_records = Reader(table, inline)
    if condition:
        read_records.conditions(condition)
    click.echo(read_records.message)


if __name__ == '__main__':
    cli()
