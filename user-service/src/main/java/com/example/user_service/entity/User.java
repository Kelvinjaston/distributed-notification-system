package com.example.user_service.entity;

import com.fasterxml.jackson.annotation.JsonProperty;
import jakarta.persistence.*;
import lombok.Data;
import lombok.Getter;
import lombok.Setter;

@Entity
@Table(name = "users")
@Data

public class User {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @JsonProperty("user_id")
    private Long userId;

    private String email;

    @Column(name = "push_token")
    @JsonProperty("push_token")
    private String pushToken;

    private String locale;

    @Column(name = "notification_preferences",columnDefinition = "text")
    @JsonProperty("notification_preference")
    private String notificationPreferences;
}
