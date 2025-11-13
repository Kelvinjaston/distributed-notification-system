package com.example.apigateway.model;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Data;

@Data
public class NotificationRequest {
    @JsonProperty("user_id")
    private Long userId;

    @JsonProperty("type")
    private String type;

    @JsonProperty("template_name")
    private String templateName;

    @JsonProperty("data")
    private Object data;
}
