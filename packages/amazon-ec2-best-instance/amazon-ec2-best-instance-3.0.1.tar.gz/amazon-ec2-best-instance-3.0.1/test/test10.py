import logging
from amazon_ec2_best_instance import Ec2BestInstance

# Optional.
options = {
    # Optional. Default: us-east-1
    'region': 'us-east-1',
    # Optional. Default: 10
    'describe_spot_price_history_concurrency': 20,
    # Optional. Default: 10
    'describe_on_demand_price_concurrency': 20
}

logging.basicConfig(level=logging.INFO, format='%(asctime)s: %(levelname)s: %(message)s')
# Optional.
logger = logging.getLogger()

ec2_best_instance = Ec2BestInstance(options, logger)

response = ec2_best_instance.get_best_instance_types({
    'vcpu': 16,
    'memory_gb': 20,
    'usage_class': 'spot',
    'burstable': False,
    'architecture': 'arm64',
    'operation_systems': ['Linux/UNIX'],
    # 'is_current_generation': True,
    'is_best_price': True,
    'availability_zones': ['us-east-1a', 'us-east-1b', 'us-east-1c']
})

print(response[0:10])
