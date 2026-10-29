package com.application.demo.AttributeAnalysis;
import com.application.demo.GeoServerService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.HashMap;
import java.util.Map;
import java.util.List;

@RestController
@RequestMapping("/attribute-analysis")
public class AttributeAnalysisController {
    
    private final AttributeAnalysisService attributeAnalysisService;
    private final GeoServerService geoServerService;

    public AttributeAnalysisController(AttributeAnalysisService attributeAnalysisService, GeoServerService geoServerService) {
        this.attributeAnalysisService = attributeAnalysisService;
        this.geoServerService = geoServerService;
    }

    @PostMapping("/new-attribute-selection")
    public ResponseEntity<?> newAttribute(@RequestParam Map<String, Object> formData) {
        System.out.println("Received form data at AttributeController: " + formData);
        Map<String, Object> attributeFormData = new HashMap<>();

        attributeFormData.put("attributeLayer", formData.get("attributeLayer"));
        attributeFormData.put("attributeAttribute", formData.get("attributeAttribute"));
        attributeFormData.put("attributeSign", formData.get("attributeSign"));
        attributeFormData.put("attributeCondition", formData.get("attributeCondition"));
        attributeFormData.put("userId", formData.get("userId"));
        attributeFormData.put("time", formData.get("time"));
        String userId = (String) formData.get("userId");
        String time = (String) formData.get("time");

        String tableName = "user_" + userId + "_temp_table_" + time;
        String response = null;
        try {
            response = attributeAnalysisService.newAttributeSelection(attributeFormData, tableName);

            if (response.startsWith("Error")) {
                return ResponseEntity.badRequest().body("Error: Invalid attribute selection.");
            } 
        } catch (Exception e) {
            return ResponseEntity.badRequest().body("Error: " + e.getMessage());
            
        }

        try {
            geoServerService.publishLayer(tableName, tableName, userId);
        } catch (Exception e) {
            return ResponseEntity.badRequest().body("Error publishing layer: " + e.getMessage());
        }




        //Deletion of temp table is handled already in return-button 

        return ResponseEntity.ok("TTTTTTTYYYYYPEEE" + response);
    }

    @PostMapping("/update-attribute-selection")
    public ResponseEntity<?> updateAttribute(@RequestParam Map<String, Object> formData) {
        System.out.println("Received form data at AttributeController: " + formData);
        Map<String, Object> attributeFormData = new HashMap<>();

        attributeFormData.put("attributeLayer", formData.get("attributeLayer"));
        attributeFormData.put("attributeAttribute", formData.get("attributeAttribute"));
        attributeFormData.put("attributeSign", formData.get("attributeSign"));
        attributeFormData.put("attributeCondition", formData.get("attributeCondition"));
        attributeFormData.put("userId", formData.get("userId"));
        attributeFormData.put("time", formData.get("time"));
        String userId = (String) formData.get("userId");
        String time = (String) formData.get("time");
        String tableName = "user_" + userId + "_temp_table_" + time;

        try {
            String response = attributeAnalysisService.updateAttributeSelection(attributeFormData, tableName);
            if (response.startsWith("Error")) {
                return ResponseEntity.badRequest().body("Error: Invalid attribute selection.");
            }
        } catch (Exception e) {
            return ResponseEntity.badRequest().body("Error: " + e.getMessage());
        }

        try {
            geoServerService.deleteLayer(tableName, userId);
            geoServerService.publishLayer(tableName, tableName, userId);
        } catch (Exception e) {
            return ResponseEntity.badRequest().body("Error publishing layer: " + e.getMessage());
        }



        return ResponseEntity.ok().build();
    }

    @GetMapping ("/get-attribute-selection")
    public ResponseEntity<?> getAttribute(@RequestParam String tableName) {
        try {
            List<Map<String, Object>> result = attributeAnalysisService.getSelection(tableName);
            return ResponseEntity.ok(result);
        } catch (Exception e) {
            return ResponseEntity.status(500).body("Error getting attribute selection: " + e.getMessage());
        }
    }

    @GetMapping ("/get-picked-layer")
    public ResponseEntity<?> getPickedLayer(@RequestParam String pickedTable) {
        try {
            List<Map<String, Object>> result = attributeAnalysisService.getPickedLayer(pickedTable);
            return ResponseEntity.ok(result);
        } catch (Exception e) {
            return ResponseEntity.status(500).body("Error getting picked layer: " + e.getMessage());
        }
    }

    @PostMapping ("/check-query")
    public ResponseEntity<?> checkQuery(@RequestParam Map<String, Object> formData) {
        Map<String, Object> attributeFormData = new HashMap<>();

        attributeFormData.put("attributeLayer", formData.get("attributeLayer"));
        attributeFormData.put("attributeAttribute", formData.get("attributeAttribute"));
        attributeFormData.put("attributeSign", formData.get("attributeSign"));
        attributeFormData.put("attributeCondition", formData.get("attributeCondition"));
        attributeFormData.put("userId", formData.get("userId"));
        attributeFormData.put("time", formData.get("time"));
        attributeFormData.put("caseString", formData.get("caseString"));

        try {
            String response = attributeAnalysisService.checkQuery(attributeFormData);
            if (response.startsWith("Error")) {
                return ResponseEntity.badRequest().body("Error: Invalid query.");
            }
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            return ResponseEntity.status(500).body("Error checking query: " + e.getMessage());
        }
    }

    @DeleteMapping ("/delete-attribute-selection")
    public ResponseEntity<?> deleteAttribute(@RequestParam String oldUserId, @RequestParam String oldTime) {
        try {
            String tableName = attributeAnalysisService.deleteTableFromSelection(oldUserId, oldTime);
            geoServerService.deleteLayer(tableName, oldUserId);
            return ResponseEntity.ok("Successfully deleted table for user: " + oldUserId + " at time: " + oldTime);
        } catch (Exception e) {
            return ResponseEntity.status(500).body("Error deleting table: " + e.getMessage());
        }   
    }
}