package com.application.demo;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.util.Map;


@RestController
@RequestMapping("/save")
public class DataSaveController {

    private final DataSaveService dataSaveService;

    public DataSaveController(DataSaveService dataSaveService) {
        this.dataSaveService = dataSaveService;
    }

    @GetMapping("/get-xml-as-json")
    public ResponseEntity<?> getXmlAsJson(@RequestParam String url) {
        try {
            ResponseEntity<?> result = dataSaveService.getXMLasJSON(url);
            if (result.getStatusCode() != HttpStatus.OK) {
                return result;
            }
            return result;
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(Map.of("error", "Error retrieving XML as JSON: " + e.getMessage()));
        }
    }

    @PostMapping("/selected-objects")
    public ResponseEntity<?> saveSelectedObjects(
            @RequestParam String oldUserId,
            @RequestParam String oldTime,
            @RequestParam String title,
            @RequestParam String type,
            @RequestParam String userId,
            @RequestParam String time,
            @RequestParam String layer,
            @RequestParam String ids) {
        try {
            ResponseEntity<?> resultDeletingTempTable = dataSaveService.deleteTableFromSelection(oldUserId, oldTime);
            if (resultDeletingTempTable.getStatusCode() != HttpStatus.OK) {
                return resultDeletingTempTable;
            }
        // UPDATING THE JSON ARRAY IN THE DATABASE////////////////////////////////////////
            ResponseEntity<?> resultSavingJSON = dataSaveService.updateJSONinTable(title, userId, time, type, layer);
            if (resultSavingJSON.getStatusCode() != HttpStatus.OK) {
                return resultSavingJSON;
            }
        ////////////////////////////////////////////////////////////////////////////////////////
        // SAVING SELECTED LAYER AS A TABLE IN DATABASE ////////////////////////////////////////////////////
            ResponseEntity<?> resultSavingDB = dataSaveService.saveObjInDatabase(layer, ids, userId, time);
            if (resultSavingDB.getStatusCode() != HttpStatus.OK) {
                return resultSavingDB;
            }
        ////////////////////////////////////////////////////////////////////////////////////////
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(Map.of("error", "Error saving selected objects: " + e.getMessage()));
        }
        

        return ResponseEntity.ok().body(Map.of("message", "Selected objects saved successfully")); 
    }

    @GetMapping("/get-json")
    public ResponseEntity<?> getJson(@RequestParam String userId) {
        try {
            ResponseEntity<?> result = dataSaveService.getJsonFromDatabase(userId);
            if (result.getStatusCode() != HttpStatus.OK) {
                return result;
            }
            return result;
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(Map.of("error", "Error retrieving JSON from the database: " + e.getMessage()));
        }
    }

    @PostMapping("/publish-layer")
    public ResponseEntity<?> publishLayer(
            @RequestParam String userId,
            @RequestParam String time,
            @RequestParam(required = false) String layer) {
        try {
            ResponseEntity<?> result = dataSaveService.publishLayer(userId, time, layer);
            if (result.getStatusCode() != HttpStatus.OK) {
                return result;
            }
            return result;
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body(Map.of("error", "Error publishing layer: " + e.getMessage()));
        }
    }
}