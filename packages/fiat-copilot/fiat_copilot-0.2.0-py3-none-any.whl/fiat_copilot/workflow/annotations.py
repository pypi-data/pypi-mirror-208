from dagster import asset, op, In, Nothing, job, Definitions


def as_asset(
        name: str,
        description: str | None = None,
        io_manager_key: str = "default_io_manager"
):
    def wrapper(computing_func):
        return asset(
            name=name,
            description=description,
            io_manager_key=io_manager_key
        )(computing_func)

    return wrapper


def as_op(
        name: str | None = None,
        description: str | None = None,
        ins=None,
):
    def wrapper(computing_func):
        return op(
            name=name,
            description=description,
            ins=ins or {"start": In(Nothing)},
        )(computing_func)

    return wrapper


def as_job(
        name: str | None = None,
        description: str | None = None,
):
    def wrapper(computing_func):
        return job(
            name=name,
            description=description,
        )(computing_func)

    return wrapper


def form_definitions(
        assets: list,
        resources: dict
) -> Definitions:
    defs = Definitions(
        assets=assets,
        resources=resources
    )

    return defs
