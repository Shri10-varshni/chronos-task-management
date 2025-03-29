import httpx
from fastapi import HTTPException, status
from app.core.config import settings

async def forward_request(service_url: str, path: str, method: str, headers: dict = None, 
                         params: dict = None, data: dict = None, json: dict = None):
    """
    Forward request to the appropriate microservice
    """
    url = f"{service_url}{path}"
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                data=data,
                json=json,
                timeout=10.0  # 10 seconds timeout
            )
            
            return {
                "status_code": response.status_code,
                "content": response.json() if response.content else None,
                "headers": dict(response.headers)
            }
    except httpx.RequestError as exc:
        # Handle request errors (connection errors, timeouts, etc.)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service unavailable: {str(exc)}"
        )
    except Exception as exc:
        # Handle other unexpected errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(exc)}"
        )
