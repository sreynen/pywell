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
    'DB_QUERY': 'Database query, as string or file path ending with ".sql".',
    'NO_RESULTS': 'Optional True flag if the query just needs to run without results.',
    'DB_VALUES': 'Optional values to fill placeholders in query.'
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
    if 'DB_VALUES' in args.__dict__ and args.DB_VALUES:
        database_cursor.execute(query, args.DB_VALUES)
    else:
        database_cursor.execute(query)
    if 'NO_RESULTS' in args.__dict__ and args.NO_RESULTS:
        database.commit()
        return []
    return [dict(row) for row in database_cursor.fetchall()]


if __name__ == '__main__':
    run_from_cli(get_psql_results, DESCRIPTION, ARG_DEFINITIONS, REQUIRED_ARGS)
