package com.example.apigateway.controller;

import com.example.apigateway.model.NotificationRequest;
import com.example.apigateway.service.MessageQueueService;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

@RestController
@RequestMapping("/api/v1/notifications")
public class NotificationController {
    private final MessageQueueService messageQueueService;

    public NotificationController(MessageQueueService messageQueueService) {
        this.messageQueueService = messageQueueService;
    }
    @PostMapping
    public ResponseEntity<Map<String,Object>> sendNotification(@RequestBody NotificationRequest request){
        String type = request.getType() != null ? request.getType().toLowerCase() : null;
        if (request.getUserId()==null || type==null || request.getTemplateName()== null || (!type.equals("push"))){
            return ResponseEntity
                    .badRequest()
                    .body(Map.of("error", "Invalid request body.", "details", "Requires user_id, type ('email' or 'push'), and template_name."));
        }
        try {
            String requestId = messageQueueService.publishNotification(request);
            return ResponseEntity
                    .status(HttpStatus.ACCEPTED)
                    .body(Map.of("status", "queued",
                            "request_id", requestId,
                            "message", "Notification request accepted and queued for processing."
                    ));
        } catch (Exception e) {
            return ResponseEntity
                    .status(HttpStatus.SERVICE_UNAVAILABLE)
                    .body(Map.of("error", "Service Unavailable", "message", "Could not connect to the message broker. Try again later."));
        }
    }

}
