package com.example.apigateway.service;

import com.example.apigateway.model.NotificationRequest;
import org.springframework.amqp.core.MessageDeliveryMode;
import org.springframework.amqp.rabbit.core.RabbitTemplate;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.util.Map;
import java.util.UUID;

@Service
public class MessageQueueService {
    private final RabbitTemplate rabbitTemplate;

    @Value("${rabbitmq.exchange.name}")
    private String exchangeName;

    public MessageQueueService(RabbitTemplate rabbitTemplate) {
        this.rabbitTemplate = rabbitTemplate;
    }
    public String publishNotification(NotificationRequest request){
        String requestId= UUID.randomUUID().toString();
        String routingKey = request.getType().toLowerCase();

        Map<String,Object> payload = Map.of(
                "request_id",requestId,
                "user_id",request.getUserId(),
                "template_name", request.getTemplateName(),
                "data",request.getData(),
                "created_at",System.currentTimeMillis()

        );
        rabbitTemplate.convertAndSend(exchangeName,routingKey,payload,m->{
            m.getMessageProperties().setCorrelationId(requestId);
            m.getMessageProperties().setDeliveryMode(MessageDeliveryMode.PERSISTENT);
            return m;

        });
        System.out.println("Message queue.ID: " + requestId + ",Type: " + routingKey);
        return requestId;

    }
}
