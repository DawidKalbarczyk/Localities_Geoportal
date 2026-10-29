package com.application.demo;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.HashMap;
import java.util.Map;
import java.util.List;

@Service
public class DataSaveService {
    private final JdbcTemplate jdbcTemplate;
    private final ObjectMapper objectMapper = new ObjectMapper();
    private final GeoServerService geoServerService;
    private final RestTemplate restTemplate = new RestTemplate();

    @Value("${geoserver.url}")
    private String geoserverUrl;

    @Value("${geoserver.username}")
    private String username;

    @Value("${geoserver.password}")
    private String password;

    @Value ("${spring.datasource.db}")
    private String dbName;

    @Value ("${spring.datasource.username}")
    private String dbUsername;

    @Value ("${spring.datasource.password}")
    private String dbPassword;

    public DataSaveService(JdbcTemplate jdbcTemplate, GeoServerService geoServerService) {
        this.jdbcTemplate = jdbcTemplate;
        this.geoServerService = geoServerService;
    }

    public ResponseEntity<?> updateJSONinTable(String title, String userId, String time, String type, String layer) {
        try {
            Map<String, Object> payload = new HashMap<>();
                payload.put("title", title);
                payload.put("userId", userId);
                payload.put("time", time);
                payload.put("type", type);
                payload.put("layer", layer);

                String json = objectMapper.writeValueAsString(payload);

                String sql = "UPDATE users SET json = array_append(json, ?::json) WHERE id = ?";
                int rows = jdbcTemplate.update(sql, json, userId);

                if (rows == 0) {
                    return ResponseEntity.status(HttpStatus.NOT_FOUND)
                            .body(Map.of("error", "Nie znaleziono użytkownika o podanym id"));
                }
            return ResponseEntity.ok().body(Map.of("message", "Selected objects saved successfully into JSON array"));
        } catch (JsonProcessingException e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(Map.of("error", "Error processing JSON: " + e.getMessage()));
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(Map.of("error", "Error updating JSON in the database: " + e.getMessage()));
        }
    }

    public ResponseEntity<?> saveObjInDatabase(String layer, String ids, String userId, String time) {
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
            String sqlSELECT = "SELECT * FROM \"" + layerMapComponentName + "\" WHERE ogc_fid IN (" + ids + ")";
            String tableName = "user_" + userId + "_perm_table_" + time;
            String sql = "CREATE TABLE " + tableName + " AS " + sqlSELECT;
            jdbcTemplate.execute(sql);
            // PostgreSQL bez cudzysłowów zapisuje nazwy tabel małymi literami!
            // userId ma wielkie litery (np. pel4PIa...) więc trzeba użyć toLowerCase()
            // żeby ALTER TABLE trafił w tabelę o właściwej nazwie.
            String tableNameLower = tableName.toLowerCase();
            jdbcTemplate.execute(
                "ALTER TABLE " + tableNameLower + " ALTER COLUMN wkb_geometry TYPE geometry(Geometry, 3857) USING ST_Transform(ST_SetSRID(wkb_geometry, 2180), 3857)"
            );
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(Map.of("error", "Error creating PERMANENT table from selection: " + e.getMessage()));
        } 
        return ResponseEntity.ok().body(Map.of("message", "Selected objects saved successfully in the database PERMANENTLY"));
    }

    public ResponseEntity<?> deleteTableFromSelection(String oldUserId, String oldTime) {
        try {
            String tableName = "user_" + oldUserId + "_temp_table_" + oldTime;
            String sql = "DROP TABLE IF EXISTS " + tableName;
            jdbcTemplate.execute(sql);
            
            // Delete the corresponding layer from GeoServer
            geoServerService.deleteLayer(tableName, oldUserId);
            
            return ResponseEntity.ok(Map.of("message", "Table deleted successfully"));
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(Map.of("error", "Error deleting table: " + e.getMessage()));
        }
    }

    public ResponseEntity<?> publishLayer(String userId, String time, String layer) {
        try {
            String tableName = "user_" + userId + "_perm_table_" + time;
            String title = tableName;
            String style = determineStyle(layer);
            publishLayerCore(tableName, title, userId, style);
            return ResponseEntity.ok(Map.of("message", "Layer published successfully"));
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(Map.of("error", "Error publishing layer: " + e.getMessage()));
        }
    }

    private String determineStyle(String layer) {
        if (layer == null) return "generic";
        return switch (layer) {
            case "boundsLayerPanstwo" -> "boundsPanstwo";
            case "boundsLayerWojewodz" -> "boundsWojewodz";
            case "boundsLayerPowiaty" -> "boundsPowiaty";
            case "boundsLayerGminy" -> "boundsGminy";
            case "boundsLayerCities" -> "boundsCities";
            case "vectorLayer" -> "pointLayer";
            default -> "generic";
        };
    }

    public void publishLayerCore(String tableName, String title, String userId, String styleName) {
        String url = geoserverUrl + "/rest/workspaces/user_" + userId
                + "/datastores/user_" + userId + "/featuretypes"
                + "?recalculate=nativebbox,latlonbbox";

        String body = """
                {
                  "featureType": {
                    "name": "%s",
                    "nativeName": "%s",
                    "title": "%s",
                    "srs": "EPSG:3857",
                    "nativeCRS": "EPSG:3857",
                    "enabled": true
                  }
                }
                """.formatted(tableName, tableName.toLowerCase(), title);

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        headers.setBasicAuth(username, password);

        HttpEntity<String> entity = new HttpEntity<>(body, headers);

        ResponseEntity<String> response = restTemplate.postForEntity(url, entity, String.class);

        if (!response.getStatusCode().is2xxSuccessful()) {
            throw new RuntimeException("GeoServer error: " + response.getStatusCode());
        }

        if (styleName != null && !styleName.isBlank()) {
            setLayerStyle(tableName, userId, styleName);
        }
    }


    public void setLayerStyle(String tableName, String userId, String styleName) {
        try {
            String layerUrl = geoserverUrl + "/rest/layers/user_" + userId + ":" + tableName;
            String body = """
                    {
                      "layer": {
                        "defaultStyle": {
                          "name": "%s"
                        }
                      }
                    }
                    """.formatted(styleName);

            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.APPLICATION_JSON);
            headers.setBasicAuth(username, password);

            HttpEntity<String> entity = new HttpEntity<>(body, headers);
            restTemplate.put(layerUrl, entity);
        } catch (Exception e) {
            // Jeśli styl nie istnieje w GeoServerze, warstwa zachowa styl generic
        }
    }

    public ResponseEntity<?> getJsonFromDatabase(String userId) {
        try {
            String sql = "SELECT COALESCE(array_to_json(json)::text, '[]') FROM users WHERE id = ?";
            List<String> list = jdbcTemplate.queryForList(sql, String.class, userId);
            if (list.isEmpty()) {
                return ResponseEntity.status(HttpStatus.NOT_FOUND)
                        .body(Map.of("error", "Nie znaleziono użytkownika o podanym id"));
            }
            String rawJson = list.get(0);
            Object parsedJson = objectMapper.readValue(rawJson, Object.class);
            return ResponseEntity.ok().body(Map.of("json", parsedJson));
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(Map.of("error", "Error retrieving JSON from the database: " + e.getMessage()));
        }
    }

    public ResponseEntity<?> getXMLasJSON(String url) {
        try {
            HttpHeaders headers = new HttpHeaders();
            headers.setBasicAuth(username, password);
            HttpEntity<String> entity = new HttpEntity<>(headers);

            ResponseEntity<String> response = restTemplate.exchange(url, HttpMethod.GET, entity, String.class);

            if (!response.getStatusCode().is2xxSuccessful()) {
                return ResponseEntity.status(response.getStatusCode())
                        .body(Map.of("error", "GeoServer error: " + response.getStatusCode()));
            }

            String jsonContent = response.getBody();
            Object parsed = objectMapper.readValue(jsonContent, Object.class);
            return ResponseEntity.ok().body(parsed);
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(Map.of("error", "Error retrieving XML from GeoServer: " + e.getMessage()));
        }
    }

}