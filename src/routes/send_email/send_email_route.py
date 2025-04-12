import http.client
import json
import os
from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder
from database.engine import SessionDep
from validations import send_email_validation
from routes.send_email.template import get_html_template


router = APIRouter()


@router.post("/send-mail/", tags=["Mail"])
async def send(payload: send_email_validation.SendMailValidation):
    try:
        html_template = get_html_template(content=payload.content,
                                          title=payload.subject,
                                          email_type=payload.category,
                                          subtitle=payload.subtitle)
        payload = {
            "to": [{"email": payload.to.email, "name": payload.to.name}],
            "from": {"email": payload.origin.email, "name": payload.origin.name},
            "subtitle": f"{payload.subtitle}", 
            "subject": payload.subject,
            "text": payload.content,
            "category": payload.category,
            "html": html_template
        }
        conn = http.client.HTTPSConnection("send.api.mailtrap.io")
        headers = {
            'Content-Type': "application/json",
            'Accept': "application/json",
            'Api-Token': os.getenv("MAIL_API")
        }

        conn.request("POST", "/api/send",
                     json.dumps(jsonable_encoder(payload)), headers)

        res = conn.getresponse()
        data = res.read()
        decoded_data = data.decode('utf-8')

        print(decoded_data)
        return decoded_data
    except Exception as e:
        print(f"Send email api error: {e}")
