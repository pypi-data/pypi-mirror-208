SERVICES_COVERED_MAP = {
    # Lambda Client
    "lambda": ['invoke', 'invoke_async'],

    # DynamoDb Client
    "dynamodb": ['batch_get_item', 'batch_write_item', 'create_table', 'delete_table', 'delete_item',
                 'get_item', 'put_item', 'update_item']
}