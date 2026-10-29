// Umieszcza DTO w pakiecie aplikacji.
package com.application.demo;

// Żądanie zawiera tylko dane profilu, a nie dane identyfikujące konto.
public record UserCreateRequest(
        // Nazwa wyświetlana w profilu.
        String userName,
        // Opcjonalny adres zdjęcia profilowego.
        String photoURL
) {
    // Record automatycznie tworzy konstruktor i metody dostępowe.
}