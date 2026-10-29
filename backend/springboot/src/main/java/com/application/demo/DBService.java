package com.application.demo;

// Udostępnia skonfigurowaną aplikację Firebase Admin.
import com.google.firebase.FirebaseApp;
// Wysyła żądania administracyjne do Firebase Authentication.
import com.google.firebase.auth.FirebaseAuth;
// Reprezentuje błąd zwracany przez Firebase podczas aktualizacji użytkownika.
import com.google.firebase.auth.FirebaseAuthException;
import com.google.firebase.auth.FirebaseToken;
// Buduje żądanie aktualizacji danych użytkownika Firebase.
import com.google.firebase.auth.UserRecord;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Service;

@Service
public class DBService {
    private final JdbcTemplate jdbcTemplate;
    // Klient Firebase używany do aktualizacji profilu po stronie serwera.
    private final FirebaseAuth firebaseAuth;

    public DBService(JdbcTemplate jdbcTemplate, FirebaseApp firebaseApp) {
        this.jdbcTemplate = jdbcTemplate;
        // Pobiera FirebaseAuth z aplikacji skonfigurowanej przez FirebaseConfig.
        this.firebaseAuth = FirebaseAuth.getInstance(firebaseApp);
    }

    // Sprawdza, czy baza ma rekord o podanym UID.
    public boolean checkUserExists(String userId) {
        // Definiuje zapytanie sprawdzające liczbę rekordów.
        String sql = "SELECT COUNT(*) FROM users WHERE id = ?";
        // Wykonuje zapytanie z parametrem zamiast sklejać SQL ręcznie.
        Integer count = jdbcTemplate.queryForObject(sql, Integer.class, userId);
        // Zwraca true tylko wtedy, gdy znaleziono co najmniej jeden rekord.
        return count != null && count > 0;
    }

    // Tworzy rekord użytkownika z UID i e-mailem pochodzącymi z tokenu.
    public void createUser(String userId, String userEmail, String userName, String photoURLString) {
        // Rekord jest powiązany z UID Firebase zapisanym jako user_id.
        // ON CONFLICT chroni przed błędem przy ponownym tworzeniu tego samego konta.
        // E-mail jest zwykłą daną profilu; hasło pozostaje wyłącznie w Firebase.
        String sql = "INSERT INTO users (id, username, email, \"photoUrl\", json) VALUES (?, ?, ?, ?, NULL) "
                + "ON CONFLICT (id) DO NOTHING";
        // Wykonuje bezpieczny parametryzowany INSERT.
        jdbcTemplate.update(sql, userId, userName, userEmail, photoURLString);
    }

    // Aktualizacja zawsze ma warunek na UID pobrany z tokenu.
    // Zwraca informację, czy dokładnie jeden rekord został zmieniony.



    private static final long REAUTH_WINDOW_SECONDS = 300;
    public boolean isTokenFresh(FirebaseToken token) {
        Object authTimeClaim = token.getClaims().get("auth_time");
        if (authTimeClaim == null) {
            return false;
        }
        long authTimeSeconds = ((Number) authTimeClaim).longValue();
        long currentTimeSeconds = System.currentTimeMillis() / 1000;
        return currentTimeSeconds - authTimeSeconds <= REAUTH_WINDOW_SECONDS;
    }

    public boolean checkIfUserNameTaken(String userName, String userId) {
        String sql = "SELECT COUNT(*) FROM users WHERE username = ? AND id != ?";
        Integer count = jdbcTemplate.queryForObject(sql, Integer.class, userName, userId);
        return count != null && count > 0;
    }

    public boolean checkIfEmailTaken(String email, String userId) {
        String sql = "SELECT COUNT(*) FROM users WHERE email = ? AND id != ?";
        Integer count = jdbcTemplate.queryForObject(sql, Integer.class, email, userId);
        return count != null && count > 0;
    }


    public boolean updateUserName(String userId, String userName) throws FirebaseAuthException {
        // Przygotowuje żądanie Firebase dla UID odczytanego z tokenu.
        UserRecord.UpdateRequest firebaseUpdate = new UserRecord.UpdateRequest(userId)
            // Aktualizuje displayName w Firebase Authentication.
            .setDisplayName(userName);

        // Wysyła żądanie zmiany danych do Firebase przed zapisem lokalnym.
        firebaseAuth.updateUser(firebaseUpdate);
        // Aktualizuje nazwę i zdjęcie tylko dla właściwego UID.
        String sql = "UPDATE users SET username = ? WHERE id = ?";
        // Wykonuje UPDATE i sprawdza liczbę zmienionych rekordów.
        return jdbcTemplate.update(sql, userName, userId) == 1;
    }

    public boolean updateUserEmail(String userId, String email) throws FirebaseAuthException {
        // Przygotowuje żądanie Firebase dla UID odczytanego z tokenu.
        if (checkIfEmailTaken(email, userId)) {
            return true;
        }; // Sprawdza, czy e-mail jest już zajęty przez innego użytkownika
        UserRecord.UpdateRequest firebaseUpdate = new UserRecord.UpdateRequest(userId)
            // Aktualizuje e-mail w Firebase Authentication.
            .setEmail(email);

        // Wysyła żądanie zmiany danych do Firebase przed zapisem lokalnym.
        firebaseAuth.updateUser(firebaseUpdate);
        // Aktualizuje e-mail tylko dla właściwego UID.
        String sql = "UPDATE users SET email = ? WHERE id = ?";
        // Wykonuje UPDATE i sprawdza liczbę zmienionych rekordów.
        return jdbcTemplate.update(sql, email, userId) == 1;
    }

    public void updateUserPassword(String userId, String password) throws FirebaseAuthException {
        // Przygotowuje żądanie Firebase dla UID odczytanego z tokenu.
        UserRecord.UpdateRequest firebaseUpdate = new UserRecord.UpdateRequest(userId)
            // Aktualizuje hasło w Firebase Authentication.
            .setPassword(password);

        // Wysyła żądanie zmiany danych do Firebase przed zapisem lokalnym.
        firebaseAuth.updateUser(firebaseUpdate);
        // Aktualizuje hasło tylko dla właściwego UID.
        firebaseAuth.revokeRefreshTokens(userId);
    }

    public boolean updateUserPhotoURL(String userId, String photoURL) throws FirebaseAuthException {
        // Przygotowuje żądanie Firebase dla UID odczytanego z tokenu.
        UserRecord.UpdateRequest firebaseUpdate = new UserRecord.UpdateRequest(userId)
            // Aktualizuje photoURL w Firebase Authentication.
            .setPhotoUrl(photoURL);

        // Wysyła żądanie zmiany danych do Firebase przed zapisem lokalnym.
        firebaseAuth.updateUser(firebaseUpdate);
        // Aktualizuje zdjęcie tylko dla właściwego UID.
        String sql = "UPDATE users SET \"photoUrl\" = ? WHERE id = ?";
        // Wykonuje UPDATE i sprawdza liczbę zmienionych rekordów.
        return jdbcTemplate.update(sql, photoURL, userId) == 1;
    }

}
