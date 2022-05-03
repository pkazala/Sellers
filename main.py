from fastapi import FastAPI, Request, status
from fastapi.responses import HTMLResponse
from starlette.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
import aiohttp
import json

app = FastAPI()

templates = Jinja2Templates(directory='templates')

current = 20

async def depth(data):
    depthNum = 1
    visited = []
    for item in data["sellers"]:
        if (item["seller_type"] != "PUBLISHER" and item["domain"] not in visited):
            depthNum += 1
            visited.append(item["domain"])
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.get("https://" + item["domain"] + "/sellers.json") as response:
                        print("https://" + item["domain"] + "/sellers.json")
                        datas = await response.text()
                        datas = json.loads(data)
                        depth(datas)
                except:
                    print("Wrong address")
    item["depth"] = depthNum
    return data


async def sort(data):
    final = {
        "sellers": []
    }
    visited = []
    for item in data["sellers"]:
        if (item["name"] not in visited):
            visited.append(item["name"])
            final["sellers"].append(item)
    return final

@app.get("/getMore")
def getMore(request: Request):
    global current
    current += 20
    url = app.url_path_for("home")
    return RedirectResponse(url=url, status_code=status.HTTP_303_SEE_OTHER)


@app.api_route("/", methods=["GET", "POST"])
async def home(request: Request):
    async with aiohttp.ClientSession() as session:
        async with session.get("https://openx.com/sellers.json") as response:
            global current
            data = await response.text()
            data = json.loads(data)
            data = await sort(data)
            data = data["sellers"][0:current]
            return templates.TemplateResponse("index.html", {"request": request, "data": data})
