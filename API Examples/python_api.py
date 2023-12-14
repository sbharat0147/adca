from django.apps import apps
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
from django.db.models import Q
from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist

def build_dynamic_filter(column_name, operator, column_value):
    filter_kwargs = {}

    if operator == '>':
        filter_kwargs[f'{column_name}__gt'] = column_value
    elif operator == '<':
        filter_kwargs[f'{column_name}__lt'] = column_value
    elif operator == '=':
        filter_kwargs[column_name] = column_value
    elif operator == '>=':
        filter_kwargs[f'{column_name}__gte'] = column_value
    elif operator == '<=':
        filter_kwargs[f'{column_name}__lte'] = column_value
    elif operator in ('!=', '<>'):
        filter_kwargs[f'{column_name}__ne'] = column_value
    else:
        raise ValueError(f"Invalid operator: {operator}")

    return Q(**filter_kwargs)

@csrf_exempt
def data_export_generic_api(request):
    if request.method == 'POST':
        data = request.POST  # If using POST request
    elif request.method == 'GET':
        data = request.GET  # If using GET request
    else:
        return JsonResponse({'error_message': 'Method not allowed.'}, status=405)
    
    try:
        # Parse the request data and validate it
        table_name = data.get('table_name')
        filters = data.get('filters', [])
        page_size = int(data.get('page_size', 1000))
        page_number = int(data.get('page_number', 1))
        order_by = data.get('order_by', [])
        
        # Get the model dynamically based on the table_name
        model = apps.get_model(app_label='your_app', model_name=table_name)
        
        if model is None:
            raise ObjectDoesNotExist(f"Model '{table_name}' not found")

        # Apply filters and fetch data from the database
        queryset = model.objects.all()
        date_time_columns = ["CREATED_AT", "UPDATED_AT", "DELETED_AT"]
        
        for filter_item in filters:
            column_name = filter_item['column_name']
            operator = filter_item['operator']
            # Check if the column_name is in the list of date-time columns
            if column_name in date_time_columns:
                # Apply date-time formatting
                column_value = datetime.strptime(filter_item['column_value'], '%d-%m-%Y %H:%M:%S')
            else:
                # No formatting needed for other columns
                column_value = filter_item['column_value']
            filter_q = build_dynamic_filter(column_name, operator, column_value)
            queryset = queryset.filter(filter_q)
            
        total_records = queryset.count()

        # Apply ordering
        for order_item in order_by:
            column_name = order_item['column_name']
            order = order_item['order']
            if order == 'ASC':
                queryset = queryset.order_by(column_name)
            elif order == 'DESC':
                queryset = queryset.order_by(f'-{column_name}')

        # Paginate the data
        start_index = (page_number - 1) * page_size
        end_index = start_index + page_size
        paginated_data = queryset[start_index:end_index]

        # Serialize the paginated data using Django's serializers
        serialized_data = serializers.serialize('json', paginated_data)

        response_data = {
            'table_name': table_name,
            'response_time': datetime.now().strftime('%d-%m-%Y %H:%M:%S'),
            'data': serialized_data,
            'total': total_records,
            'page_size': page_size,
            'page_number': page_number
        }

        return JsonResponse(response_data)

    except ObjectDoesNotExist as e:
        error_response = {
            'table_name': table_name,
            'response_time': datetime.now().strftime('%d-%m-%Y %H:%M:%S'),
            'error_code': 404,
            'error_message': str(e),
        }

        return JsonResponse(error_response, status=404)
    except ValueError as e:
        error_response = {
            'table_name': table_name,
            'response_time': datetime.now().strftime('%d-%m-%Y %H:%M:%S'),
            'error_code': 400,
            'error_message': str(e),
        }

        return JsonResponse(error_response, status=400)
    except Exception as e:
        error_response = {
            'table_name': table_name,
            'response_time': datetime.now().strftime('%d-%m-%Y %H:%M:%S'),
            'error_code': 500,
            'error_message': str(e),
        }

        return JsonResponse(error_response, status=500)
