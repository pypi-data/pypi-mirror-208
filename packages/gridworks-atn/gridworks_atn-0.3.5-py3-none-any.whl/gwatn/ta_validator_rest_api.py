from fastapi import FastAPI
from fastapi import HTTPException
from gridworks.utils import RestfulResponse

from gwatn.dev_utils.dev_validator import DevValidator
from gwatn.types import TerminalassetCertifyHack


app = FastAPI()

validator = DevValidator()


@app.post("/terminalasset-certification/")
async def terminalasset_certify_hack_received(payload: TerminalassetCertifyHack):
    r = validator.terminalasset_certify_hack_received(payload)
    return r
