from .services.status_manager import status_manager_instance, ProcessStatusManager

def get_status_manager() -> ProcessStatusManager:
    return status_manager_instance
