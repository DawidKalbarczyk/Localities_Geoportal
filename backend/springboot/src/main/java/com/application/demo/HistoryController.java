package com.application.demo;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.web.bind.annotation.*;
import tools.jackson.databind.ObjectMapper;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/history-service")
public class HistoryController {
    private final JdbcTemplate jdbcTemplate;
    private final ObjectMapper objectMapper;

    public HistoryController(JdbcTemplate jdbcTemplate, ObjectMapper objectMapper) {
        this.jdbcTemplate = jdbcTemplate;
        this.objectMapper = objectMapper;
    }

    @GetMapping("/get-history")
    public ResponseEntity<?> getHistory(@RequestParam String tableName) {
        try {
            String sql = """
                SELECT 'SELECT '
                    || string_agg(
                        CASE WHEN column_name = 'wkb_geometry'
                            THEN 'ST_AsGeoJSON(ST_Transform(wkb_geometry, 4326)) AS wkb_geometry'
                            ELSE quote_ident(column_name)
                        END, ', ' ORDER BY ordinal_position)
                    || ' FROM ' || quote_ident(table_name) AS generated_query
                FROM information_schema.columns
                WHERE table_name = ?
                  AND table_schema = 'public'
                GROUP BY table_name
                """;
            List<String> queries = jdbcTemplate.queryForList(sql, String.class, tableName.toLowerCase());

            if (queries.isEmpty()) {
                return ResponseEntity.status(HttpStatus.NOT_FOUND)
                        .body(Map.of("error", "Table not found: " + tableName));
            }

            List<Map<String, Object>> rows = jdbcTemplate.queryForList(queries.get(0));

            for (Map<String, Object> row: rows) {
                Object geom = row.get("wkb_geometry");
                if (geom != null) {
                    row.put("wkb_geometry", objectMapper.readTree(geom.toString()));
                }
            }
            return ResponseEntity.ok(Map.of("data", rows));
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(Map.of("error", "Error fetching history: " + e.getMessage()));
        }
    }
}