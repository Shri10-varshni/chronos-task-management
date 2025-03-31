import httpx
import json
from datetime import datetime, date, time
from fastapi import HTTPException, status
from app.core.config import settings

def json_serializer(obj):
    """Custom JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, (datetime, date, time)):
        return obj.isoformat()
    if hasattr(obj, 'dict'):
        return obj.dict()
    raise TypeError(f"Type {type(obj)} not serializable")

async def forward_request(service_url: str, path: str, method: str, headers: dict = None, 
                         params: dict = None, data: dict = None, json_data: dict = None):
    """Forward request to the appropriate microservice"""
    url = f"{service_url}{path}"
    
    try:
        print(f"API Gateway: Making request to URL: {url}")
        print(f"API Gateway: Request payload: {json_data}")
        
        # Convert payload to JSON with custom serializer
        if json_data is not None:
            if hasattr(json_data, 'dict'):
                json_data = json_data.dict()
            json_data = json.dumps(json_data, default=json_serializer)
            json_data = json.loads(json_data)
        
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                data=data,
                json=json_data,
                timeout=10.0
            )
            print(f"Forwarded request to {url} with status code {response.status_code}")
            
            # Add response debug logging
            print(f"API Gateway: Response status: {response.status_code}")
            print(f"API Gateway: Response content: {response.content}")
            
            try:
                return {
                    "status_code": response.status_code,
                    "content": response.json() if response.content else None,
                    "headers": dict(response.headers)
                }
            except json.JSONDecodeError as e:
                print(f"API Gateway: JSON decode error: {str(e)}")
                print(f"API Gateway: Raw response content: {response.content}")
                raise
    except Exception as exc:
        print(f"API Gateway: Error in forward_request: {str(exc)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(exc)}"
        )
