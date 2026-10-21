package com.application.demo.AttributeAnalysis;

import java.util.Map;
import org.springframework.stereotype.Service;
import org.springframework.jdbc.core.JdbcTemplate;

import java.util.List;

@Service
public class AttributeAnalysisService {

    private JdbcTemplate jdbcTemplate;

    public AttributeAnalysisService(JdbcTemplate jdbcTemplate) {
        this.jdbcTemplate = jdbcTemplate;
    }


    public String newAttributeSelection(Map<String, Object> formData, String tableName) {
        // Implement the logic for new attribute selection
        try {
            String userId = (String) formData.get("userId");
            String time = (String) formData.get("time");
            String layer = (String) formData.get("attributeLayer");
            String attribute = (String) formData.get("attributeAttribute");
            String conditionStr = (String) formData.get("attributeCondition");
            
            String sign = (String) formData.get("attributeSign");

            List<String> numericAttributes = List.of(
                "jpt_powier", "jpt_powi_1", "shape_leng", "shape_le_1", "shape_area",
                "wspgeog", "wspxy", "liczbamies"
            );

            String sqlSELECT = "";
            String pickedLayer = translateLayer(layer);
            if (pickedLayer.equals("vectorLayer")) {
                pickedLayer = "sql_data";
            }
            
            if (numericAttributes.contains(attribute)) {
                String temp = conditionStr.replace(" ", "").trim();
                double condition = Double.parseDouble(temp.replace(",", "."));
                
                sqlSELECT = "SELECT * FROM \"" + pickedLayer + "\" " +
                "WHERE CAST(\"" + attribute + "\" AS double precision) " +
                sign + " " + condition;

            } else {
                if (sign.equals("=") || sign.equals("!=")) {
                sqlSELECT = "SELECT * FROM \"" + pickedLayer + "\" " +
                    "WHERE \"" + attribute + "\" " +
                    sign + " " + "\'" + conditionStr + "\'"; 
                } else {
                    return "Error: Invalid sign for non-numeric attribute. Only '=' and '!=' are allowed.";
                }
                
            }
            
            
            String sql = "CREATE TABLE " + tableName + " AS " + sqlSELECT;
            jdbcTemplate.execute(sql);
            // PostgreSQL bez cudzysłowów zapisuje nazwy tabel małymi literami!
            // userId ma wielkie litery (np. pel4PIa...) więc trzeba użyć toLowerCase()
            // żeby ALTER TABLE trafił w tabelę o właściwej nazwie.
            String tableNameLower = tableName.toLowerCase();
            jdbcTemplate.execute(
                "ALTER TABLE " + tableNameLower + " ALTER COLUMN wkb_geometry TYPE geometry(Geometry, 3857) USING ST_Transform(ST_SetSRID(wkb_geometry, 2180), 3857)"
            );
            
            

            // SQL command do stworzenia nowej temp_table a potem dodaj to do temp_datastore 
            // uzytkownika i zrob publishLayer. Mniej wiecej tak samo jak w recznym sposobie. Dodaj przycisk zapisu do frontendu 

            System.out.println("Received form data in AttributeAnalysisService: " + formData);
            return "Success creating new ATTRIBUTE SELECTION table for user: " + userId + " at time: " + time;

        } catch (Exception e) {
            e.printStackTrace();
            return "Error creating new ATTRIBUTE SELECTION table: " + e.getMessage();
        }
    }

    public String updateAttributeSelection(Map<String, Object> formData, String tableName) {
        try {
            String userId = (String) formData.get("userId");
            String time = (String) formData.get("time");
            String layer = (String) formData.get("attributeLayer");
            String attribute = (String) formData.get("attributeAttribute");
            String conditionStr = (String) formData.get("attributeCondition");
            String sign = (String) formData.get("attributeSign");

            List<String> numericAttributes = List.of(
                "jpt_powier", "jpt_powi_1", "shape_leng", "shape_le_1", "shape_area",
                "wspgeog", "wspxy", "liczbamies"
            );

            String sqlSELECT = "";

            String pickedLayer = translateLayer(layer);
            
            if (pickedLayer.equals("vectorLayer")) {
                pickedLayer = "sql_data";
            }

            String tableNameLower = tableName.toLowerCase();
            if (numericAttributes.contains(attribute)) {
                String temp = conditionStr.replace(" ", "").trim();
                double condition = Double.parseDouble(temp.replace(",", "."));

                sqlSELECT = "SELECT * FROM \"" + tableNameLower + "\" " +
                "WHERE CAST(\"" + attribute + "\" AS double precision) " +
                sign + " " + condition;
            } else {
                if (sign.equals("=") || sign.equals("!=")) {
                    sqlSELECT = "SELECT * FROM \"" + tableNameLower + "\" " +
                    "WHERE \"" + attribute + "\" " +
                    sign + " " + "\'" + conditionStr + "\'";
                } else {
                    return "Error: Invalid sign for non-numeric attribute. Only '=' and '!=' are allowed.";
                }
            }
            String tempTableName = ("\"tmp_" + userId + "_tempp_table_" + time + "\"").toLowerCase();
            String sql = "BEGIN; CREATE TEMP TABLE " + tempTableName +
            " ON COMMIT DROP AS " + sqlSELECT + "; DROP TABLE IF EXISTS \"" + tableNameLower + "\"; " +
            "CREATE TABLE \"" + tableNameLower + "\" AS SELECT * FROM pg_temp." + tempTableName + 
            "; COMMIT;";
            jdbcTemplate.execute(sql);

            return "Success updating ATTRIBUTE SELECTION table for user: " + userId + " at time: " + time;
        } catch (Exception e) {
            e.printStackTrace();
            throw new RuntimeException("Error updating ATTRIBUTE SELECTION table: " + e.getMessage());
        }

        // Implement the logic for updating attribute selection
    }
    
    public List<Map<String, Object>> getSelection(String tableName) {
        List<Map<String,Object>> result = jdbcTemplate.queryForList("SELECT * FROM \"" + tableName.toLowerCase() + "\"");
        result.forEach(row -> row.remove("wkb_geometry"));
        return result;
    } 

    public List<Map<String, Object>> getPickedLayer(String pickedTable) {
        String tableName = translateLayer(pickedTable);
        List<Map<String, Object>> result = jdbcTemplate.queryForList("SELECT * FROM \"" + tableName.toLowerCase() + "\"");
        result.forEach(row -> row.remove("wkb_geometry"));
        return result;
    }

    private String translateLayer(String layer) {
        switch (layer) {
            case "boundsLayerPanstwo":
                return "boundspanstwo";
            case "boundsLayerWojewodz":
                return "boundswojewodz";
            case "boundsLayerPowiaty":
                return "boundspowiaty";
            case "boundsLayerGminy":
                return "boundsgminy";
            case "boundsLayerCities":
                return "boundscities";
            case "vectorLayer":
                return "sql_data";
        }
        return "Wrong attribute layer name" + layer;
    }

    public String deleteTableFromSelection(String oldUserId, String oldTime) {
        String tableName = "user_" + oldUserId + "_temp_table_" + oldTime;
        String sql = "DROP TABLE IF EXISTS " + tableName;
        jdbcTemplate.execute(sql);
        
        // Delete the corresponding layer from GeoServer
        
        return tableName;
    }
    // Implement the service methods for attribute analysis here
}


