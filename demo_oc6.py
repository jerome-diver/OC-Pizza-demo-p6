"""Main file"""

import click


@click.group()
def cli():
    """Main function"""

    click.secho("""
    -- O p e n C l a s s R o o m s  (Python Path)  --
    Bienvenue dans la démonstration du projet-6 
    """, fg='green')


@cli.command()
@click.option("--target", help="Create new target operation",
    type=click.Choice(['database', 'user', 'types', 'tables', 'all']))
def initialize(target):
    """Try to create something"""

    from pg_manager import OCPizzaCreator
    create = OCPizzaCreator()
    success = False
    helped = False
    if target == "all":
        success = create.all()
    elif target == "user":
        success = create.user()
    elif target == "database":
        success = create.database()
    elif target == 'types':
        success = create.types()
    elif target == 'tables':
        success = create.tables()
    else:
        click.secho("You have to use a --target option (look at --help)",
                    fg='yellow')
        helped = True
    if not helped:
        click.secho("SUCCESS" if success else "FAILED",
                    fg='green' if success else 'red')

@cli.command()
@click.option("--target",
              help='Create a new record inside target existing table',
              type=str, required=False)
@click.option("--from_csv", help="with --target, record from a csv file",
              type=str, required=False)
@click.option("--entry_list",
              help="get possible entry list for insert datas in database",
              is_flag=True)
@click.option("--debug", help="Show debug messages", is_flag=True)
def create(target, entry_list, from_csv, debug):
    '''Insert mode for CRUD model to record inside target table'''

    from pg_manager import Record
    if entry_list:
        click.secho("""
        You have to respect order of entries, and by the fact, it is logic:
        1/ 'user'
        2/ 'provider', 'promotion', 'code_accounting'
        3/ 'nutriment', 'drink', 'option' 
        4/ 'pizza'
        5/ 'restaurant', 'stock'
        6/ 'hand_over', 'order'
        
        The other one tables will be populate by your answers at 
        asked questions tags during creation process. 
        Having fun...
        """, fg='blue')
    elif target:
        if from_csv:
            new_records = Record(target, file=from_csv, file_type="csv")
        else:
            new_records = Record(target)
        click.secho(new_records.show_messages(), fg='green')
        if debug:
            click.secho(new_records.show_debug(), fg='red')
    else:
        click.secho("""
        You have to use one option:
        --target [NAME_OF_TARGET]\twill create a target record
        \twith --from-csv [absolute_filename]\tcreate from csv filename
        --entry_list             \twill show possible target list
        """, fg="yellow")


@cli.command()
@click.option("--tables", help="show tables list", is_flag=True)
@click.option("--table", help="show table fields list", type=str)
@click.option("--types", help="Show types list and values", is_flag=True)
def inspect(tables, table, types):
    """Show metadata of database 'oc-pizza':
    tables names, table's fields details, user's types list,
    specific named user's type enum content"""

    from dialog import Inspector
    inspect = Inspector()
    if tables:
        click.secho(inspect.tables(), fg='blue')
    elif table:
        click.secho(inspect.table(table), fg='blue')
    elif types:
        click.secho(inspect.types(), fg='blue')
    else:
        click.secho("add \"--help\" for read use of \"inspect\" command",
                    fg='yellow')


@cli.command()
@click.option("--table", help="Show table content", type=str)
@click.option("--condition",
              help="Show table content whith condition,",
              type=str)
@click.option("--inline",
              help="Show records in line instead of table view",
              is_flag=True)
def show(table, condition, inline):
    """Show content for given table name with optional conditions"""

    from dialog import Reader
    if table:
        read_records = Reader(table, inline)
        if condition:
            read_records.conditions(condition)
        click.secho(read_records.message, fg='blue')
    else:
        click.secho("add \"--help\" for read use of \"show\" command",
                    fg='yellow')


if __name__ == '__main__':
    cli()
