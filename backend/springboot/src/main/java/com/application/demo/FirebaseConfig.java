// Umieszcza konfigurację Firebase w pakiecie głównej aplikacji Spring Boot.
package com.application.demo;

import com.google.api.client.http.apache.v2.ApacheHttpTransport;
// Odczytuje dane uwierzytelniające Google service account.
import com.google.auth.oauth2.GoogleCredentials;
// Reprezentuje uruchomioną aplikację Firebase Admin.
import com.google.firebase.FirebaseApp;
// Buduje konfigurację Firebase Admin.
import com.google.firebase.FirebaseOptions;
// Wstrzykuje wartość z application.properties lub zmiennej środowiskowej.
import org.springframework.beans.factory.annotation.Value;
// Oznacza klasę jako konfigurację Springa.
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

// Odczytuje dane Base64 w pamięci.
import java.io.ByteArrayInputStream;
// Pozwala przekazać surowy JSON jako bajty UTF-8.
import java.nio.charset.StandardCharsets;
// Dekoduje Base64 do oryginalnego JSON-a.
import java.util.Base64;

// Informuje Springa, że ta klasa definiuje bean-y konfiguracyjne.
@Configuration
public class FirebaseConfig {
    // Tworzy jedną instancję Firebase Admin używaną przez backend.
    @Bean
    FirebaseApp firebaseApp(@Value("${firebase.service-account-json-base64}") String encodedCredentials)
            throws Exception {
        // Zatrzymuje uruchamianie, jeżeli sekret nie został skonfigurowany.
        if (encodedCredentials.isBlank()) {
            // Ten komunikat wskazuje brak zmiennej, ale nie ujawnia jej wartości.
            throw new IllegalStateException("FIREBASE_SERVICE_ACCOUNT_JSON_BASE64 must be configured");
        }

        // Przygotowuje bajty konfiguracji Firebase z wartości środowiskowej.
        byte[] credentialsJson = encodedCredentials.trim().startsWith("{")
            // Obsługuje jednoliniowy surowy JSON zaczynający się od klamry.
            ? encodedCredentials.trim().getBytes(StandardCharsets.UTF_8)
            // Obsługuje Base64 wygenerowane z pliku JSON.
            : Base64.getDecoder().decode(encodedCredentials.trim());

        // Buduje opcje Firebase na podstawie sekretu service account.
        FirebaseOptions options = FirebaseOptions.builder()
            // Odczytuje JSON service account z przygotowanych bajtów.
            .setCredentials(GoogleCredentials.fromStream(new ByteArrayInputStream(credentialsJson)))
            .setHttpTransport(new ApacheHttpTransport())
                .build();
        // Loguje tylko nazwę projektu, aby porównać ją z projectId frontendu.
        System.out.println("[Firebase] backend projectId=" + options.getProjectId());
        // Rejestruje skonfigurowaną aplikację Firebase w Springu.
        return FirebaseApp.initializeApp(options);
    }
}