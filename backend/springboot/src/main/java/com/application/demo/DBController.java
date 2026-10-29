package com.application.demo;

import com.google.firebase.auth.FirebaseToken;
import com.google.firebase.auth.FirebaseAuthException;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.*;

import org.springframework.web.multipart.MultipartFile;
import org.springframework.http.MediaType;
import java.io.IOException;




@RestController 
@RequestMapping("/pass")
public class DBController {
    private final DBService dbService;
    private final JdbcTemplate jdbcTemplate;
    private final FileStorageService fileStorageService;

    public DBController(DBService dbService, JdbcTemplate jdbcTemplate, FileStorageService fileStorageService) {
        this.dbService = dbService;
        this.jdbcTemplate = jdbcTemplate;
        this.fileStorageService = fileStorageService;
    }

    // Mapuje tworzenie użytkownika na metodę HTTP POST.
    @PostMapping("/create-user")
    public ResponseEntity<?> createUser(@AuthenticationPrincipal FirebaseToken token,
                                        @RequestBody UserCreateRequest request) {
        // Próbuje utworzyć rekord dla UID pobranego z uwierzytelnienia.
        try {
            // UID i e-mail pochodzą z tokenu, a nie z danych przesłanych przez przeglądarkę.
            dbService.createUser(token.getUid(), token.getEmail(), request.userName(), request.photoURL());
            // Zwraca kod 201 po poprawnym utworzeniu rekordu.
            return ResponseEntity.status(HttpStatus.CREATED).body("User created successfully");
        } catch (Exception e) {
            // Zwraca błąd serwera, jeśli zapis do bazy się nie udał.
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                    .body("Error creating user: " + e.getMessage());
        }
    }

    // Mapuje zmianę profilu na metodę HTTP PATCH.

    @GetMapping("/get-user-data")
    public ResponseEntity<?> getUserData(@AuthenticationPrincipal FirebaseToken token) {
        boolean userExists = dbService.checkUserExists(token.getUid());
        if (!userExists) {
            return ResponseEntity.status(HttpStatus.NOT_FOUND).body("User not found");
        }

        String sql = "SELECT id, username, email, \"photoUrl\" FROM users WHERE id = ?";
        UserGetRequest userData = jdbcTemplate.queryForList(sql, token.getUid())
                .stream()
                .findFirst()
                .map(row -> new UserGetRequest(
                        (String) row.get("id"),
                        (String) row.get("username"),
                        (String) row.get("email"),
                        (String) row.get("photoUrl")
                ))
                .orElse(null);
        // Zwraca dane użytkownika w formacie JSON.
        return ResponseEntity.ok(userData);
    }
    @GetMapping("/get-user-data-firebase")
    public ResponseEntity<?> getUserDataFirebase(@AuthenticationPrincipal FirebaseToken token) {
        // Zwraca dane użytkownika z Firebase.
        return ResponseEntity.ok(token);
    }

    @PatchMapping("/update-user-name")
    public ResponseEntity<?> updateUser(@AuthenticationPrincipal FirebaseToken token,
                                        @RequestBody UserUpdateRequest request) {
        // Klient może zmienić profil tylko zalogowanego użytkownika.
        // Odrzuca pustą albo zbyt długą nazwę.
        if (!dbService.isTokenFresh(token)) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body("Re-authentication required to update user profile");
        }
        if (request.userName() == null || request.userName().isBlank() || request.userName().length() > 255) {
            // Informuje klienta, że dane profilu są niepoprawne.
            return ResponseEntity.badRequest().body("Invalid user name");
        }
        if (dbService.checkIfUserNameTaken(request.userName(), token.getUid())) {
            return ResponseEntity.badRequest().body("User name is already taken");
        }

        try {
            // Aktualizuje Firebase i rekord wskazany wyłącznie przez UID z tokenu.
            boolean updated = dbService.updateUserName(token.getUid(), request.userName().trim());
            // Zwraca sukces albo informację, że użytkownik nie istnieje w bazie.
            return updated ? ResponseEntity.ok("User updated successfully") : ResponseEntity.notFound().build();
        } catch (FirebaseAuthException e) {
            // Zwraca kontrolowany błąd, gdy Firebase odrzuci aktualizację profilu.
            return ResponseEntity.status(HttpStatus.BAD_GATEWAY)
                    .body("Firebase user update failed: " + e.getMessage());
        }
    }

    @PatchMapping ("/update-user-email")
    public ResponseEntity<?> updateUserEmail(@AuthenticationPrincipal FirebaseToken token,
                                             @RequestBody UserUpdateRequest request) {
        // Klient może zmienić profil tylko zalogowanego użytkownika.
        // Odrzuca pustą albo niepoprawną adres e-mail.
        if (!dbService.isTokenFresh(token)) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body("Re-authentication required to update user profile");
        }

        if (request.userEmail() == null || request.userEmail().isBlank() || !request.userEmail().contains("@")) {
            // Informuje klienta, że dane profilu są niepoprawne.
            return ResponseEntity.badRequest().body("Invalid user email");
        }
        if (dbService.checkIfEmailTaken(request.userEmail(), token.getUid())) {
            return ResponseEntity.badRequest().body("User email is already taken");
        }

        try {
            // Aktualizuje Firebase i rekord wskazany wyłącznie przez UID z tokenu.
            boolean updated = dbService.updateUserEmail(token.getUid(), request.userEmail().trim());
            // Zwraca sukces albo informację, że użytkownik nie istnieje w bazie.
            return updated ? ResponseEntity.ok("User email updated successfully") : ResponseEntity.notFound().build();
        } catch (FirebaseAuthException e) {
            // Zwraca kontrolowany błąd, gdy Firebase odrzuci aktualizację profilu.
            return ResponseEntity.status(HttpStatus.BAD_GATEWAY)
                    .body("Firebase user email update failed: " + e.getMessage());
        }
    }

    @PatchMapping ("/update-user-password")
    public ResponseEntity<?> updateUserPassword(@AuthenticationPrincipal FirebaseToken token,
                                                @RequestBody UserUpdateRequest request) {
        // Klient może zmienić profil tylko zalogowanego użytkownika.
        // Odrzuca pustą albo zbyt krótką hasło.
        if (!dbService.isTokenFresh(token)) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body("Re-authentication required to update user profile");
        }

        if (request.userPassword() == null || request.userPassword().isBlank() || request.userPassword().length() < 6) {
            // Informuje klienta, że dane profilu są niepoprawne.
            return ResponseEntity.badRequest().body("Invalid user password");
        }
        if (request.userPassword().length() < 8) {
            return ResponseEntity.badRequest().body("Weak password");
        }

        try {
            // Aktualizuje Firebase i rekord wskazany wyłącznie przez UID z tokenu.
            dbService.updateUserPassword(token.getUid(), request.userPassword().trim());
            // Zwraca sukces albo informację, że użytkownik nie istnieje w bazie.
            return ResponseEntity.ok("User password updated successfully");
        } catch (FirebaseAuthException e) {
            // Zwraca kontrolowany błąd, gdy Firebase odrzuci aktualizację profilu.
            return ResponseEntity.status(HttpStatus.BAD_GATEWAY)
                    .body("Firebase user password update failed: " + e.getMessage());
        }
    }
    
    @PatchMapping(value="/update-user-photo", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    public ResponseEntity<?> updateUserPhoto(@AuthenticationPrincipal FirebaseToken token,
                                             @RequestParam("profilePicture") MultipartFile file) {
        if (!dbService.isTokenFresh(token)) {
            return ResponseEntity.status(HttpStatus.UNAUTHORIZED).body("Re-authentication required to update user profile");
        }

        if (file == null || file.isEmpty()) {
            return ResponseEntity.badRequest().body("No file uploaded");
        }

        String contentType = file.getContentType();
        boolean allowedType = contentType != null && (contentType.equals("image/png") || contentType.equals("image/jpeg") || contentType.equals("image/gif") || contentType.equals("image/webp"));
        if (!allowedType) {
            return ResponseEntity.badRequest().body("Invalid file type. Only PNG, JPEG, GIF, and WEBP are allowed.");
        }
        if (file.getSize() > 10 * 1024 * 1024) { // 10 MB limit
            return ResponseEntity.badRequest().body("File size exceeds the maximum limit of 10 MB.");
        }
        try {
            String photoUrl = fileStorageService.storeProfilePicture(token.getUid(), file);
            boolean updated = dbService.updateUserPhotoURL(token.getUid(), photoUrl);
            if (updated) {
                return ResponseEntity.ok("User photo updated successfully");
            } else {
                return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body("Failed to update user photo in database");
            }
        } catch (IOException e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body("An error occurred while updating user photo: " + e.getMessage());
        } catch (FirebaseAuthException e) {
            return ResponseEntity.status(HttpStatus.BAD_GATEWAY).body("Firebase user photo update failed: " + e.getMessage());
        }
    }
}
