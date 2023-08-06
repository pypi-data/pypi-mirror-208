import os
import time
import json
from http import HTTPStatus
from inspect import signature
from dataclasses import dataclass
from typing import get_args, get_origin

from ..utils.convert import JSONEncoder
from ..utils.data import import_modules, import_directories
from ..di.data import qualifier_to_data
from ..di.injector import init_config, provide
from .data import HTTPRequest, HTTPResponse, http_event_to_request
from .app_controller import AppController


@dataclass()
class _Route:
    func: callable
    request_type: type | None
    dependencies: list[tuple[type, str | None]]


class AppModule:
    """AWS lambda application main entry point.
    :param controllers: Application controllers.
    :param modules: Modules to force import.
    :param directories: Directories to force import.
    """

    def __init__(self, controllers: list[AppController],
                 modules: list[str] = None,
                 directories: list[str] = None):

        if modules:
            import_modules(modules)
        elif os.environ.get("IMPORT_MODULES"):
            import_modules(os.environ["IMPORT_MODULES"].split(","))

        root = os.environ["ROOT_DIRECTORY"] if os.environ.get("ROOT_DIRECTORY") else "/var/task/"

        if directories:
            import_directories(root, directories)
        elif os.environ.get("IMPORT_DIRECTORIES"):
            import_directories(root, os.environ["IMPORT_DIRECTORIES"].split(","))

        init_config()

        routes = dict()

        for c in controllers:
            routes.update(c.routes)

        for resource, methods in routes.items():
            for method, handler in methods.items():

                request_type: type | None = None
                dependencies: list[tuple[type, str | None]] = list()
                data = qualifier_to_data(handler[1]) if handler[1] else dict()

                for key, value in signature(handler[0]).parameters.items():
                    origin = get_origin(value.annotation)
                    cls = origin if origin else value.annotation
                    if cls is HTTPRequest:
                        args = get_args(value.annotation)
                        request_type = args[0] if len(args) > 0 else dict
                        continue
                    dependencies.append((cls, data.get(key)))

                if not request_type:
                    raise Exception("HTTPRequest param is not provided.")
                routes[resource][method] = _Route(handler[0], request_type, dependencies)

        self._routes = routes

    async def serve(self, event: dict, context) -> dict:

        try:
            start = time.time()

            route = self._routes[event["resource"]][event["httpMethod"]]
            if not route:
                raise ValueError(f"unknown route, resource: {event.get('resource')} method: {event.get('httpMethod')}")

            params = [await provide(cls, name) for cls, name in route.dependencies]
            params.append(http_event_to_request(route.request_type, event, context))

            response: HTTPResponse = await route.func(*params)

            status_code = response.status
            body = json.dumps(response.body, cls=JSONEncoder) if response.body else response.body
            headers = response.headers if response.headers else dict()
            headers["X-Process-Time"] = int((time.time() - start) * 1000)

        except Exception as e:
            print(f"error:: {e}")
            status_code = HTTPStatus.BAD_REQUEST
            body = json.dumps({"message": str(e)})
            headers = dict()

        return {
            "statusCode": status_code,
            "body": body,
            "headers": headers
        }
