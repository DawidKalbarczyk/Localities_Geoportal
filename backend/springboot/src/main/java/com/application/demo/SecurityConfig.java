// Umieszcza konfigurację bezpieczeństwa w pakiecie aplikacji.
package com.application.demo;

// Udostępnia bean konfiguracyjny Springa.
import org.springframework.context.annotation.Bean;
// Oznacza klasę jako konfigurację.
import org.springframework.context.annotation.Configuration;
// Udostępnia budowniczy reguł HTTP Security.
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
// Włącza konfigurację Spring Security.
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
// Ustawia sposób przechowywania sesji.
import org.springframework.security.config.http.SessionCreationPolicy;
// Reprezentuje gotowy łańcuch filtrów bezpieczeństwa.
import org.springframework.security.web.SecurityFilterChain;
// Wskazuje miejsce w łańcuchu dla naszego filtra Firebase.
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;

// Rejestruje własne reguły autoryzacji.
@Configuration
@EnableWebSecurity
public class SecurityConfig {
    // Buduje stateless security chain dla API.
    @Bean
    SecurityFilterChain securityFilterChain(HttpSecurity http, FirebaseTokenFilter tokenFilter)
            throws Exception {
        // Rozpoczyna konfigurację HTTP Security.
        return http
                // API używa Bearer tokenów, więc wyłącza CSRF oparte na cookies.
                .csrf(csrf -> csrf.disable())
                // Nie przechowuje sesji użytkownika po stronie serwera.
                .sessionManagement(session -> session.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
                // Definiuje, które ścieżki wymagają uwierzytelnienia.
                .authorizeHttpRequests(auth -> auth
                        // Operacje na profilu i zasobach użytkownika wymagają tokenu.
                        .requestMatchers("/pass/**", "/create/**").authenticated()
                        // Pozostałe endpointy pozostają publiczne.
                        .anyRequest().permitAll())
                // Uruchamia nasz filtr przed standardowym filtrem nazwy i hasła.
                .addFilterBefore(tokenFilter, UsernamePasswordAuthenticationFilter.class)
                // Zwraca gotową konfigurację do Springa.
                .build();
    }
}