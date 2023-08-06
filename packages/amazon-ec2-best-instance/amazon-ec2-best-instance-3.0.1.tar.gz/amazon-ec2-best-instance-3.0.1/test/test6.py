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

is_instance_storage_supported = ec2_best_instance.is_instance_storage_supported_for_instance_type('m5.4xlarge')

assert not is_instance_storage_supported

is_instance_storage_supported = ec2_best_instance.is_instance_storage_supported_for_instance_type('m5d.4xlarge')

assert is_instance_storage_supported
