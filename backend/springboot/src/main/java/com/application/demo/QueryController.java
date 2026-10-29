package com.application.demo;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;
import org.springframework.jdbc.core.JdbcTemplate;


import java.util.HashMap;
import java.util.Map;
import java.util.List;

@RestController
@RequestMapping("/query")
public class QueryController {

    @Autowired
    private JdbcTemplate jdbcTemplate;

    @GetMapping("/get_query") 
    public Map<String, Object> getQuery(@RequestParam String searchTerm) {
        Map<String, Object> response = new HashMap<>();
        try {
            String sql = "SELECT idprng, ST_AsGeoJSON(ST_Transform(wkb_geometry, 4326)), nazwa, rodzaj, powiat, gmina FROM sql_data WHERE nazwa ILIKE ?";
            String pattern = "%" + searchTerm + "%";
            List<Map<String, Object>> results = jdbcTemplate.queryForList(sql, pattern);
            response.put("data", results);
        } catch (Exception e) {
            response.put("status", "error");
            response.put("message", e.getMessage());
        }
        return response;
    }
}
