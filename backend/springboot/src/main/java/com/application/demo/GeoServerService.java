package com.application.demo;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.web.client.HttpClientErrorException;
import org.springframework.web.client.RestClientResponseException;
import org.springframework.web.client.RestTemplate;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@Service
public class GeoServerService {

  private static final Logger logger = LoggerFactory.getLogger(GeoServerService.class);

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


    private final RestTemplate restTemplate = new RestTemplate();

    public boolean isCreated(String userId, String type) {
        String url = "";
      
        switch (type) {
            case "workspace" -> url = geoserverUrl + "/rest/workspaces/user_" + userId;
            case "workspacetemp" -> url = geoserverUrl + "/rest/workspaces/user_" + userId + "_temp";
            case "datastore" -> url = geoserverUrl + "/rest/workspaces/user_" + userId + "/datastores/user_" + userId;
            case "datastoretemp" -> url = geoserverUrl + "/rest/workspaces/user_" + userId + "_temp/datastores/user_" + userId + "_temp_datastore";
            default -> throw new IllegalArgumentException("Invalid type: " + type);
        }
        HttpHeaders headers = new HttpHeaders();
        headers.setBasicAuth(username, password);
        HttpEntity<String> entity = new HttpEntity<>(headers);

        try {
          ResponseEntity<String> response = restTemplate.exchange(url, HttpMethod.GET, entity, String.class);
          return response.getStatusCode().is2xxSuccessful();
        } catch (HttpClientErrorException.NotFound e) {
          logger.info("GeoServer resource does not exist: type={}, userId={}", type, userId);
          logger.info("Creating {}... for userId={}", type, userId);
          return false;
        }
    }

    public void deleteTemp(String userId) {
      if (isCreated(userId, "workspacetemp")) {
          String url = geoserverUrl + "/rest/workspaces/user_" + userId + "_temp?recurse=true";
          HttpHeaders headers = new HttpHeaders();
          headers.setBasicAuth(username, password);
          HttpEntity<String> entity = new HttpEntity<>(headers);
          restTemplate.exchange(url, HttpMethod.DELETE, entity, String.class);
          logger.info("Deleted temporary workspace for user: {}", userId);
      } 
    }


    public void deleteUserData(String userId) {
      if (isCreated(userId, "workspace")) {
          String url = geoserverUrl + "/rest/workspaces/user_" + userId + "?recurse=true";
          HttpHeaders headers = new HttpHeaders();
          headers.setBasicAuth(username, password);
          HttpEntity<String> entity = new HttpEntity<>(headers);
          restTemplate.exchange(url, HttpMethod.DELETE, entity, String.class);
          logger.info("Deleted workspace for user: {}", userId);
      } 

    }


    public boolean createWorkspace(String userId) {
      if (isCreated(userId, "workspace")) {
          logger.info("Workspace already exists for user: {}", userId);
          return false;
      }
      String url = geoserverUrl + "/rest/workspaces";
      String body = """
              {
                "workspace": {
                  "name": "user_%s"
                }
              }
              """.formatted(userId);
      HttpHeaders headers = new HttpHeaders();
      headers.setContentType(MediaType.APPLICATION_JSON);
      headers.setBasicAuth(username, password);

      restTemplate.postForEntity(url, new HttpEntity<>(body, headers), String.class);
      enableWorkspaceServices("user_" + userId);
      return true;
    }

    public boolean createTempWorkspace(String userId) {
        if (isCreated(userId, "workspacetemp")) {
          enableWorkspaceServices("user_" + userId + "_temp");
          logger.info("Temporary workspace already exists for user: {}", userId);
          return false;
      }
        String url = geoserverUrl + "/rest/workspaces";
        String body = """
                {
                  "workspace": {
                    "name": "user_%s_temp"
                  }
                }
                """.formatted(userId);
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        headers.setBasicAuth(username, password);

        restTemplate.postForEntity(url, new HttpEntity<>(body, headers), String.class);
        enableWorkspaceServices("user_" + userId + "_temp");
        return true;
    }

  private void enableWorkspaceServices(String workspaceName) {
    HttpHeaders headers = new HttpHeaders();
    headers.setContentType(MediaType.APPLICATION_JSON);
    headers.setBasicAuth(username, password);

    for (String service : new String[] {"wms", "wfs", "wmts", "wcs"}) {
      String url = geoserverUrl + "/rest/services/" + service
          + "/workspaces/" + workspaceName + "/settings";
      String body = service.equals("wfs")
        ? """
          {
            "wfs": {
              "name": "WFS",
              "enabled": true,
              "maxFeatures": 1000000
            }
          }
          """
        : "{\"" + service + "\":{\"name\":\""
            + service.toUpperCase() + "\",\"enabled\":true}}";
      try {
        restTemplate.put(url, new HttpEntity<>(body, headers));
        logger.info("Enabled {} for workspace {}", service.toUpperCase(), workspaceName);
      } catch (RestClientResponseException e) {
        logger.error("Could not enable {} for workspace {}: status={}, response={}",
            service.toUpperCase(), workspaceName, e.getStatusCode(), e.getResponseBodyAsString());
      }
    }
  }
    
    public boolean createDatastore(String userId) {
        if (isCreated(userId, "datastore")) {
            logger.info("Datastore already exists for user: {}", userId);
            return false;
        }
        String url = geoserverUrl + "/rest/workspaces/user_" + userId + "/datastores";
        String body = """
                {
                  "dataStore": {
                    "name": "user_%s",
                    "connectionParameters": {
                      "host": "postgres",
                      "port": "5432",
                      "database": "%s",
                      "user": "%s",
                      "passwd": "%s",
                      "dbtype": "postgis"
                    }
                  }
                }
                """.formatted(userId, dbName, dbUsername, dbPassword);

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        headers.setBasicAuth(username, password);

        restTemplate.postForEntity(url, new HttpEntity<>(body, headers), String.class);
    
      return true;
    }
    public boolean createTempDatastore(String userId) {
        if (isCreated(userId, "datastoretemp")) {
          logger.info("Temporary datastore already exists for user: {}", userId);
          return false;
        }
        String url = geoserverUrl + "/rest/workspaces/user_" + userId + "_temp/datastores";
        String body = """
                {
                  "dataStore": {
                    "name": "user_%s_temp_datastore",
                    "connectionParameters": {
                      "host": "postgres",
                      "port": "5432",
                      "database": "%s",
                      "user": "%s",
                      "passwd": "%s",
                      "dbtype": "postgis"
                    }
                  }
                }
                """.formatted(userId, dbName, dbUsername, dbPassword);

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        headers.setBasicAuth(username, password);

        restTemplate.postForEntity(url, new HttpEntity<>(body, headers), String.class);
      return true;
    }

    public void publishLayer(String tableName, String title, String userId) {
        String url = geoserverUrl + "/rest/workspaces/user_" + userId + "_temp"
                + "/datastores/user_" + userId + "_temp_datastore/featuretypes"
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
    }
    public void deleteLayer(String tableName, String userId) {
        String url = geoserverUrl + "/rest/workspaces/user_" + userId + "_temp"
                + "/datastores/user_" + userId + "_temp_datastore/featuretypes/" + tableName + "?recurse=true";

        HttpHeaders headers = new HttpHeaders();
        headers.setBasicAuth(username, password);
        HttpEntity<String> entity = new HttpEntity<>(headers);

        try {
            restTemplate.exchange(url, HttpMethod.DELETE, entity, String.class);
            logger.info("Deleted layer from GeoServer: {}", tableName);
        } catch (HttpClientErrorException.NotFound e) {
            logger.info("Layer not found in GeoServer (already deleted): {}", tableName);
        } catch (Exception e) {
            logger.error("Error deleting layer from GeoServer: {}", e.getMessage());
        }
    }
}
