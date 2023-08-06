import boto3
import json
import logging
import os
import operator
import hashlib
from datetime import datetime
from typing import Optional, Dict, Any
from multiprocessing.pool import ThreadPool
from lambda_thread_pool import LambdaThreadPool
from .SpotUtils import SpotUtils


class Ec2BestInstance:
    __DESCRIBE_SPOT_PRICE_HISTORY_CONCURRENCY = 10
    __DESCRIBE_ON_DEMAND_PRICE_CONCURRENCY = 10
    __CACHE_TTL_IN_MINUTES = 120
    __cache = {}

    __REGIONS = {
        'us-east-2': 'US East (Ohio)',
        'us-east-1': 'US East (N. Virginia)',
        'us-west-1': 'US West (N. California)',
        'us-west-2': 'US West (Oregon)',
        'ap-east-1': 'Asia Pacific (Hong Kong)',
        'ap-south-1': 'Asia Pacific (Mumbai)',
        'ap-northeast-3': 'Asia Pacific (Osaka-Local)',
        'ap-northeast-2': 'Asia Pacific (Seoul)',
        'ap-southeast-1': 'Asia Pacific (Singapore)',
        'ap-southeast-2': 'Asia Pacific (Sydney)',
        'ap-northeast-1': 'Asia Pacific (Tokyo)',
        'ca-central-1': 'Canada (Central)',
        'cn-north-1': 'China (Beijing)',
        'cn-northwest-1': 'China (Ningxia)',
        'eu-central-1': 'EU (Frankfurt)',
        'eu-west-1': 'EU (Ireland)',
        'eu-west-2': 'EU (London)',
        'eu-west-3': 'EU (Paris)',
        'eu-north-1': 'EU (Stockholm)',
        'me-south-1': 'Middle East (Bahrain)',
        'sa-east-1': 'South America (Sao Paulo)'
    }

    __OS_PRODUCT_DESCRIPTION_MAP = {
        'Linux/UNIX': 'Linux',
        'Red Hat Enterprise Linux': 'RHEL',
        'SUSE Linux': 'SUSE',
        'Windows': 'Windows',
        'Linux/UNIX (Amazon VPC)': 'Linux',
        'Red Hat Enterprise Linux (Amazon VPC)': 'RHEL',
        'SUSE Linux (Amazon VPC)': 'SUSE',
        'Windows (Amazon VPC)': 'Windows'
    }

    def __init__(self, options: Optional[Dict[str, Any]] = None, logger: Optional[logging.Logger] = None):
        if options is None:
            options = {}

        self.__CACHE_TTL_IN_MINUTES = options.get('cache_ttl_in_minutes', self.__CACHE_TTL_IN_MINUTES)
        self.__Pool = self.__get_pool()
        self.__region = options.get('region', 'us-east-1')
        self.__describe_spot_price_history_concurrency = options.get('describe_spot_price_history_concurrency',
                                                                     self.__DESCRIBE_SPOT_PRICE_HISTORY_CONCURRENCY)
        self.__describe_on_demand_price_concurrency = options.get('describe_on_demand_price_concurrency',
                                                                  self.__DESCRIBE_ON_DEMAND_PRICE_CONCURRENCY)
        self.__ec2_client = self.__get_client(options, 'ec2', self.__region)
        self.__pricing_client = self.__get_client(options, 'pricing', 'us-east-1')
        self.__logger = logger if logger is not None else logging.getLogger()

    def get_best_instance_types(self, options={}):
        hash_digest = self.get_hash(options)
        if self.__cache.get(hash_digest) is not None:
            cache_datetime = self.__cache[hash_digest]['datetime']
            now = datetime.now()
            delta = now - cache_datetime
            delta_in_minutes = delta.total_seconds() / 60
            if delta_in_minutes <= self.__CACHE_TTL_IN_MINUTES:
                self.__logger.info(f'Cache hit for {hash_digest}')
                return self.__cache[hash_digest]['result']
            else:
                self.__logger.info(f'Cache expired for {hash_digest}')
                del self.__cache[hash_digest]['result']
        else:
            self.__logger.info(f'Cache miss for {hash_digest}')

        import logging
        logging.getLogger("urllib3").setLevel(logging.ERROR)
        if options.get('vcpu') is None:
            raise Exception('A vcpu option is missing')
        if options.get('memory_gb') is None:
            raise Exception('A memory_gb option is missing')

        cpu = options['vcpu']
        memory_gb = options.get('memory_gb')

        usage_class = options.get('usage_class', 'on-demand')
        burstable = options.get('burstable')
        architecture = options.get('architecture', 'x86_64')
        availability_zones = options.get('availability_zones')
        final_spot_price_determination_strategy = options.get('final_spot_price_determination_strategy', 'min')

        has_gpu = options.get('has_gpu')
        gpu_memory = options.get('gpu_memory')

        valid_product_descriptions = [
            'Linux/UNIX',
            'Red Hat Enterprise Linux',
            'SUSE Linux',
            'Windows',
            'Linux/UNIX (Amazon VPC)',
            'Red Hat Enterprise Linux (Amazon VPC)',
            'SUSE Linux (Amazon VPC)',
            'Windows (Amazon VPC)'
        ]
        product_description = options.get('product_description', 'Linux/UNIX')
        if product_description not in valid_product_descriptions:
            raise Exception(f'The product description {product_description} is not supported')
        is_current_generation = None
        is_best_price = True
        is_instance_storage_supported = options.get('is_instance_storage_supported')
        max_interruption_frequency = options.get('max_interruption_frequency')
        operating_system = self.__get_operating_system_by_product_description(product_description)

        if options.get('is_current_generation') is not None:
            is_current_generation = 'true' if options['is_current_generation'] == True else 'false'

        instances = self.__describe_instance_types({
            'is_current_generation': is_current_generation,
            'is_instance_storage_supported': is_instance_storage_supported
        })

        filtered_instances = self.__filter_ec2_instances(instances, {
            'cpu': cpu,
            'memory_gb': memory_gb,
            'usage_class': usage_class,
            'burstable': burstable,
            'architecture': architecture,
            'has_gpu': has_gpu,
            'gpu_memory': gpu_memory
        })

        self.__logger.debug(f'Instance types number before filtering: {str(len(instances))}')

        if usage_class == 'spot' and max_interruption_frequency is not None:
            spot_utils = SpotUtils(self.__region)

            interruption_frequencies = spot_utils.get_spot_interruption_frequency(operating_system)

            def interruption_frequency_statistic_existing_filter(ec2_instance):
                instance_type = ec2_instance['InstanceType']
                if interruption_frequencies.get(instance_type) is not None:
                    return True
                else:
                    self.__logger.warning(
                        f'Interruption frequency statistic is missing for {instance_type}, so instance type is ignored')
                    return False

            filtered_instances = list(filter(interruption_frequency_statistic_existing_filter, filtered_instances))

            def add_interruption_frequency(ec2_instance, interruption_frequency):
                ec2_instance['interruption_frequency'] = interruption_frequency
                return ec2_instance

            filtered_instances = list(map(lambda ec2_instance:
                                          add_interruption_frequency(ec2_instance, interruption_frequencies[
                                              ec2_instance['InstanceType']]),
                                          filtered_instances))
            filtered_instances = list(
                filter(lambda ec2_instance: ec2_instance['interruption_frequency']['min'] <= max_interruption_frequency,
                       filtered_instances))

        self.__logger.debug(f'Instance types number after filtering: {str(len(filtered_instances))}')

        if is_best_price:
            if usage_class == 'on-demand':
                result = self.__sort_on_demand_instances_by_price(filtered_instances, operating_system)
            elif usage_class == 'spot':
                result = self.__sort_spot_instances_by_price(filtered_instances, product_description,
                                                             availability_zones,
                                                             final_spot_price_determination_strategy)
            else:
                raise Exception(f'The usage_class: {usage_class} does not exist')
        else:
            result = list(map(lambda ec2_instance: {'instance_type': ec2_instance['InstanceType']}, filtered_instances))

        hash_digest = self.get_hash(options)
        self.__cache[hash_digest] = {
            'result': result,
            'datetime': datetime.now()
        }
        return result

    def is_instance_storage_supported_for_instance_type(self, instance_type):
        response = self.__ec2_client.describe_instance_types(
            InstanceTypes=[instance_type]
        )
        instance_types = response['InstanceTypes']
        if len(instance_types) == 0:
            raise Exception(f'The {instance_type} instance type not found')
        instance_type_description = instance_types[0]
        is_instance_storage_supported = instance_type_description['InstanceStorageSupported']
        return is_instance_storage_supported

    def __describe_instance_types(self, options=None):
        is_current_generation = None
        is_instance_storage_supported = None

        if options is not None:
            is_current_generation = options.get('is_current_generation')
            is_instance_storage_supported = options.get('is_instance_storage_supported')

        instances = []

        response = self.__describe_instance_types_page(
            is_current_generation=is_current_generation,
            is_instance_storage_supported=is_instance_storage_supported
        )

        instances += response['InstanceTypes']

        next_token = response.get('NextToken')

        while next_token is not None:
            response = self.__describe_instance_types_page(next_token, is_current_generation,
                                                           is_instance_storage_supported)
            instances += response['InstanceTypes']
            next_token = response.get('NextToken')

        return instances

    def __describe_instance_types_page(self, next_token=None, is_current_generation=None,
                                       is_instance_storage_supported=None):
        filters = [] if is_current_generation is None else [{
            'Name': 'current-generation',
            'Values': [is_current_generation]
        }]

        if is_instance_storage_supported is not None:
            if is_instance_storage_supported:
                filters.append({
                    'Name': 'instance-storage-supported',
                    'Values': ['true']
                })
            else:
                filters.append({
                    'Name': 'instance-storage-supported',
                    'Values': ['false']
                })

        if next_token is not None:
            response = self.__ec2_client.describe_instance_types(
                Filters=filters,
                NextToken=next_token
            )
        else:
            response = self.__ec2_client.describe_instance_types(
                Filters=filters
            )

        return response

    def __filter_ec2_instances(self, instances, options):
        if options is None:
            return []

        filtered_instances = []

        if options.get('cpu') is not None:
            filtered_instances = list(
                filter(lambda ec2_instance: ec2_instance['VCpuInfo']['DefaultVCpus'] >= options.get('cpu'), instances))
        if options.get('memory_gb') is not None:
            filtered_instances = list(
                filter(lambda ec2_instance: ec2_instance['MemoryInfo']['SizeInMiB'] >= options.get('memory_gb') * 1024,
                       filtered_instances))
        if options.get('usage_class') is not None:
            filtered_instances = list(
                filter(lambda ec2_instance: options.get('usage_class') in ec2_instance['SupportedUsageClasses'],
                       filtered_instances))
        if options.get('burstable') is not None:
            filtered_instances = list(
                filter(lambda ec2_instance: options.get('burstable') == ec2_instance['BurstablePerformanceSupported'],
                       filtered_instances))
        if options.get('architecture') is not None:
            filtered_instances = list(
                filter(lambda ec2_instance: options.get('architecture') in ec2_instance['ProcessorInfo'][
                    'SupportedArchitectures'],
                       filtered_instances))
        if options.get('has_gpu') is not None:
            if options['has_gpu']:
                filtered_instances = list(
                    filter(lambda ec2_instance: ec2_instance.get('GpuInfo') is not None, filtered_instances))
                if options.get('gpu_memory') is not None:
                    filtered_instances = list(
                        filter(
                            lambda ec2_instance: int(ec2_instance['GpuInfo']['TotalGpuMemoryInMiB'] / 1024) >= options[
                                'gpu_memory'], filtered_instances))
            else:
                filtered_instances = list(
                    filter(lambda ec2_instance: ec2_instance.get('GpuInfo') is None, filtered_instances))

        return filtered_instances

    def __ec2_instance_price_loop(self, ec2_instance, product_description, availability_zones,
                                  final_spot_price_determination_strategy):
        instance_type = ec2_instance['InstanceType']

        filters = [
            {
                'Name': 'product-description',
                'Values': [product_description]
            }
        ]

        if availability_zones:
            filters.append({
                'Name': 'availability-zone',
                'Values': availability_zones
            })

        response = self.__ec2_client.describe_spot_price_history(
            InstanceTypes=[instance_type],
            Filters=filters
        )

        if len(response['SpotPriceHistory']) == 0:
            return None

        history_events = response['SpotPriceHistory']

        az_price = {}

        if availability_zones is None:
            availability_zones = self.get_all_availability_zones_for_region()

        for i, availability_zone in enumerate(availability_zones):
            for history_event in history_events:
                az = history_event['AvailabilityZone']
                if availability_zone == az:
                    az_price[availability_zone] = history_event['SpotPrice']
                    break

        strategy = final_spot_price_determination_strategy

        values = [float(v) for v in az_price.values()]

        if strategy == 'average':
            spot_price = sum(values) / len(values)
        elif strategy == 'max':
            spot_price = max(values)
        elif strategy == 'min':
            spot_price = min(values)
        else:
            raise Exception(f'The {strategy} strategy is wrong')

        return {
            'price': spot_price,
            'ec2_instance': ec2_instance,
            'az_price': az_price
        }

    def __sort_spot_instances_by_price(self, filtered_instances, product_description, availability_zones,
                                       final_spot_price_determination_strategy):
        pool = self.__Pool(self.__describe_spot_price_history_concurrency)

        results = []

        for ec2_instance in filtered_instances:
            result = pool.apply_async(self.__ec2_instance_price_loop,
                                      (ec2_instance, product_description, availability_zones,
                                       final_spot_price_determination_strategy))
            results.append(result)

        pool.close()
        pool.join()

        ec2_instances = [result.get() for result in results]
        ec2_instances = [ec2_instance for ec2_instance in ec2_instances if ec2_instance is not None]
        ec2_instances.sort(key=operator.itemgetter('price'))

        enriched_instances = []

        for ec2_instance in ec2_instances:
            interruption_frequency = ec2_instance['ec2_instance'].get('interruption_frequency')

            entry = {
                'instance_type': ec2_instance['ec2_instance']['InstanceType'],
                'price': ec2_instance['price'],
                'az_price': ec2_instance['az_price'],
                'vcpu': ec2_instance['ec2_instance']['VCpuInfo']['DefaultVCpus'],
                'memory': int(ec2_instance['ec2_instance']['MemoryInfo']['SizeInMiB'] / 1024),
                'network_performance': ec2_instance['ec2_instance']['NetworkInfo']['NetworkPerformance'],
                'storage': ec2_instance['ec2_instance'].get('InstanceStorageInfo').get('Disks') if ec2_instance[
                    'ec2_instance'].get('InstanceStorageInfo') else 'EBS Only'
            }

            if ec2_instance['ec2_instance'].get('GpuInfo') is not None:
                entry['gpu_memory'] = int(ec2_instance['ec2_instance']['GpuInfo']['TotalGpuMemoryInMiB'] / 1024)

            if interruption_frequency:
                entry['interruption_frequency'] = interruption_frequency

            enriched_instances.append(entry)

        return enriched_instances

    def __sort_on_demand_instances_by_price(self, ec2_instances_input, operating_system):
        ec2_prices = self.__get_ec2_price(operating_system)
        ec2_instances = []

        for ec2_instance_input in ec2_instances_input:
            instance_type = ec2_instance_input['InstanceType']
            price = ec2_prices.get(instance_type)
            if price is not None:
                entry = {
                    'price': ec2_prices[instance_type]['instance_price'],
                    'instance_type': instance_type,
                    'vcpu': ec2_instance_input['VCpuInfo']['DefaultVCpus'],
                    'memory': int(ec2_instance_input['MemoryInfo']['SizeInMiB'] / 1024),
                    'network_performance': ec2_instance_input['NetworkInfo']['NetworkPerformance'],
                    'storage': ec2_instance_input.get('InstanceStorageInfo').get('Disks') if ec2_instance_input.get(
                        'InstanceStorageInfo') else 'EBS Only'
                }

                if ec2_instance_input.get('GpuInfo') is not None:
                    entry['gpu_memory'] = int(ec2_instance_input['GpuInfo']['TotalGpuMemoryInMiB'] / 1024)

                ec2_instances.append(entry)
            else:
                self.__logger.warning(f'Price for the {instance_type} instance type not found')

        ec2_instances.sort(key=operator.itemgetter('price'))

        return ec2_instances

    def __get_ec2_price(self, operating_system):
        next_token = ''
        records = {}
        while next_token is not None:
            response = self.__pricing_client.get_products(
                ServiceCode='AmazonEC2',
                Filters=[
                    {'Type': 'TERM_MATCH', 'Field': 'preInstalledSw', 'Value': 'NA'},
                    # {'Type': 'TERM_MATCH', 'Field': 'storage', 'Value': 'EBS only'},
                    {'Type': 'TERM_MATCH', 'Field': 'productFamily', 'Value': 'Compute Instance'},
                    {'Type': 'TERM_MATCH', 'Field': 'termType', 'Value': 'OnDemand'},
                    {'Type': 'TERM_MATCH', 'Field': 'location', 'Value': self.__REGIONS[self.__region]},
                    {'Type': 'TERM_MATCH', 'Field': 'licenseModel', 'Value': 'No License required'},
                    {'Type': 'TERM_MATCH', 'Field': 'tenancy', 'Value': 'Shared'},
                    {'Type': 'TERM_MATCH', 'Field': 'capacitystatus', 'Value': 'Used'},
                    {'Type': 'TERM_MATCH', 'Field': 'operatingSystem', 'Value': operating_system}
                ],
                NextToken=next_token
            )
            try:
                next_token = response['NextToken']
            except KeyError:
                next_token = None
            for price in response['PriceList']:
                details = json.loads(price)
                pricedimensions = next(iter(details['terms']['OnDemand'].values()))['priceDimensions']
                pricing_details = next(iter(pricedimensions.values()))
                instance_price = float(pricing_details['pricePerUnit']['USD'])
                instance_type = details['product']['attributes']['instanceType']
                if instance_price <= 0:
                    continue
                vcpu = details['product']['attributes']['vcpu']
                memory = details['product']['attributes']['memory'].split(" ")[0]
                os = json.loads(price)['product']['attributes']['operatingSystem']
                records[instance_type] = {
                    'instance_type': instance_type,
                    'vcpu': vcpu,
                    'memory': memory,
                    'os': os,
                    'instance_price': instance_price
                }
        return records

    def __get_operating_system_by_product_description(self, product_description):
        operating_system = self.__OS_PRODUCT_DESCRIPTION_MAP[product_description]
        return operating_system

    def get_hash(self, dictionary):
        dictionary_copy = dictionary.copy()
        dictionary_copy['region'] = self.__region
        dict_string = json.dumps(dictionary_copy)
        hash_object = hashlib.md5(dict_string.encode())
        return hash_object.hexdigest()

    def get_all_availability_zones_for_region(self):
        response = self.__ec2_client.describe_availability_zones()

        availability_zones = []
        for zone in response['AvailabilityZones']:
            availability_zones.append(zone['ZoneName'])

        if len(availability_zones) == 0:
            raise Exception(f'Availability zones not found for the {self.__region} region')

        return availability_zones

    @staticmethod
    def unique(list1):
        list_set = set(list1)
        unique_list = (list(list_set))
        return unique_list

    @staticmethod
    def __get_pool() -> Any:
        if os.environ.get('AWS_LAMBDA_FUNCTION_NAME') is None:
            return ThreadPool
        else:
            return LambdaThreadPool

    @staticmethod
    def __get_client(options: Dict[str, Any], service: str, region: str) -> Any:
        if options.get('clients') is not None and options['clients'].get(service) is not None:
            return options['clients'][service]
        else:
            return boto3.session.Session().client(service, region_name=region)
