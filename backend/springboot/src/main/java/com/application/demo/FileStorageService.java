package com.application.demo;

import org.springframework.stereotype.Service;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.nio.file.*;
import java.util.stream.Stream;

@Service 
public class FileStorageService {
    @Value("${app.base-url}")
    private String baseUrl;

    private static final String BASE_DIR = "images/user";

    public String storeProfilePicture(String uid, MultipartFile file) throws IOException {
        String extension = resolveExtension(file.getOriginalFilename(), file.getContentType());
        Path userDir = Paths.get(BASE_DIR, uid);
        Files.createDirectories(userDir);

        deleteExistingProfilePictures(userDir);

        String filename = "profile" + extension;
        Path targetPath = userDir.resolve(filename);
        Files.copy(file.getInputStream(), targetPath, StandardCopyOption.REPLACE_EXISTING);

        return baseUrl + "/images/user/" + uid + "/" + filename;
    }

    private void deleteExistingProfilePictures(Path userDir) throws IOException {
        if (!Files.exists(userDir)) return;
        try (Stream<Path> files = Files.list(userDir)) {
            files.filter(path -> path.getFileName().toString().startsWith("profile"))
                 .forEach(path -> {
                     try {
                         Files.deleteIfExists(path);
                     } catch (IOException e) {
                         throw new RuntimeException("Failed to delete existing profile picture: " + path, e);
                     }
            });
        }
    }
    private String resolveExtension(String originalFilename, String contentType) {
        if (contentType != null) {
            switch (contentType) {
                case "image/png": return ".png";
                case "image/jpeg": return ".jpg";
                case "image/gif": return ".gif";
                case "image/webp": return ".webp";
            }
        }
        if (originalFilename != null && originalFilename.contains(".")) {
            return originalFilename.substring(originalFilename.lastIndexOf("."));
        }
        return ""; // Default extension
    }
}
