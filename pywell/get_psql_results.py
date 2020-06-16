import psycopg2
import psycopg2.extras

from pywell.entry_points import run_from_cli


DESCRIPTION = 'Get results from a database query.'

ARG_DEFINITIONS = {
    'DB_HOST': 'Database host IP or hostname.',
    'DB_PORT': 'Database port number.',
    'DB_USER': 'Database user.',
    'DB_PASS': 'Database password.',
    'DB_NAME': 'Database name.',
    'DB_QUERY': 'Database query, as string or file path ending with ".sql".'
}

REQUIRED_ARGS = [
    'DB_HOST', 'DB_PORT', 'DB_USER', 'DB_PASS', 'DB_NAME', 'DB_QUERY'
]


def get_psql_results(args):
    database = psycopg2.connect(
        host=args.DB_HOST,
        port=args.DB_PORT,
        user=args.DB_USER,
        password=args.DB_PASS,
        database=args.DB_NAME
    )
    database_cursor = database.cursor(
            cursor_factory=psycopg2.extras.RealDictCursor
    )
    if args.DB_QUERY[-4:] == '.sql':
        with open(args.DB_QUERY, 'r') as file:
            query = file.read()
    else:
        query = args.DB_QUERY
    database_cursor.execute(query)
    return [dict(row) for row in database_cursor.fetchall()]


if __name__ == '__main__':
    run_from_cli(get_psql_results, DESCRIPTION, ARG_DEFINITIONS, REQUIRED_ARGS)
