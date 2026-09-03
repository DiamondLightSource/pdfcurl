from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI, Request

import pdfcurl
from pdfcurl._version import __version__
from pdfcurl.logger import logger

ROUTER = APIRouter()

HEALTH_ROUTE = "/healthz"
DATA2PDF = "/data2pdf"


@ROUTER.get(HEALTH_ROUTE)
async def health():
    return {"status": "ok"}


# New endpoint to return all jobs/results if enabled in config
@ROUTER.get(DATA2PDF)
async def get_all_results(request: Request):

    results = "done"

    return results


@asynccontextmanager
async def lifespan(app: FastAPI):

    logger.info("PDFAPI started")

    yield

    logger.info("Shutting down")


def start_api() -> FastAPI:

    app = FastAPI(
        title=pdfcurl.__name__.capitalize(),
        version=__version__,
        description="An API for PDFGetX3 jobs",
        lifespan=lifespan,
    )

    # Include API routes
    app.include_router(ROUTER)
    return app


if __name__ == "__main__":
    start_api()
