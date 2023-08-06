import time
import logging

from amazon_ec2_best_instance import Ec2BestInstance

logging.basicConfig(level=logging.INFO, format='%(asctime)s: %(levelname)s: %(message)s')
# Optional.
logger = logging.getLogger()

ec2_best_instance = Ec2BestInstance(logger=logger)

response = ec2_best_instance.get_best_instance_types({
    "vcpu": 16,
    "memory_gb": 1,
    "is_best_price": True
})

print(response[0])

ec2_best_instance = Ec2BestInstance(logger=logger)

response = ec2_best_instance.get_best_instance_types({
    "vcpu": 16,
    "memory_gb": 1,
    "is_best_price": True
})

print(response[0])
