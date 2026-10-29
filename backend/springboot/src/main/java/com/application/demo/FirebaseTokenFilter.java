// Umieszcza filtr w pakiecie aplikacji.
package com.application.demo;

// Udostępnia skonfigurowaną aplikację Firebase.
import com.google.firebase.FirebaseApp;
// Weryfikuje tokeny Firebase.
import com.google.firebase.auth.FirebaseAuth;
// Reprezentuje zweryfikowany token.
import com.google.firebase.auth.FirebaseToken;
// Udostępnia elementy filtra servletowego.
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
// Tworzy obiekt uwierzytelnienia Spring Security.
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
// Przechowuje uwierzytelnienie na czas żądania.
import org.springframework.security.core.context.SecurityContextHolder;
// Udostępnia logger do komunikatów widocznych w logach kontenera.
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
// Rejestruje filtr jako bean Springa.
import org.springframework.stereotype.Component;
// Zapewnia wykonanie filtra tylko raz na żądanie.
import org.springframework.web.filter.OncePerRequestFilter;
import java.util.Base64;
import java.nio.charset.StandardCharsets;

// Udostępnia typy wyjątków i wejścia filtra.
import java.io.IOException;
// Oznacza brak dodatkowych ról użytkownika.
import java.util.Collections;

// Ten filtr sprawdza nagłówek Authorization przed kontrolerem.
@Component
public class FirebaseTokenFilter extends OncePerRequestFilter {
    // Tworzy logger przypisany do tego filtra.
    private static final Logger logger = LoggerFactory.getLogger(FirebaseTokenFilter.class);
    // FirebaseAuth wykonuje faktyczną weryfikację tokenu.
    private final FirebaseAuth firebaseAuth;

    // Konstruktor pobiera aplikację Firebase skonfigurowaną przez FirebaseConfig.
    public FirebaseTokenFilter(FirebaseApp firebaseApp) {
        // Tworzy klienta Firebase Admin dla tej aplikacji.
        this.firebaseAuth = FirebaseAuth.getInstance(firebaseApp);
    }

    // Przetwarza każde żądanie HTTP przed jego obsługą przez kontroler.
    @Override
    protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response,
                                    FilterChain filterChain) throws ServletException, IOException {
        // Odczytuje nagłówek Authorization przesłany przez Angulara.
        String authorization = request.getHeader("Authorization");
        // Sprawdza, czy żądanie w ogóle zawiera nagłówek Bearer.
        boolean hasBearerToken = authorization != null && authorization.startsWith("Bearer ");
        // Loguje ścieżkę i obecność tokenu, ale nie jego treść.
        logger.info("[Firebase] request={} {} bearerToken={}", request.getMethod(), request.getRequestURI(), hasBearerToken);

        // Sprawdza, czy nagłówek ma oczekiwany format Bearer token.
        // Tylko token zweryfikowany przez Firebase może utworzyć uwierzytelnienie.
        if (hasBearerToken) {
            try {
                // Loguje bezpieczne nagłówki JWT przed weryfikacją podpisu.
                logTokenClaims(authorization.substring(7));
                // Usuwa prefiks Bearer i sprawdza podpis, projekt oraz ważność tokenu.
                FirebaseToken token = firebaseAuth.verifyIdToken(authorization.substring(7));
                // Zapisuje zweryfikowany token w kontekście bieżącego żądania.
                SecurityContextHolder.getContext().setAuthentication(
                        // Tworzy uwierzytelnienie bez dodatkowych ról.
                        new UsernamePasswordAuthenticationToken(token, null, Collections.emptyList()));
                // Potwierdza poprawną weryfikację i pokazuje UID.
                logger.info("[Firebase] token zaakceptowany, uid={}", token.getUid());
            } catch (Exception exception) {
                // Niepoprawny token nie może utworzyć dostępu.
                SecurityContextHolder.clearContext();
                // Informuje o odrzuceniu bez ujawniania tokenu ani szczegółów sekretu.
                logger.warn("[Firebase] token odrzucony, path={}, reason={}",
                        request.getRequestURI(), exception.getMessage());
            }
        }

        // Przekazuje żądanie do następnego filtra albo kontrolera.
        filterChain.doFilter(request, response);
    }

    // Odczytuje tylko kid, aud i iss, aby sprawdzić zgodność projektu bez ujawniania tokenu.
    private void logTokenClaims(String token) {
        try {
            String[] parts = token.split("\\.");
            String header = new String(Base64.getUrlDecoder().decode(parts[0]), StandardCharsets.UTF_8);
            String payload = new String(Base64.getUrlDecoder().decode(parts[1]), StandardCharsets.UTF_8);
            logger.info("[Firebase] token header={}, payload={}", header, payload);
        } catch (Exception exception) {
            logger.warn("[Firebase] nie można odczytać nagłówka tokenu: {}", exception.getMessage());
        }
    }
}