import asyncio
import contextlib
from typing import Any, AsyncGenerator, Dict, TypedDict

from fastapi import FastAPI
from fastapi.encoders import jsonable_encoder
from {{ project_name }}.db import create_main_async_session_maker, create_main_engine
{% if use_keycloak %}
from {{ project_name }}.di.auth import get_openid_configuration
{% endif %}

{% if use_ozjet %}
from {{ project_name }}.jetapp import app as jet
{% endif %}
from {{project_name}}.logger import init_logger, logger
from {{project_name}}import __version__


class LifespanState(TypedDict):
    main_async_session_maker: Any
{% if use_keycloak %}
    openid_configuration: Dict[str, Any]
{% endif %}


@contextlib.asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[LifespanState, None]:
    init_logger()
    main_engine = create_main_engine()
{% if use_keycloak %}
    openid_configuration = await get_openid_configuration()
{% endif %}
    logger.info("{{ project_name }}services are started", version=__version__)
{% if use_ozjet %}
    jet_task = asyncio.create_task(jet.start())
{% endif %}
    yield {
        "main_async_session_maker": create_main_async_session_maker(main_engine),
{% if use_keycloak %}
        "openid_configuration": openid_configuration,
{% endif %}
    }
    await main_engine.dispose()
{% if use_ozjet %}
    jet_task.cancel()
{% endif %}
    logger.info("{{ project_name }}service are stopped")
