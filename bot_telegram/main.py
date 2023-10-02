import websockets
from aiogram import types
from aiogram.dispatcher.webhook import get_new_configured_app
from aiohttp import web

from bot_app import TOKEN, app, bot, dp, webhook_path
from bot_app.settings.configs import web_ngrok


async def set_webhook():
    webhook_url = f"{web_ngrok}{webhook_path}"
    print(webhook_url)
    await bot.set_webhook(webhook_url)


async def on_startup(_):
    await set_webhook()
    uri = "ws://localhost:8888/ws/chat/test/"
    websocket_connection = await websockets.connect(uri)

    dp.data["websocket_connection"] = websocket_connection


async def handle_webhook(request):
    url = str(request.url)
    index = url.rfind("/")
    token = url[index + 1 :]

    if token == TOKEN:
        request_data = await request.json()
        update = types.Update(**request_data)
        await dp.process_update(update)
        return web.Response()
    else:
        return web.Response(status=403)


app.router.add_post(f"/{TOKEN}", handle_webhook)
if __name__ == "__main__":
    app = get_new_configured_app(dispatcher=dp, path=webhook_path)
    app.on_startup.append(on_startup)
    web.run_app(
        app,
        host="0.0.0.0",
        port=5000,
    )
