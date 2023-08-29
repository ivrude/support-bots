from bot_app import bot,webhook_path,TOKEN,dp,app
from aiogram import types
from aiohttp import web


async def set_webhook():
    webhook_url=f'https://4250-146-120-100-17.ngrok-free.app{webhook_path}'
    print(webhook_url)
    await bot.set_webhook(webhook_url)
async def on_startup(_):
    await set_webhook()




async def handle_webhook(request):
    url= str(request.url)
    index=url.rfind('/')
    token=url[index+1:]

    if token==TOKEN:
        request_data = await request.json()
        update=types.Update(**request_data)
        await dp.process_update(update)
        return web.Response()
    else:
        return web.Response(status=403)


from aiogram.dispatcher.webhook import get_new_configured_app
app.router.add_post(f'/{TOKEN}', handle_webhook)
if __name__=='__main__':
    app = get_new_configured_app(dispatcher=dp, path=webhook_path)
    app.on_startup.append(on_startup)
    web.run_app(
        app,
        host='0.0.0.0',
        port=5000,
    )