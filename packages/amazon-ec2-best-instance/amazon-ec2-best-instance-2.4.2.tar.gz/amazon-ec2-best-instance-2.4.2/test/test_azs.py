import time

from amazon_ec2_best_instance import Ec2BestInstance

ec2_best_instance = Ec2BestInstance()

response = ec2_best_instance.get_best_instance_types({
    'vcpu': 16,
    'memory_gb': 20,
    'usage_class': 'spot',
    'burstable': False,
    'is_best_price': True,
    'is_current_generation': True,
    'max_interruption_frequency': 15,
    'availability_zones': ['us-east-1a', 'us-east-1b', 'us-east-1c']
})

print(response[0])

response = ec2_best_instance.get_best_instance_types({
    'vcpu': 16,
    'memory_gb': 20,
    'usage_class': 'spot',
    'burstable': False,
    'is_best_price': True,
    'is_current_generation': True,
    'max_interruption_frequency': 15,
    #'availability_zones': ['us-east-1a', 'us-east-1b', 'us-east-1c']
})

print(response[0])

response = ec2_best_instance.get_best_instance_types({
    'vcpu': 16,
    'memory_gb': 20,
    'usage_class': 'spot',
    'burstable': False,
    'is_best_price': True,
    'is_current_generation': True,
    'max_interruption_frequency': 15,
    'availability_zones': ['us-east-1d']
})

print(response[0])
