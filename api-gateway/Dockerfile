# Stage 1: Build the application using JDK (compilation environment)
FROM eclipse-temurin:17-jdk-focal AS build

WORKDIR /app

# Copy the build configuration file and source code
# Assuming you are using Maven:
COPY pom.xml .
COPY src ./src

# Install Maven and build the Spring Boot application
# The -DskipTests flag skips running unit tests during the container build
RUN apt-get update && apt-get install -y maven
RUN mvn clean package -DskipTests

# Stage 2: Create the final lightweight runtime image
FROM eclipse-temurin:17-jre-focal

# Set the argument for the path to the JAR file
ARG JAR_FILE=/app/target/*.jar

# Copy the generated JAR file from the 'build' stage
COPY --from=build ${JAR_FILE} app.jar

# Expose the default port for the service (will be mapped by docker-compose)
# User Service: 8081 / API Gateway: 8080 (based on your properties)
# EXPOSE 8081 or EXPOSE 8080 depending on the application. Spring handles this via server.port
EXPOSE 8080

# Define the entry point to run the application
ENTRYPOINT ["java", "-jar", "app.jar"]