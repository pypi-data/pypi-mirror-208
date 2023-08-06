# py-redis-utils



## General info

This is a python package containing functionality working with Redis

### Package installation
```
pip install py-redis-utils
```

### Package usage
```
import pyredisutils
```

## Package contains:

### jwt_redis_auth
Decorator to authenticate using Redis messaging and JWT token
Decorator accepts these params:
    - redis_instance
    - channel_name (for Redis)
    
Usage example:
```
redis_instance = redis.Redis(host=localhost, port=6000, db=1) 

@jwt_redis_auth(redis_instance, 'channel_name')
def generate_pdf() -> Response:      
    pass
```
Process explanation:
- Decorator uses the redis_instance provided to decorator and sends a predefined (hardcoded for now) message withgenerated UUID to Redis channel_name provided to decorator.
- Decorator listens on channel_name+'.reply' channel for a response with same UUID which was sent and then validates it.
- If validation successfull - proceeds to decorated function
- If validation fails, possible responses from decorator:
  - 401 Unauthorized - token is invalid, not authorized
  - 401 Token is missing - token is not provided in the header
  - 502 Bad Gateway - connection to redis instance failed
  - 504 Gateway Timeout - timeout after 5sec of waiting for a response with ID in channel_name+'.reply' channel



