import json
import decimal
import logging
import asyncio
import datetime
from typing import List
from fastapi import FastAPI, WebSocket
import websockets

logger = logging.getLogger(__name__)
app = FastAPI()

# Binance WebSocket URL
URL = "wss://fstream.binance.com/stream?streams=btcusdt@aggTrade/btcusdt@markPrice"


class Socket:
    webSocket: WebSocket


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)
        if isinstance(o, datetime.datetime):
            return o.__str__()
        return super().default(o)


activeConnections: List[Socket] = []


@app.websocket("/market/get_btcusdt_price")
async def get_btcusdt_price(websocket: WebSocket):
    await websocket.accept()
    socket = Socket()
    socket.webSocket = websocket
    activeConnections.append(socket)
    try:
        while True:
            await runbroadcast()
            await asyncio.sleep(1)
    except Exception as e:
        logger.error(f"Error in WebSocket: {e}")
    finally:
        activeConnections.remove(socket)
        logger.info("Socket Disconnected")


async def receive_data():
    async with websockets.connect(URL) as websocket:
        response = await websocket.recv()
        return json.loads(response)


@app.get("/test")
async def runbroadcast():
    try:
        async with websockets.connect(URL) as aaaaws:
            response = await aaaaws.recv()
            data = json.loads(response)

            for connection in activeConnections[:]:  # Copy the list to avoid modification errors
                try:
                    await connection.webSocket.send_text(json.dumps(data, default=str))
                except Exception as e:
                    logger.info("Socket Disconnected.")
                    activeConnections.remove(connection)
                    logger.error(f"Error {e} occurred in broadcast function")

            return data
    except Exception as e:
        logger.error(f"Error {e} occurred in runbroadcast function")
        return {"error": str(e)}

