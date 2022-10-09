import fastapi

from kafka_utils.producer import EventKafkaProducer


async def event_producer_handler(request: fastapi.Request) -> EventKafkaProducer:
    return request.app.state.event_producer


event_producer_dep = fastapi.Depends(event_producer_handler)
