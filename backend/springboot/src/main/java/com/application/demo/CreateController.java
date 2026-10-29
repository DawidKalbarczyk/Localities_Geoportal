package com.application.demo;

import com.google.firebase.auth.FirebaseToken;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.security.core.annotation.AuthenticationPrincipal;


@RestController 
@RequestMapping ("/create")
public class CreateController {

    @Autowired
    private GeoServerService geoServerService;

    // Mapuje usuwanie tymczasowych zasobów na żądanie DELETE.
    @DeleteMapping("/delete-temp")
    public ResponseEntity<?> deleteTemp(@AuthenticationPrincipal FirebaseToken token) {
        // Wykonuje operację dla UID odczytanego z poprawnego tokenu.
        try {
            // UID jest pobierany z tokenu, więc nie można wskazać zasobów innego konta.
            geoServerService.deleteTemp(token.getUid());
            // Zwraca sukces po usunięciu zasobów.
            return ResponseEntity.ok("Temporary workspaces and datastores deleted successfully");
        } catch (Exception e) {
            // Zwraca błąd, gdy GeoServer nie wykona operacji.
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body("Error deleting temporary workspaces and datastores: " + e.getMessage());
        }
    }

    // Mapuje usuwanie wszystkich danych użytkownika na DELETE.
    @DeleteMapping ("/delete-user-data")
    public ResponseEntity<?> deleteUserData(@AuthenticationPrincipal FirebaseToken token) {
        // Wykonuje usuwanie wyłącznie dla UID z tokenu.
        try {
            geoServerService.deleteUserData(token.getUid());
            // Potwierdza usunięcie danych.
            return ResponseEntity.ok("User data deleted successfully");
        } catch (Exception e) {
            // Obsługuje błąd GeoServera.
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body("Error deleting user data: " + e.getMessage());
        }
    }

    // Mapuje utworzenie workspace i datastore na POST.
    @PostMapping("/create-user-data")
    public ResponseEntity<?> createUserData(@AuthenticationPrincipal FirebaseToken token) {
        // Tworzy zasoby przypisane do UID z tokenu.
        try {
            geoServerService.createWorkspace(token.getUid());
            geoServerService.createDatastore(token.getUid());

            // Potwierdza utworzenie danych użytkownika.
            return ResponseEntity.ok("User data created successfully");
        } catch (Exception e) {
            // Zwraca błąd, jeśli tworzenie zasobów się nie powiedzie.
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body("Error creating user data: " + e.getMessage());
        }
    }

    // Mapuje utworzenie pojedynczego workspace na POST.
    @PostMapping("/create-workspace")
    public ResponseEntity<?> createWorkspace(@AuthenticationPrincipal FirebaseToken token) {
        // Tworzy workspace dla UID z tokenu.
        try {
            boolean created = geoServerService.createWorkspace(token.getUid());
            if (created) {
                // Informuje o utworzeniu workspace.
                return ResponseEntity.ok("Workspace created successfully");
            } else {
                // Informuje, że workspace już istniał.
                return ResponseEntity.ok("Workspace already exists");
            }
        } catch (Exception e) {
            // Zwraca błąd GeoServera.
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body("Error creating workspace: " + e.getMessage());
        }
    }

    // Mapuje utworzenie datastore na POST.
    @PostMapping("/create-datastore")
    public ResponseEntity<?> createDatastore(@AuthenticationPrincipal FirebaseToken token) {
        // Tworzy datastore przypisany do UID z tokenu.
        try {
            boolean created = geoServerService.createDatastore(token.getUid());
            if (created) {
                // Informuje o utworzeniu datastore.
                return ResponseEntity.ok("Datastore created successfully");
            } else {
                // Informuje, że datastore już istniał.
                return ResponseEntity.ok("Datastore already exists");
            }
        } catch (Exception e) {
            // Zwraca błąd GeoServera.
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body("Error creating datastore: " + e.getMessage());
        }
    }

    // Mapuje utworzenie tymczasowego workspace na POST.
    @PostMapping("/create-temp-workspace")
    public ResponseEntity<?> createTempWorkspace(@AuthenticationPrincipal FirebaseToken token) {
        // Tworzy tymczasowy workspace dla UID z tokenu.
        try {
            boolean created = geoServerService.createTempWorkspace(token.getUid());
            if (created) {
                // Informuje o utworzeniu tymczasowego workspace.
                return ResponseEntity.ok("Temporary workspace created successfully");
            } else {
                // Informuje, że tymczasowy workspace już istniał.
                return ResponseEntity.ok("Temporary workspace already exists");
            }
        } catch (Exception e) {
            // Zwraca błąd GeoServera.
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body("Error creating temporary workspace: " + e.getMessage());
        }
    }

    // Mapuje utworzenie tymczasowego datastore na POST.
    @PostMapping("/create-temp-datastore")
    public ResponseEntity<?> createTempDatastore(@AuthenticationPrincipal FirebaseToken token) {
        // Tworzy tymczasowy datastore dla UID z tokenu.
        try {
            boolean created = geoServerService.createTempDatastore(token.getUid());
            if (created) {
                // Informuje o utworzeniu tymczasowego datastore.
                return ResponseEntity.ok("Temporary datastore created successfully");
            } else {
                // Informuje, że tymczasowy datastore już istniał.
                return ResponseEntity.ok("Temporary datastore already exists");
            }
        } catch (Exception e) {
            // Zwraca błąd GeoServera.
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body("Error creating temporary datastore: " + e.getMessage());
        }
    }
}
