package com.example.user_service.controller;

import com.example.user_service.entity.User;
import com.example.user_service.repo.UserRepository;
import com.example.user_service.service.UserService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;
import java.util.Optional;

@RestController
@RequestMapping("/api/v1/users")
public class UserController {
    private final UserService userService;

    public UserController(UserService userService) {
        this.userService = userService;
    }

    @GetMapping("/{userId}/contact_info")
    public ResponseEntity<Map<String,Object>> getContactInfo(@PathVariable Long userId, @RequestHeader(value = "X-Service-API-Key", required = false) String apiKey){
        Optional<User>optionalUser = userService.findUserContactInfoById(userId,apiKey);
        if (optionalUser.isEmpty()){
            return ResponseEntity
                    .status(404)
                    .body(Map.of("error", "not_found", "message", "User with ID " + userId + " not found."));

        }
        User user = optionalUser.get();
        Map<String,Object> data =Map.of("user_id", user.getUserId(),
                "email", user.getEmail() != null ? user.getEmail() : "",
                "push_token", user.getPushToken() != null ? user.getPushToken() : "",
                "locale", user.getLocale() != null ? user.getLocale() : "en",
                "notification_preferences", user.getNotificationPreferences()
        );
        return ResponseEntity.ok(data);
    }
}
