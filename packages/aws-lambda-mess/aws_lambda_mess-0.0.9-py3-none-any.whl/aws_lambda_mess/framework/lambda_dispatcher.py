import json

from aws_lambda_mess.framework.failures import not_found, internal_server_error


def get_handler(routes):
    def lambda_handler(event, context):
        path = event.get("path", "/")
        method = event.get("httpMethod", "GET")
        body = json.loads(event.get("body", None) or "{}")

        for route in routes:
            match, params = route.match(method, path)
            if match:
                try:
                    return route.run(params, body)
                except:
                    return internal_server_error()

        return not_found()
    return lambda_handler