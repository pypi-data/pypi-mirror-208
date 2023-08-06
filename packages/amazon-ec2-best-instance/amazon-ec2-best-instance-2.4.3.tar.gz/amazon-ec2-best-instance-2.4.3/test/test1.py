from amazon_ec2_best_instance import Ec2BestInstance

ec2_best_instance = Ec2BestInstance({
    # Optional. Default: us-east-1
    'region': 'us-east-1',
    # Optional. Default: 10
    'describe_spot_price_history_concurrency': 20,
    # Optional. Default: 10
    'describe_on_demand_price_concurrency': 20
})

response = ec2_best_instance.get_best_instance_types({
    'vcpu': 1,
    'memory_gb': 2,
    'burstable': False,
    'is_best_price': True,
    'usage_class': 'spot',
    'is_current_generation': True
})

print(response)

response = ec2_best_instance.get_best_instance_types({
    # Required.
    'vcpu': 1,
    # Required.
    'memory_gb': 2,
    # Optional. Default: 'on-demand'. Values: 'spot'|'on-demand'
    'usage_class': 'spot',
    # Optional.
    'burstable': False,
    # Optional. Default: 'x86_64'. Values: 'i386'|'x86_64'|'arm64'|'x86_64_mac'
    'architecture': 'x86_64',
    # Optional. Default: ['Linux/UNIX']. Values: 'Linux/UNIX'|'Linux/UNIX (Amazon VPC)'|'Windows'|'Windows (Amazon VPC)'
    'operation_systems': ['Linux/UNIX'],
    # Optional.
    'is_current_generation': False,
    # Optional.
    'is_best_price': True,
})

print(response)

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
    # Optional. Default: ['Linux/UNIX']. Values: 'Linux/UNIX'|'Linux/UNIX (Amazon VPC)'|'Windows'|'Windows (Amazon VPC)'
    'operation_systems': ['Linux/UNIX'],
    # Optional.
    'is_current_generation': False,
    # Optional.
    'is_best_price': True,
})

print(response)