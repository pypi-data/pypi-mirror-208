import os
import logging
from datetime import datetime

logging.basicConfig(level=logging.CRITICAL)

def isDeployed():
    flag_value = os.getenv("ECIDA_DEPLOY", "").lower()
    return flag_value == "true"

logging.debug("This is a debug message")
logging.info("This is an informational message")
logging.warning("This is a warning message")
logging.error("This is an error message")
logging.critical("This is a critical message")


def now():
    return "[" + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "]"

print(now())

result = isDeployed()
print(f"{now()} result")



def pull(input: str) -> str:
    return __builtins__.input("FUCK")
# inp = input("Type anything:")
print(pull("A"))
