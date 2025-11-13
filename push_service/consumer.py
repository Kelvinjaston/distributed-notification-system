"""
Push Notification Service
Consumes messages from push queue and sends push notifications
"""
import os
import pika
import json
import logging
import time
import requests
from typing import Dict, Any, Optional
from datetime import datetime
from firebase_admin import credentials, initialize_app, messaging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# --- RabbitMQ Configuration ---
RABBITMQ_HOST = os.environ.get("RABBITMQ_HOST", "rabbitmq")
RABBITMQ_PORT = int(os.environ.get("RABBITMQ_PORT", 5672))
RABBITMQ_USER = os.environ.get("RABBITMQ_USER")
RABBITMQ_PASS = os.environ.get("RABBITMQ_PASS")
QUEUE_NAME = os.environ.get("PUSH_QUEUE_NAME", "push.queue")

# --- External Service Contracts ---
# Hostnames MUST be 'user-service' and 'template-service' inside Docker
USER_SERVICE_URL = os.environ.get("USER_SERVICE_BASE_URL", "http://user-service:8081")
TEMPLATE_SERVICE_URL = os.environ.get("TEMPLATE_SERVICE_BASE_URL", "http://template-service:8082")
API_KEY = os.environ.get("USER_SERVICE_API_KEY")  # Used for X-Service-API-Key header

# Firebase configuration
FIREBASE_CREDENTIALS_PATH = os.environ.get("FIREBASE_CREDENTIALS_PATH", "firebase-credentials.json")

# Retry configuration
MAX_RETRY_COUNT = 3
RETRY_DELAYS = [60, 300, 900]  # 1 min, 5 min, 15 min (exponential backoff)

# Initialize Firebase (if credentials exist)
firebase_initialized = False
try:
    if os.path.exists(FIREBASE_CREDENTIALS_PATH):
        cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)
        initialize_app(cred)
        firebase_initialized = True
        logger.info("Firebase initialized successfully")
    else:
        logger.warning(f"Firebase credentials not found at {FIREBASE_CREDENTIALS_PATH}")
        logger.warning("Push notifications will be simulated (logged only)")
except Exception as e:
    logger.error(f"Failed to initialize Firebase: {str(e)}")
    logger.warning("Push notifications will be simulated (logged only)")


def get_rabbitmq_connection():
    """Establish RabbitMQ connection"""
    try:
        credentials_obj = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
        parameters = pika.ConnectionParameters(
            host=RABBITMQ_HOST,
            port=RABBITMQ_PORT,
            credentials=credentials_obj,
            heartbeat=600,
            blocked_connection_timeout=300
        )
        connection = pika.BlockingConnection(parameters)
        logger.info(f"Connected to RabbitMQ at {RABBITMQ_HOST}:{RABBITMQ_PORT}")
        return connection
    except Exception as e:
        logger.error(f"Failed to connect to RabbitMQ: {str(e)}")
        raise


def fetch_user_data(user_id: str) -> Optional[Dict[str, Any]]:
    """Fetch user data from User Service"""
    try:
        headers = {
            "X-Service-API-Key": API_KEY,
            "Content-Type": "application/json"
        }
        
        response = requests.get(
            f"{USER_SERVICE_URL}/api/v1/users/{user_id}",
            headers=headers,
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            logger.info(f"User data fetched for user_id: {user_id}")
            return data.get("data")
        else:
            logger.error(f"Failed to fetch user data: {response.status_code} - {response.text}")
            return None
            
    except requests.exceptions.Timeout:
        logger.error(f"Timeout fetching user data for user_id: {user_id}")
        return None
    except Exception as e:
        logger.error(f"Error fetching user data: {str(e)}")
        return None


def fetch_template_data(template_code: str) -> Optional[Dict[str, Any]]:
    """Fetch template data from Template Service"""
    try:
        headers = {
            "X-Service-API-Key": API_KEY,
            "Content-Type": "application/json"
        }
        
        response = requests.get(
            f"{TEMPLATE_SERVICE_URL}/api/v1/templates/{template_code}",
            headers=headers,
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            logger.info(f"Template data fetched for template_code: {template_code}")
            return data.get("data")
        else:
            logger.error(f"Failed to fetch template data: {response.status_code} - {response.text}")
            return None
            
    except requests.exceptions.Timeout:
        logger.error(f"Timeout fetching template for template_code: {template_code}")
        return None
    except Exception as e:
        logger.error(f"Error fetching template data: {str(e)}")
        return None


def render_template_variables(template_string: str, variables: Dict[str, Any]) -> str:
    """Simple variable substitution in template"""
    if not template_string:
        return ""
    
    result = template_string
    for key, value in variables.items():
        placeholder = f"{{{{{key}}}}}"  # {{key}}
        result = result.replace(placeholder, str(value))
    
    return result


def send_push_notification_fcm(
    device_token: str,
    title: str,
    body: str,
    data: Optional[Dict[str, str]] = None,
    image_url: Optional[str] = None
) -> bool:
    """Send push notification via Firebase Cloud Messaging"""
    if not firebase_initialized:
        # Simulate notification for testing without Firebase
        logger.info(f"[SIMULATED] Push notification sent to {device_token[:20]}...")
        logger.info(f"  Title: {title}")
        logger.info(f"  Body: {body}")
        logger.info(f"  Data: {data}")
        logger.info(f"  Image: {image_url}")
        return True
    
    try:
        # Build notification
        notification = messaging.Notification(
            title=title,
            body=body,
            image=image_url
        )
        
        # Build message
        message = messaging.Message(
            notification=notification,
            data=data or {},
            token=device_token,
            android=messaging.AndroidConfig(
                priority='high',
                notification=messaging.AndroidNotification(
                    sound='default',
                    priority='max'
                )
            ),
            apns=messaging.APNSConfig(
                payload=messaging.APNSPayload(
                    aps=messaging.Aps(
                        sound='default',
                        badge=1
                    )
                )
            )
        )
        
        # Send message
        response = messaging.send(message)
        logger.info(f"Push notification sent successfully: {response}")
        return True
        
    except messaging.UnregisteredError:
        logger.error(f"Device token is invalid or unregistered: {device_token}")
        return False
        
    except messaging.SenderIdMismatchError:
        logger.error(f"Sender ID mismatch for token: {device_token}")
        return False
        
    except Exception as e:
        logger.error(f"Error sending push notification: {str(e)}")
        return False


def update_notification_status(
    notification_id: str,
    status: str,
    error: Optional[str] = None
):
    """Update notification status via User Service or API Gateway"""
    try:
        headers = {
            "X-Service-API-Key": API_KEY,
            "Content-Type": "application/json"
        }
        
        payload = {
            "notification_id": notification_id,
            "status": status,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
        if error:
            payload["error"] = error
        
        # Try to update status (adjust endpoint as needed)
        response = requests.post(
            f"{USER_SERVICE_URL}/api/v1/push/status/",
            json=payload,
            headers=headers,
            timeout=5
        )
        
        if response.status_code in [200, 201]:
            logger.info(f"Status updated for notification {notification_id}: {status}")
        else:
            logger.warning(f"Failed to update status: {response.status_code}")
            
    except Exception as e:
        logger.error(f"Error updating notification status: {str(e)}")


def move_to_dlq(channel, message: Dict[str, Any], reason: str):
    """Move failed message to dead letter queue"""
    try:
        dlq_name = "failed.queue"
        channel.queue_declare(queue=dlq_name, durable=True)
        
        message["failure_reason"] = reason
        message["failed_at"] = datetime.utcnow().isoformat() + "Z"
        
        channel.basic_publish(
            exchange='',
            routing_key=dlq_name,
            body=json.dumps(message),
            properties=pika.BasicProperties(delivery_mode=2)
        )
        
        logger.warning(f"Message moved to DLQ: {message.get('notification_id')} - Reason: {reason}")
        
    except Exception as e:
        logger.error(f"Failed to move message to DLQ: {str(e)}")


def schedule_retry(channel, message: Dict[str, Any], delay: int):
    """Schedule message retry with delay using TTL queue"""
    try:
        retry_queue = f"push.retry.{delay}"
        
        # Declare retry queue with TTL that dead-letters back to main queue
        channel.queue_declare(
            queue=retry_queue,
            durable=True,
            arguments={
                'x-message-ttl': delay * 1000,  # Convert to milliseconds
                'x-dead-letter-exchange': '',
                'x-dead-letter-routing-key': QUEUE_NAME
            }
        )
        
        # Publish to retry queue
        channel.basic_publish(
            exchange='',
            routing_key=retry_queue,
            body=json.dumps(message),
            properties=pika.BasicProperties(delivery_mode=2)
        )
        
        retry_count = message.get("retry_count", 0)
        logger.info(f"Message scheduled for retry {retry_count + 1}/{MAX_RETRY_COUNT} in {delay}s: {message.get('notification_id')}")
        
    except Exception as e:
        logger.error(f"Failed to schedule retry: {str(e)}")


def process_message(ch, method, properties, body):
    """Process push notification message from queue"""
    try:
        # Parse message
        message = json.loads(body)
        
        notification_id = message.get("notification_id")
        user_id = message.get("user_id")
        template_code = message.get("template_code")
        variables = message.get("variables", {})
        retry_count = message.get("retry_count", 0)
        
        logger.info(f"Processing notification: {notification_id} (attempt {retry_count + 1}/{MAX_RETRY_COUNT + 1})")
        
        # Fetch user data
        user_data = fetch_user_data(user_id)
        if not user_data:
            logger.error(f"User not found: {user_id}")
            move_to_dlq(ch, message, "User not found")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            update_notification_status(notification_id, "failed", "User not found")
            return
        
        # Check if user has push token
        push_token = user_data.get("push_token")
        if not push_token:
            logger.error(f"No push token found for user: {user_id}")
            move_to_dlq(ch, message, "Missing push token")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            update_notification_status(notification_id, "failed", "Missing push token")
            return
        
        # Check user preferences
        preferences = user_data.get("preferences", {})
        if not preferences.get("push", True):
            logger.info(f"User {user_id} has disabled push notifications")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            update_notification_status(notification_id, "skipped", "User disabled push notifications")
            return
        
        # Fetch template
        template_data = fetch_template_data(template_code)
        if not template_data:
            logger.error(f"Template not found: {template_code}")
            move_to_dlq(ch, message, "Template not found")
            ch.basic_ack(delivery_tag=method.delivery_tag)
            update_notification_status(notification_id, "failed", "Template not found")
            return
        
        # Render template
        title = render_template_variables(template_data.get("title", "Notification"), variables)
        body_text = render_template_variables(template_data.get("body", ""), variables)
        image_url = template_data.get("image_url")
        
        # Prepare data payload
        data_payload = {
            "notification_id": notification_id,
            "link": str(variables.get("link", "")),
        }
        
        # Add metadata if present
        if variables.get("meta"):
            data_payload.update(variables.get("meta"))
        
        # Send push notification
        success = send_push_notification_fcm(
            device_token=push_token,
            title=title,
            body=body_text,
            data=data_payload,
            image_url=image_url
        )
        
        if success:
            # Success - acknowledge and update status
            ch.basic_ack(delivery_tag=method.delivery_tag)
            update_notification_status(notification_id, "delivered")
            logger.info(f"Push notification delivered successfully: {notification_id}")
            
        else:
            # Failed - retry or move to DLQ
            if retry_count < MAX_RETRY_COUNT:
                # Schedule retry
                message["retry_count"] = retry_count + 1
                delay = RETRY_DELAYS[retry_count] if retry_count < len(RETRY_DELAYS) else RETRY_DELAYS[-1]
                
                schedule_retry(ch, message, delay)
                ch.basic_ack(delivery_tag=method.delivery_tag)
                update_notification_status(notification_id, "pending", f"Retry scheduled (attempt {retry_count + 1})")
                
            else:
                # Max retries exceeded - move to DLQ
                move_to_dlq(ch, message, "Max retries exceeded")
                ch.basic_ack(delivery_tag=method.delivery_tag)
                update_notification_status(notification_id, "failed", "Max retries exceeded")
                logger.error(f"Push delivery failed after {MAX_RETRY_COUNT} attempts: {notification_id}")
        
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON message: {str(e)}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}", exc_info=True)
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)


def start_consumer():
    """Start consuming messages from push queue"""
    logger.info("=" * 60)
    logger.info("Starting Push Service Consumer")
    logger.info("=" * 60)
    logger.info(f"RabbitMQ Host: {RABBITMQ_HOST}:{RABBITMQ_PORT}")
    logger.info(f"Queue Name: {QUEUE_NAME}")
    logger.info(f"User Service: {USER_SERVICE_URL}")
    logger.info(f"Template Service: {TEMPLATE_SERVICE_URL}")
    logger.info(f"Firebase Initialized: {firebase_initialized}")
    logger.info("=" * 60)
    
    while True:
        try:
            # Connect to RabbitMQ
            connection = get_rabbitmq_connection()
            channel = connection.channel()
            
            # Declare queue (idempotent)
            channel.queue_declare(
                queue=QUEUE_NAME,
                durable=True,
                arguments={'x-max-priority': 10}
            )
            
            # Set QoS - process one message at a time
            channel.basic_qos(prefetch_count=1)
            
            # Start consuming
            channel.basic_consume(
                queue=QUEUE_NAME,
                on_message_callback=process_message,
                auto_ack=False
            )
            
            logger.info(f"✓ Push Service ready - waiting for messages on '{QUEUE_NAME}'...")
            channel.start_consuming()
            
        except KeyboardInterrupt:
            logger.info("Shutting down Push Service...")
            break
            
        except pika.exceptions.AMQPConnectionError as e:
            logger.error(f"RabbitMQ connection error: {str(e)}")
            logger.info("Reconnecting in 5 seconds...")
            time.sleep(5)
            
        except Exception as e:
            logger.error(f"Consumer error: {str(e)}", exc_info=True)
            logger.info("Reconnecting in 5 seconds...")
            time.sleep(5)


if __name__ == "__main__":
    start_consumer()