import boto3
from botocore.config import Config
import logging
from amazon_ec2_best_instance import Ec2BestInstance

ec2_client_config = Config(
    retries={
        'max_attempts': 20,
        'mode': 'adaptive'
    }
)

pricing_client_config = Config(
    retries={
        'max_attempts': 10,
        'mode': 'standard'
    }
)

ec2_client = boto3.Session().client('ec2', config=ec2_client_config)
pricing_client = boto3.Session().client('pricing', config=pricing_client_config)

# Optional.
options = {
    # Optional. Default: us-east-1
    'region': 'us-east-1',
    # Optional. Default: 10
    'describe_spot_price_history_concurrency': 20,
    # Optional. Default: 10
    'describe_on_demand_price_concurrency': 20,
    'clients': {
        'ec2': ec2_client,
        'pricing': pricing_client
    }
}

logging.basicConfig(level=logging.INFO, format='%(asctime)s: %(levelname)s: %(message)s')
# Optional.
logger = logging.getLogger()

ec2_best_instance = Ec2BestInstance(options, logger)

response = ec2_best_instance.get_best_instance_types({
    # Required.
    'vcpu': 1,
    # Required.
    'memory_gb': 2,
    # Optional. Default: 'on-demand'. Values: 'spot'|'on-demand'
    'usage_class': 'on-demand',
    # Optional.
    'burstable': False,
    # Optional. Default: 'x86_64'. Values: 'i386'|'x86_64'|'arm64'|'x86_64_mac'
    'architecture': 'x86_64',
    # Optional. Default: ['Linux/UNIX'].
    # Values: Linux/UNIX | Red Hat Enterprise Linux | SUSE Linux | Windows | Linux/UNIX (Amazon VPC) | 
        # Red Hat Enterprise Linux (Amazon VPC) | SUSE Linux (Amazon VPC) | Windows (Amazon VPC)
    'product_descriptions': ['Linux/UNIX'],
    # Optional.
    'is_current_generation': True,
    # Optional. If this parameter is set to True, the method will return the instance type with the best price.
    'is_best_price': True,
    # Optional. If this parameter is set to True, the method will return the instance type with the instance storage.
    'is_instance_storage_supported': True,
    # Optional. Integer. Max spot instance frequency interruption in percent.
    'max_interruption_frequency': 10
})

print(response)