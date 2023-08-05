from aws_lambda_mess.framework.Route import Route
from aws_lambda_mess.framework.success import success
from aws_lambda_mess.framework.failures import bad_request
from aws_lambda_mess.framework.server import run


def index(params, body):
    return success({"Hallo": "Index"})


def greet(params, body):
    return success({"Hallo": params["name"]})


def default(params, body):
    return bad_request()


routes = [
    Route(method_pattern="GET", path_pattern="/", handler=index),
    Route(method_pattern="GET", path_pattern="/greet/<name>", handler=greet),
    Route(method_pattern=".*", path_pattern=".*", handler=default)
]

from aws_lambda_mess.framework.lambda_dispatcher import get_handler
lambda_handler = get_handler(routes)

if __name__ == "__main__":
    run(9000, routes)
