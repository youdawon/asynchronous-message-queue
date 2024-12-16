# Asynchronous Message Queue Abstraction Library

## Project Description
This project involves designing an asynchronous message queue abstraction library and demonstrating its functionality with two FastAPI-based microservices. The message queue facilitates communication between microservices, combining REST API and WebSocket for data processing and delivery.

## Tech Stack
- Python
- FastAPI
- Redis
- WebSocket
- Docker, Docker Compose
- pytest

## Key Features
1. **Message Queue Library**
   - Provides functionalities for message publishing, subscribing, and filtering.
   - Includes retry logic for handling failed messages.
2. **FastAPI Microservices**
   - **Service A**: Receives data from Client A via REST API and publishes it to the Redis message queue.
   - **Service B**: Consumes data from the Redis queue via polling and delivers it to Client B via WebSocket.
3. **Integration of REST API and WebSocket**
   - Uses REST API for data ingestion and WebSocket for data delivery.
4. **Polling-Based Data Processing**
   - Checks the Redis queue periodically (every 2 seconds) to process data.
5. **Swagger UI**
   - REST API documentation is accessible via **http://localhost:8002/docs**.
6. **Testing**
   - Includes unit tests to validate core functionalities, retry logic, and edge cases.

## System Architecture

Below is the system call flow diagram:

![System Call Flow](./call_flow.png)

## Key Processes
1. **Client A** sends data to **Service A** via REST API.
2. **Service A** receives the data and publishes it to the Redis message queue.
3. **Service B** uses a polling mechanism to consume data from the Redis queue and processes it.
   - Polling is configured with a **2-second interval**.
4. **Service B** delivers the processed data to **Client B** via WebSocket.
5. **Client B** receives the WebSocket messages and processes the results or performs additional actions.

---

## Project Structure
```
asynchronous-message-queue/
├── src/
│   ├── service_a/           # Message publishing service
│   ├── service_b/           # Message polling and WebSocket delivery service
│   ├── message_queue/       # Message queue abstraction library
│   ├── websocket/           # WebSocket-related code
│   ├── utils/               # Utility functions
│   ├── client/              # Client-side code (includes client.py)
├── test/                    # Unit test code
├── requirements.txt         # Python dependencies
├── Dockerfile               # Docker configuration
├── docker-compose.yml       # Docker Compose configuration
```

## Installation and Execution

### 1. Clone th Git repository
Clone the repository to your local device:
```bash
git clone https://github.com/youdawon/asynchronous-message-queue.git
```

### 2. Run Redis and Services
Use Docker Compose to run Redis and both services:
```bash
docker-compose up --build
```

### 3. Check REST API
To test Service A’s REST API, use Swagger UI:
- Swagger UI URL: **http://localhost:8002/docs**
- Use the `POST /messages` endpoint to publish messages.

### 4. Test WebSocket
Access the client web viewer:
- URL: **http://localhost:8003/client/viewer.html**

### 5. Run Unit Tests

Unit tests are provided to validate the core functionalities of the project, including:
- Message publishing and subscribing logic.
- Retry mechanisms for failed messages.
- Edge cases, such as maximum capacity or timeouts.

#### Prerequisites
To run the tests locally, ensure the following dependencies are installed:
1. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
2. The requirements.txt file includes:
- pytest: For running the tests.
- redis: To interact with Redis in the tests.
- pytest-mock: For mocking Redis or other dependencies.

Execute the following command to validate core functionalities and edge cases:
```bash
pytest
```

---

## Testing Instructions

### Load Testing (`test_high_load_publishing_parallel.py`)
- `test_high_load_publishing_parallel.py` is a **load test** for publishing messages in parallel.
- Ensure that the Redis server is running before executing this test.

Run Redis server:
```bash
docker run --name redis -p 6379:6379 -d redis
```

Execute the load test:
```bash
pytest test/test_high_load_publishing_parallel.py
```

### Test Logs
During the test, logs will be recorded in the logs/test_high_load_publishing_parallel.log file. 
This file will contain important information about the test execution.

At the bottom of the log file, you'll find the following key metrics:

- Total Time: The total time taken for the test to complete, from start to finish. This is a crucial metric for evaluating the performance of the system under load.
- Throughput: The number of requests processed per unit of time. This metric indicates the efficiency of the system, showing how many messages were handled per second (or other time units, depending on the test configuration).

These metrics are helpful for assessing the system's ability to handle high loads and its overall performance under stress.

---

## Filter Configuration
The message queue provides a filtering mechanism based on the `filter_mode` and `type` fields, which are configured in the `src/utils/config.py` file.

### Supported Filter Modes:
1. **`allow_all`**: All messages are delivered regardless of their type.
2. **`specific_type`**: Only messages with a specific type (e.g., `serviceB`) are delivered.

### How to Configure Filters:
1. Open the `src/utils/config.py` file in the project directory:
   ```python
   # src/utils/config.py
   FILTER_MODE = "specific_type"  # Change to "allow_all" for unfiltered delivery
   ALLOWED_TYPE = "serviceB"      # Define the type to allow in specific_type mode
   ```

2. Modify the `FILTER_MODE` and `ALLOWED_TYPE` values to your desired settings:
   - `FILTER_MODE`:
     - `"allow_all"`: All messages will be processed and delivered.
     - `"specific_type"`: Only messages with a specific type (as defined in `ALLOWED_TYPE`) will be processed.
   - `ALLOWED_TYPE`:
     - Define the type of messages to be processed (e.g., `serviceB`).

3. Restart the application to apply the changes:
   ```bash
   docker-compose down
   docker-compose up --build
   ```

### Testing the Filter:
- Use the REST API to send a message and observe the behavior based on your `src/utils/config.py` settings.
- Example:
   ```bash
   curl -X POST http://localhost:8002/messages \
   -H "Content-Type: application/json" \
   -d '{
       "content": "Test message",
       "type": "serviceB"
   }'
   ```

- The message will be filtered and delivered according to the `FILTER_MODE` and `ALLOWED_TYPE` values defined in `src/utils/config.py`.
