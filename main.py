import traceback
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn
import os
import json

from cdislogging import get_logger
from meshcard import CardClient, NodeCard

LOG_LEVEL = "debug"

# Following will update logger level, propagate, and handlers
logger = get_logger("mesh-service-main", log_level=LOG_LEVEL)

# try:
#     with open("template_skeleton.json", "r") as f:
#         template_skeleton = json.load(f)
# except:
#     logger.warning("Could not find template_skeleton.json")
#     template_skeleton = {}

# try:
#     with open("field_mapping.json", "r") as f:
#         field_mapping = json.load(f)
# except:
#     logger.warning("Could not find field_mapping.json")
#     field_mapping = {}

tags_metadata = [
    {
        "name": "card",
        "description": "get mesh or node card",
    },
    {
        "name": "nodecard",
        "description": "Retrieve nodecards that are a member of this system"
    },
    {
        "name": "status",
        "description": "Check mesh card service status",
    },

]

app = FastAPI(title="Mesh Card Service", openapi_tags=tags_metadata)

card_client = CardClient()


@app.get("/meshcard", tags=["card"])
async def meshcard() -> JSONResponse:
    try:
        status, response = await card_client.return_card()
    except Exception:
        error_message = "Unable to get card!"
        logger.error(error_message)
        traceback.print_exc()
        status, response = 500, {"error": error_message}
    return JSONResponse(content=response, status_code=status)

@app.get("/nodecard", tags=["nodecard"])
async def nodecards() -> JSONResponse:
    # get all node cards as a part of the mesh
    try:
        status, response = await card_client.get_all_cards()
    except Exception as e:
        error_message = "Unable to get all of the cards"
        logger.error(error_message)
        traceback.print_exc()
        status, response = 500, {"error": error_message}
    return JSONResponse(content=response, status_code=status)


@app.get("/nodecard/{commons_name:path}", tags=["nodecard"])
async def single_card(commons_name: str) -> JSONResponse:
    # get the commons node card that is part of this mesh
    try:
        status, response = await card_client.get_card(commons_name)
    except Exception as e:
        error_message = "Unable to get a specific card!"
        logger.error(error_message)
        traceback.print_exc()
        status, response = 500, {"error": error_message}
    return JSONResponse(content=response, status_code=status)

@app.post("/nodecard/validate/")
async def validate_card(nodecard: dict) -> JSONResponse:
    # assert that the node card is valid for the mesh
    try:
        status, response = await card_client.validate_nodecard(nodecard)
    except Exception as e:
        error_message = "Something went wrong while validating card"
        logger.error(error_message)
        traceback.print_exc()
        status, response = 500, {"error": error_message}
    return JSONResponse(content=response, status_code=status)


@app.post("/nodecard")
async def submit_card(nodecard: dict) -> JSONResponse:
    # assert that the node card is valid for the mesh and add it to the node table
    # this means first we need to validate the card and return an error if the card isn't valid
    # then we have to attempt to submit it to the db and return an error if there was a problem with the INSERT
    # if all is well up to this point return a 200
    try:
        status, response = await card_client.insert_nodecard(nodecard)
    except Exception as e:
        error_message = "Something went wrong while inserting the nodecard"
        logger.error(error_message)
        traceback.print_exc()
        status, response = 500, {"error": error_message}
    return JSONResponse(content=response, status_code=status)


@app.get("/_status", tags=["status"])
async def status() -> JSONResponse:
    return JSONResponse(content={"healthy": True}, status_code=200)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
