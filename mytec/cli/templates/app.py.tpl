from fastapi import FastAPI


app = FastAPI(
    lifespan=lifespan,
    openapi_url=None,
    redirect_slashes=True,
    generate_unique_id_function=generate_unique_id,
)
