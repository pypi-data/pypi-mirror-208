"""The Rest API wrapper for the TaDaemon Smart Contract"""
from fastapi import FastAPI
from fastapi import HTTPException
from gridworks.utils import RestfulResponse

from gwatn.python_ta_daemon import PythonTaDaemon
from gwatn.types import InitialTadeedAlgoOptin
from gwatn.types import NewTadeedAlgoOptin
from gwatn.types import OldTadeedAlgoReturn
from gwatn.types import SlaEnter


tags_metadata = [
    {
        "name": "initial.tadeed.algo.optin",
        "description": "Request TaDaemon to opt into the first TaDeed for its TerminalAsset. "
        "Must be sent by the TaOwner.",
        "externalDocs": {
            "description": "Lexicon w definitions of TaDaemon, TaDeed, TerminalAsset, TaOwner",
            "url": "https://gridworks.readthedocs.io/en/latest/lexicon.html",
        },
    },
]

app = FastAPI(openapi_tags=tags_metadata)
daemon = PythonTaDaemon()

# @app.get("/", response_class=FileResponse)
# async def root():
#     if os.path.isfile("docs/wiki/img/mushroom.png"):
#         return FileResponse("docs/wiki/img/mushroom.png", media_type="image/png")
#     else:
#         return FileResponse("docs/wiki/img/mushroom.png", media_type="image/png")


# @app.get("/icon/")
# async def main():
#     return daemon.ta_deed_icon_file


@app.get("/owned-tadeeds/")
async def main():
    return {"Owned deeds": daemon.ta_deed_alias_list()}


@app.get("/trading-rights/")
async def main():
    if daemon.trading_rights_addr == daemon.acct.addr:
        return {"Address of Trading Rights Owner": "self"}
    else:
        return {"Address of Trading Rights Owner": daemon.trading_rights_addr}


@app.get("/env/")
async def show_env():
    return daemon.settings


@app.post(
    "/initial-tadeed-algo-optin/",
    response_model=RestfulResponse,
    tags=["initial.tadeed.algo.optin"],
)
async def initial_tadeed_algo_optin_received(payload: InitialTadeedAlgoOptin):
    r = daemon.initial_tadeed_algo_optin_received(payload)
    if r.HttpStatusCode > 200:
        raise HTTPException(
            status_code=r.HttpStatusCode, detail=f"[{r.HttpStatusCode}]: {r.Note}"
        )
    return r


@app.post("/new-tadeed-algo-optin/", response_model=RestfulResponse)
async def new_tadeed_algo_received(payload: NewTadeedAlgoOptin):
    r = daemon.new_tadeed_algo_optin_received(payload)
    if r.HttpStatusCode > 200:
        raise HTTPException(
            status_code=r.HttpStatusCode, detail=f"[{r.HttpStatusCode}]: {r.Note}"
        )
    return r


@app.post("/old-tadeed-algo-return/", response_model=RestfulResponse)
async def old_tadeed_algo_return_received(payload: OldTadeedAlgoReturn):
    r = daemon.old_tadeed_algo_return_received(payload)
    if r.HttpStatusCode > 200:
        raise HTTPException(
            status_code=r.HttpStatusCode, detail=f"[{r.HttpStatusCode}]: {r.Note}"
        )
    return r


@app.post("/sla-enter/", response_model=RestfulResponse)
async def old_tadeed_algo_return_received(payload: SlaEnter):
    r = daemon.sla_enter_received(payload)
    if r.HttpStatusCode > 200:
        raise HTTPException(
            status_code=r.HttpStatusCode, detail=f"[{r.HttpStatusCode}]: {r.Note}"
        )
    return r
