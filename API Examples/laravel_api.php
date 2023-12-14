<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Carbon\Carbon;

# -- put this below line of code in your routes file ---
# Route::post('/data-export-generic-api', 'DataExportController@exportData');

class DataExportController extends Controller
{
    public function exportData(Request $request)
    {
        try {

            // Validate the incoming request data
            $request->validate([
                'table_name' => 'required|string',
                'filters' => 'required|array',
                'page_size' => 'integer',
                'page_number' => 'integer',
                'order_by' => 'array',
            ]);

            // Process the request
            $tableName = $request->input('table_name');
            $filters = $request->input('filters');
            $pageSize = $request->input('page_size', 1000); // Default to 10 if not provided
            $pageNumber = $request->input('page_number', 1); // Default to 1 if not provided
            $orderBy = $request->input('order_by', []);

            // Construct the base query
            $query = DB::table($tableName);

            // Apply filters
            foreach ($filters as $filter) {
                $column = $filter['column_name'];
                $operator = $filter['operator'];
                $value = $filter['column_value'];

                // Check if the column name is one of 'CREATED_AT', 'UPDATED_AT', or 'DELETED_AT'
                if (in_array($column, ['CREATED_AT', 'UPDATED_AT', 'DELETED_AT'])) {
                    $value = Carbon::createFromFormat('d-m-Y H:i:s', $value);
                }
                
                $query->where($column, $operator, $value);
            }

            // Add pagination
            $query->skip(($pageNumber - 1) * $pageSize)->take($pageSize);

            // Add order by
            foreach ($orderBy as $order) {
                $query->orderBy($order['column_name'], $order['order']);
            }

            // Execute the query
            $results = $query->get();

            $response = [
                'table_name' => $tableName,
                'response_time' => Carbon::now()->format('d-m-Y H:i:s'),
                'data' => $results,
                'total' => count($results),
                'page_size' => $pageSize,
                'page_number' => $pageNumber,
            ];
            return response()->json($response);
        } catch (\Exception $e) {
            // Handle exceptions and return an error response
            $errorResponse = [
                'table_name' => $request->input('table_name'),
                'response_time' => Carbon::now()->format('d-m-Y H:i:s'),
                'error_code' => $e->getCode(),
                'error_message' => $e->getMessage(),
            ];

            return response()->json($errorResponse, 500); // You can adjust the HTTP status code as needed
        }
    }
}
