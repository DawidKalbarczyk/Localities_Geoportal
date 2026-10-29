package com.application.demo;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.jdbc.core.JdbcTemplate;

import java.util.HashMap;
import java.util.Map;
import java.util.List;

@RestController
@RequestMapping("/analysys")
public class AnalysysController {
    private final JdbcTemplate jdbcTemplate;
    private final GeoServerService geoServerService;


    public AnalysysController(JdbcTemplate jdbcTemplate, GeoServerService geoServerService) {
        this.jdbcTemplate = jdbcTemplate;
        this.geoServerService = geoServerService;
    }

    @GetMapping("/get_analysys")
    public Map<String, Object> getAnalysys(@RequestParam String searchTerm) {
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

    @PostMapping("/create-layer")
    public ResponseEntity<?> createLayer(@RequestBody LayerRequest layerRequest) {
        try {
            geoServerService.publishLayer(layerRequest.tableName(), layerRequest.title(), layerRequest.userId());

            return ResponseEntity.ok(Map.of("message", "Layer created successfully"));
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(Map.of("error", "Error creating layer: " + e.getMessage()));
        }
    }

    @PostMapping("/create-table-from-selection")
    public ResponseEntity<?> createTableFromSelection(@RequestParam String userId, @RequestParam String layer, @RequestParam String ids, @RequestParam String time) {
        try {
            String layerMapComponentName;   
            switch (layer) {
                case "boundsLayerPanstwo": 
                    layerMapComponentName = "boundspanstwo";
                    break;
                case "boundsLayerWojewodz": 
                    layerMapComponentName = "boundswojewodz";
                    break;
                case "boundsLayerPowiaty":
                    layerMapComponentName = "boundspowiaty";
                    break;
                case "boundsLayerGminy":
                    layerMapComponentName = "boundsgminy";
                    break;
                case "boundsLayerCities":
                    layerMapComponentName = "boundscities";
                    break;
                case "vectorLayer":
                    layerMapComponentName = "sql_data";
                    break;
                default:
                    layerMapComponentName = layer;
            }
            String sqlSELECT = "SELECT * FROM \"" + layerMapComponentName + "\" WHERE ogc_fid IN " + ids;
            String tableName = "user_" + userId + "_temp_table_" + time;
            String sql = "CREATE TABLE " + tableName + " AS " + sqlSELECT;
            jdbcTemplate.execute(sql);
            // PostgreSQL bez cudzysłowów zapisuje nazwy tabel małymi literami!
            // userId ma wielkie litery (np. pel4PIa...) więc trzeba użyć toLowerCase()
            // żeby ALTER TABLE trafił w tabelę o właściwej nazwie.
            String tableNameLower = tableName.toLowerCase();
            jdbcTemplate.execute(
                "ALTER TABLE " + tableNameLower + " ALTER COLUMN wkb_geometry TYPE geometry(Geometry, 3857) USING ST_Transform(ST_SetSRID(wkb_geometry, 2180), 3857)"
            );
            return ResponseEntity.ok(Map.of("message", "Table created successfully"));
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(Map.of("error", "Error creating table from selection: " + e.getMessage()));
        } 
    }

    @DeleteMapping("/delete-table-from-selection")
    public ResponseEntity<?> deleteTableFromSelection(@RequestParam String userId, @RequestParam String time) {
        try {
            String tableName = "user_" + userId + "_temp_table_" + time;
            String sql = "DROP TABLE IF EXISTS " + tableName;
            jdbcTemplate.execute(sql);
            
            // Delete the corresponding layer from GeoServer
            geoServerService.deleteLayer(tableName, userId);
            
            return ResponseEntity.ok(Map.of("message", "Table deleted successfully"));
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(Map.of("error", "Error deleting table: " + e.getMessage()));
        }
    }

    //Kolejny PostMapping do updatu selection

}

