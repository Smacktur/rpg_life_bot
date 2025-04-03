from typing import Dict, Any, Type, Optional, Callable
import inspect
import logging

class ServiceProvider:
    """
    A simple dependency injection container that manages service instances.
    
    This class follows the Service Locator pattern to provide centralized 
    access to services throughout the application.
    """
    
    _instances: Dict[Type, Any] = {}
    _factories: Dict[Type, Callable] = {}
    
    @classmethod
    def register(cls, service_class: Type, factory: Optional[Callable] = None) -> None:
        """
        Register a service with an optional factory function.
        
        Args:
            service_class: The class to register
            factory: Optional factory function to create the service
        """
        if factory:
            cls._factories[service_class] = factory
        else:
            # Use class constructor as factory
            cls._factories[service_class] = service_class
        
        logging.debug(f"Registered service: {service_class.__name__}")
    
    @classmethod
    def get(cls, service_class: Type) -> Any:
        """
        Get or create a service instance.
        
        Args:
            service_class: The class to retrieve
            
        Returns:
            An instance of the requested service
            
        Raises:
            ValueError: If the service is not registered
        """
        # Return cached instance if available
        if service_class in cls._instances:
            return cls._instances[service_class]
        
        # Check if service is registered
        if service_class not in cls._factories:
            raise ValueError(f"Service {service_class.__name__} not registered")
        
        # Create new instance
        factory = cls._factories[service_class]
        instance = factory()
        
        # Cache instance
        cls._instances[service_class] = instance
        return instance
    
    @classmethod
    def reset(cls) -> None:
        """Reset all instances (useful for testing)"""
        cls._instances = {}
    
    @classmethod
    def is_registered(cls, service_class: Type) -> bool:
        """Check if a service is registered"""
        return service_class in cls._factories 