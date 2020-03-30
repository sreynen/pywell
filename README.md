# PyWell

A Unix-first ("do one thing well") approach to Python web apps. The core of PyWell is entry_points.py, a series of functions that can be wrapped around other functions to make them callable in various contexts. Let's start with the most Unix-y of these: `run_from_cli()`, which takes input as command-line parameters and formats output to be readable via command-line.

If you have generic `hello(name)` function, you might use `run_from_cli()` like so:

```
from pywell.entry_points import run_from_cli

DESCRIPTION = 'Say hello.'
ARG_DEFINITIONS = {'NAME': "Who we're greeting"}
REQUIRED_ARGS = ['NAME']

def hello(args):
  return 'hello %s' % args.NAME

if __name__ == '__main__':
  run_from_cli(hello, DESCRIPTION, ARG_DEFINITIONS, REQUIRED_ARGS)
```

You could then call the script from the command line like so:

```
$ python hello.py --NAME world
'hello world'
```

Importantly, `DESCRIPTION`, `ARG_DEFINITIONS`, and `REQUIRED_ARGS` allow the script to self-document, for both someone reading the code and someone trying to run it:

```
$ python hello.py
Who we're greeting (NAME) required, missing.
```

We can, of course, import this script into another:

```
from pywell.entry_points import run_from_cli
from hello import hello

DESCRIPTION = 'Say hello to the world.'
ARG_DEFINITIONS = {}
REQUIRED_ARGS = []

def hello_world(args):
  args.NAME = 'world'
  return hello(args)

if __name__ == '__main__':
  run_from_cli(hello_world, DESCRIPTION, ARG_DEFINITIONS, REQUIRED_ARGS)
```

We can also use this with other command-line utilities:

```
$ python hello.py --NAME $(echo "dlrow" | rev) | awk '{ print toupper($0) }'
'HELLO WORLD'
```

Now that we have our Python script working with the expected input and output via command line, we can easily make it work on AWS Lambda by simply adding an additional entry point:

```
from pywell.entry_points import run_from_cli, run_from_lamba

DESCRIPTION = 'Say hello.'
ARG_DEFINITIONS = {'NAME': "Who we're greeting"}
REQUIRED_ARGS = ['NAME']

def hello(args):
  return 'hello %s' % args.NAME

def aws_lambda(event, context):
  return run_from_lamba(hello, DESCRIPTION, ARG_DEFINITIONS, REQUIRED_ARGS, event)

if __name__ == '__main__':
  run_from_cli(hello, DESCRIPTION, ARG_DEFINITIONS, REQUIRED_ARGS)
```

With just 2 extra lines, this function can be run on Lambda with standard JSON input and output, e.g. input of `{'NAME': 'world'}` will output `'hello world'`.

Or if we want to run our Lambda via API Gateway, simply replace `run_from_lamba` with `run_from_api_gateway` and now our Lambda can take input via POST paramters and return appropriate HTTP headers along with JSON output.

Finally, for functions that return the appropriate structure (list of dict), we can also output as CSV:

```
return run_from_api_gateway(
  hello, DESCRIPTION, ARG_DEFINITIONS, REQUIRED_ARGS, event,
  format='CSV', filename='hello.csv'
)
```

Over time, I'll likely add more entry points and also some general-purpose scripts that might be useful in composing more complex projects. (Or you could — pull requests welcome!) For now, this should hopefully give you a sense of the goals of PyWell: to make small reusable pieces of code usable and testable first on Unix command line, and then minimize the work required to export that composability to the web.
