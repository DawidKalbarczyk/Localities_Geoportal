package com.application.demo;

public record UserGetRequest(
    String userId,
    String userName,
    String email,
    String photoURL
) {
}
