import requests
import logging
from typing import Dict, Optional
from fastapi import HTTPException

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ServiceHealth:
    def __init__(self):
        self.service_urls = {
            "bug_tracker": "http://bug-tracker:8000",
            "code_review": "http://code-review:8001",
            "architectural_model": "http://architectural-model:8003",
            "version_control": "http://version-control:8002"
        }
        self.service_status: Dict[str, bool] = {}

    async def check_service(self, service_name: str) -> bool:
        """Check if a specific service is available."""
        try:
            if service_name not in self.service_urls:
                logger.error(f"Unknown service: {service_name}")
                return False

            url = f"{self.service_urls[service_name]}/health"
            response = requests.get(url, timeout=5)
            is_available = response.status_code == 200
            self.service_status[service_name] = is_available
            return is_available
        except (requests.exceptions.RequestException, requests.exceptions.Timeout) as e:
            logger.error(f"Error checking {service_name} service availability: {str(e)}")
            self.service_status[service_name] = False
            return False

    async def check_all_services(self) -> Dict[str, bool]:
        """Check availability of all services."""
        for service_name in self.service_urls:
            await self.check_service(service_name)
        return self.service_status

    def get_service_status(self, service_name: str) -> Optional[bool]:
        """Get the last known status of a service."""
        return self.service_status.get(service_name)

    def raise_if_service_unavailable(self, service_name: str):
        """Raise an HTTPException if the service is unavailable."""
        if not self.get_service_status(service_name):
            raise HTTPException(
                status_code=503,
                detail=f"Service {service_name} is currently unavailable. Please try again later."
            )

# Create a singleton instance
service_health = ServiceHealth() 