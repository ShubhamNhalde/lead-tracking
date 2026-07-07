from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
import httpx
from datetime import datetime

from database import get_db
from whatsapp import send_whatsapp


app = FastAPI()


NETLIFY_URL = "https://6a3d17e4f455624e2c44955a--relaxed-buttercream-4fb006.netlify.app"



@app.get("/page/{lead_token}")

async def track_page(
    lead_token:str,
    request:Request
):


    db=get_db()

    cursor=db.cursor(dictionary=True)



    cursor.execute(
        """
        SELECT *
        FROM leads
        WHERE lead_token=%s
        """,
        (lead_token,)
    )


    lead=cursor.fetchone()


    if not lead:

        return {
            "error":"Lead not found"
        }



    ip=request.client.host



    cursor.execute(
        """
        INSERT INTO activity_logs
        (
        lead_token,
        event,
        activity,
        ip_address
        )
        VALUES(%s,%s,%s,%s)
        """,

        (
        lead_token,
        "page_open",
        "Lead opened the page",
        ip
        )

    )


    db.commit()



    message=f"""
🔔 Live Activity Alert!

Lead Name: {lead['name']}
Phone: {lead['phone']}

Event: page_open

Activity:
Lead opened the page

Page:
{lead['page_name']}

URL:
{lead['page_url']}

Time:
{datetime.utcnow().isoformat()}Z

"""


    send_whatsapp(message)



    async with httpx.AsyncClient() as client:

        response=await client.get(
            NETLIFY_URL
        )


    return HTMLResponse(
        response.text
    )
