package com.example.user_service.service;

import com.example.user_service.entity.User;
import com.example.user_service.repo.UserRepository;
import com.example.user_service.exception.UnauthorizedServiceException;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.cache.annotation.Cacheable;
import java.util.Arrays;
import java.util.List;
import java.util.Optional;

@Service
public class UserService {

    private final UserRepository userRepository;
    private final List<String> validApiKeys;
    public UserService(
            UserRepository userRepository,
            @Value("${service.auth.valid-keys}") String validKeysString) {

        this.userRepository = userRepository;
        this.validApiKeys = Arrays.asList(validKeysString.split(","));
    }

    public Optional<User> findUserContactInfoById(Long userId, String apiKey) {

        authorizeServiceCall(apiKey);

        return fetchUserFromCacheOrDB(userId);
    }

    private void authorizeServiceCall(String apiKey) {
        if (apiKey == null || !validApiKeys.contains(apiKey)) {
            throw new UnauthorizedServiceException("Unauthorized access: Invalid or missing service API key.");
        }
    }
    @Cacheable(value = "user_contact", key = "#userId")
    private Optional<User> fetchUserFromCacheOrDB(Long userId) {

        System.out.println("--- CACHE MISS --- Fetching user ID " + userId + " from PostgreSQL...");
        return userRepository.findByUserId(userId);
    }
}