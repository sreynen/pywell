def all_required_args_set(args, required, definitions) -> bool:
    """
    Check that all requried args are set, print details on any missing.
    """
    set = True

    for arg in required:
        if not getattr(args, arg, False):
            print('%s (%s) required, missing.' % (definitions.get(arg), arg))
            set = False

    return set

def run_from_cli(func, description, definitions, required) -> None:
    """
    Entry point via command line.
    """
    import argparse
    import os
    import pprint

    if os.path.exists(os.path.join(os.getcwd(), 'settings.py')):
        import settings
    else:
        settings = {}

    parser = argparse.ArgumentParser(description=description)

    for argname, helptext in definitions.items():
        parser.add_argument(
            '--%s' % argname, dest=argname, help=helptext,
            default=getattr(settings, argname, False)
        )

    args = parser.parse_args()

    if all_required_args_set(args, required, definitions):
        pprint.PrettyPrinter(indent=2).pprint(func(args))

class Struct:
    def __init__(self, **entries):
        self.__dict__.update(entries)

def json_serial(obj):
    """
    JSON serializer for objects not serializable by default JSON code.
    """
    if isinstance(obj, datetime.datetime):
        return obj.isoformat()
    raise TypeError("Type %s not serializable." % type(obj))

def run_from_lamba(func, description, definitions, required, event) -> str:
    """
    Entry point from Amazon Lambda.
    """
    import json
    import os

    if os.path.exists(os.path.join(os.getcwd(), 'settings.py')):
        import settings
    else:
        settings = {}

    kwargs = event.get('kwargs', False)
    if kwargs:
        for argname in kwargs.keys():
            event[argname] = kwargs.get(argname)

    for argname, helptext in definitions.items():
        if not event.get(argname, False):
            event[argname] = getattr(settings, argname, False)

    args = Struct(**event)

    if all_required_args_set(args, required, definitions):
        return json.dumps(func(args), default=json_serial)


def run_from_api_gateway(func, description, definitions, required, event, format='JSON', filename='') -> str:
    """
    Entry point from Amazon Lambda via API Gateway.
    """
    import json
    import os
    from urllib.parse import parse_qsl

    if os.path.exists(os.path.join(os.getcwd(), 'settings.py')):
        import settings
    else:
        settings = {}

    kwargs = event.get('kwargs', False)
    if kwargs:
        for argname in kwargs.keys():
            event[argname] = kwargs.get(argname)

    if event.get('httpMethod', '') == 'POST':
        try:
            post_body = json.loads(event.get('body', '{}'))
        except:
            try:
                post_body = dict(parse_qsl(event.get('body', '')))
            except:
                post_body = {}
        for argname, helptext in definitions.items():
            if not event.get(argname, False) and argname in post_body.keys():
                event[argname] = post_body.get(argname, False)

    for argname, helptext in definitions.items():
        if not event.get(argname, False):
            event[argname] = getattr(settings, argname, False)

    args = Struct(**event)

    if all_required_args_set(args, required, definitions):
        result = func(args)
        if format == 'CSV':
            import csv
            import io
            if len(result):
                headers = result[0].keys()
            else:
                headers = []
            output = io.StringIO()
            writer = csv.DictWriter(
                output,
                quoting=csv.QUOTE_NONNUMERIC,
                fieldnames=headers
            )
            writer.writeheader()
            for data in result:
                writer.writerow(data)
            return {
                'isBase64Encoded': True,
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'text/csv',
                    'Content-Disposition': 'attachment;filename=%s' % filename
                },
                "body": output.getvalue()
            }
        else:
            return {
                'isBase64Encoded': False,
                'statusCode': 200,
                'headers': {'Content-Type': 'application/json'},
                "body": json.dumps(result)
            }
