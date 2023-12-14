import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.web.bind.annotation.*;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.RequestBody;
import javax.persistence.EntityNotFoundException;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.Date;
import java.util.HashMap;
import java.io.IOException;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

@RestController
@RequestMapping("/data-export-generic-api")
public class DataExportController {

    @Autowired
    private ObjectMapper objectMapper;

    @Autowired
    private JdbcTemplate jdbcTemplate;

    @PostMapping
    public ResponseEntity<?> dataExportGenericApi(@Validated @RequestBody JsonNode requestData) {
        String tableName = requestData.get("table_name").asText();
        DateTimeFormatter responseTimeFormatter = DateTimeFormatter.ofPattern("dd-MM-yyyy HH:mm:ss");
        String responseTime = LocalDateTime.now().format(responseTimeFormatter);


        Map<String, Object> response = new HashMap<>();

        try {
            List<Filter> filters = new ArrayList<>();
            int pageSize = requestData.has("page_size") ? requestData.get("page_size").asInt() : 1000;
            int pageNumber = requestData.has("page_number") ? requestData.get("page_number").asInt() : 1;
            JsonNode orderBy = requestData.has("order_by") ? requestData.get("order_by") : null;

            List<Map<String, Object>> result = getSqlQueryResult(tableName, filters, orderBy, page_number, page_size);

            int totalRecords = result.size();
            String jsonData = objectMapper.writeValueAsString(result);

            response.put("table_name", tableName);
            response.put("response_time", responseTime);
            response.put("data", jsonData);
            response.put("total", totalRecords);
            response.put("page_size", pageSize);
            response.put("page_number", pageNumber);

            return ResponseEntity.ok(response);
        } catch (EntityNotFoundException e) {
            return handleErrorResponse(HttpStatus.NOT_FOUND, e, tableName, responseTime);
        } catch (IllegalArgumentException | IOException e) {
            return handleErrorResponse(HttpStatus.BAD_REQUEST, e, tableName, responseTime);
        } catch (Exception e) {
            return handleErrorResponse(HttpStatus.INTERNAL_SERVER_ERROR, e, tableName, responseTime);
        }
    }

    private ResponseEntity<Map<String, Object>> handleErrorResponse(HttpStatus status, Exception e, String tableName, String responseTime) {
        Map<String, Object> errorResponse = new HashMap<>();
        errorResponse.put("table_name", tableName);
        errorResponse.put("response_time", responseTime); // Formatted date
        errorResponse.put("error_code", status.value());
        errorResponse.put("error_message", e.getMessage());
        return ResponseEntity.status(status).body(errorResponse);
    }

    private List<Map<String, Object>> getSqlQueryResult(String tableName, List<Filter> filters, JsonNode orderBy, int page_number, int page_size) {

        // Construct the SQL query using parameterized queries
        StringBuilder sqlQuery = new StringBuilder("SELECT * FROM ").append(tableName);

        List<Object> parameters = new ArrayList<>();

        if (!filters.isEmpty()) {
            sqlQuery.append(" WHERE ");
            for (int i = 0; i < filters.size(); i++) {
                Filter filter = filters.get(i);
                sqlQuery.append(filter.getColumn_name())
                        .append(" ")
                        .append(filter.getOperator())
                        .append(" ?"); // Use parameterized queries to prevent SQL injection

                // Add the filter value as a parameter
                parameters.add(filter.getColumn_value());

                if (i < filters.size() - 1) {
                    sqlQuery.append(" AND ");
                }
            }
        }

        if (orderBy != null && !orderBy.isEmpty()) {
            sqlQuery.append(" ORDER BY ");
            for (JsonNode orderItem : orderBy) {
                String column = orderItem.get("column_name").asText();
                String orderDirection = orderItem.get("order").asText();
                sqlQuery.append(column).append(" ").append(orderDirection);

                if (orderItem != orderBy.get(orderBy.size() - 1)) {
                    sqlQuery.append(", ");
                }
            }
        }

        // Add the LIMIT and OFFSET as parameters
        sqlQuery.append(" LIMIT ? OFFSET ?");
        int offset = (pageNumber - 1) * pageSize;
        parameters.add(pageSize);
        parameters.add(offset);

        // Now you can use the parameters list to pass the values to jdbcTemplate
        Object[] paramsArray = parameters.toArray();

        
        // Execute the SQL query
        List<Map<String, Object>> result = jdbcTemplate.queryForList(sqlQuery, paramsArray);

        return result;
    }

    public static class Filter {
        private String column_name;
        private String operator;
        private String column_value;

        public String getColumn_name() {
            return column_name;
        }

        public void setColumn_name(String column_name) {
            this.column_name = column_name;
        }

        public String getOperator() {
            return operator;
        }

        public void setOperator(String operator) {
            this.operator = operator;
        }

        public String getColumn_value() {
            return column_value;
        }

        public void setColumn_value(String column_value) {
            this.column_value = column_value;
        }
    }

}
