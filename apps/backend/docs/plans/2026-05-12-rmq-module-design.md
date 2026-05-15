# RMQ Module Design

## Goal

Add a reusable RabbitMQ infrastructure module to `fastapi_template` that can:

- publish messages from business modules;
- register and run queue consumers through a shared registry;
- expose debug HTTP endpoints for test publish and consume flows;
- start background listeners during FastAPI startup;
- be reused later by `telegram_rmq_module` without embedding transport logic there.

The module must remain transport-focused and not encode Telegram-specific business behavior.

## Scope

### Included In V1

- shared RMQ client built around one application-level connection;
- standard message envelope;
- reusable publisher API;
- consumer registry and startup listeners;
- exchange, queue, and binding declaration support;
- debug endpoints: health, publish, consume, registrations;
- RabbitMQ service in `infra/docker-compose.yml`;
- configuration via `amqp_url` plus extra runtime settings;
- module-level `README.md` and `AGENTS.md`.

### Not Included In V1

- dead-letter queues as a first-class workflow;
- retry orchestration or backoff policy;
- request-response messaging;
- schema version negotiation;
- idempotency or exactly-once guarantees.

## Message Contract

All published messages use a standard envelope:

- `event`
- `payload`
- `message_id`
- `timestamp`
- `source`
- `correlation_id`

This keeps the transport generic while preserving traceability across modules.

## Architecture

The module lives in `app/modules/rmq_module/` and contains:

- `handlers.py`
  HTTP debug endpoints.
- `schemas/`
  Pydantic DTOs for messages and endpoint payloads.
- `services/client.py`
  Low-level RabbitMQ connection and channel management.
- `services/publisher.py`
  High-level publish API used by business modules.
- `services/registry.py`
  Consumer registration storage and exported registration helper.
- `services/consumer.py`
  Listener loop and incoming message dispatch.
- `services/runtime.py`
  Startup and shutdown lifecycle orchestration.
- `services/topology.py`
  Exchange, queue, and binding specifications.

Exports from `rmq_module` must be sufficient for business modules to publish and subscribe without importing `aio-pika` directly.

## Runtime Flow

### Publish Flow

1. A business module calls the exported publisher.
2. The publisher assembles an `RMQMessage`.
3. The client ensures the target exchange exists.
4. If requested, the client also ensures queue and binding topology.
5. The message is published to RabbitMQ.

### Consume Flow

1. Business modules register consumer handlers in the shared registry.
2. FastAPI startup triggers `rmq_runtime.start()`.
3. Runtime connects to RabbitMQ and declares default topology.
4. Runtime starts one background listener task per registered consumer.
5. Incoming JSON is validated into `RMQMessage`.
6. The registered handler is called.
7. Success leads to `ack`; validation or handler failure leads to `reject(requeue=False)`.

## API Surface

The module exports:

- `RMQMessage`
- `RMQPublisher`
- `RMQConsumerRegistry`
- `ConsumerRegistration`
- `register_consumer(...)`
- `rmq_publisher`
- `rmq_registry`
- `rmq_runtime`

Business modules use these exports instead of talking to RabbitMQ directly.

## HTTP Endpoints

- `GET /api/rmq/health`
  Shows runtime status, registration count, and default topology.
- `GET /api/rmq/registrations`
  Lists registered consumers.
- `POST /api/rmq/publish`
  Publishes a debug message using the shared publisher.
- `POST /api/rmq/consume`
  Pulls one message from a queue for debug purposes.

The consume endpoint is for controlled debugging only. It is not the main production consume path.

## Configuration

Required:

- `amqp_url`

Additional:

- `rabbitmq_default_exchange`
- `rabbitmq_default_exchange_type`
- `rabbitmq_default_queue`
- `rabbitmq_default_routing_key`
- `rabbitmq_prefetch_count`
- `rabbitmq_consumer_enabled`
- `rabbitmq_publish_timeout`
- `rabbitmq_reconnect_interval`

## Docker

`infra/docker-compose.yml` must include a `rabbitmq` service using the management image so local development has:

- AMQP on `5672`
- management UI on `15672`
- persistent storage
- a simple healthcheck

## Error Handling

V1 keeps consumer behavior conservative:

- invalid envelope: reject without requeue;
- handler error: reject without requeue;
- broker/channel issues: reconnect loop handled by runtime.

This avoids silent poison-message loops and keeps retry policy out of scope until there is a concrete need.

## Documentation

`README.md` explains:

- what the module owns;
- how to configure it;
- how to publish messages;
- how to register consumers;
- which debug endpoints exist;
- what V1 does not yet handle.

`AGENTS.md` documents local rules for future edits:

- keep transport logic inside `rmq_module`;
- do not let feature modules import `aio-pika` directly;
- keep the message envelope backward-compatible;
- extend retry and DLQ behavior only through shared runtime primitives.
