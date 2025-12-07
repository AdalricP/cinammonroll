import os
import asyncio
from aiohttp import web
import socketio

# Initialize Socket.IO server
sio = socketio.AsyncServer(cors_allowed_origins='*')
app = web.Application()
sio.attach(app)

# Serve static files
static_path = os.path.join(os.path.dirname(__file__), 'static')
routes = web.RouteTableDef()

@routes.get('/')
async def index(request):
    return web.FileResponse(os.path.join(static_path, 'index.html'))

# NOTE: app.router.add_static is called at the bottom, so we don't need a route for /static here.


@routes.post('/api/press')
async def handle_press(request):
    data = await request.json()
    digit = data.get('digit')
    print(f"Server received press: {digit}")
    
    if digit:
        # Emit event to all connected clients (the GUI)
        await sio.emit('press', {'digit': digit})
        return web.json_response({'status': 'ok', 'digit': digit})
    
    return web.json_response({'status': 'error', 'message': 'No digit provided'}, status=400)

@routes.post('/api/transcription')
async def handle_transcription(request):
    data = await request.json()
    role = data.get('role', 'system')
    text = data.get('text', '')
    
    await sio.emit('transcript', {'role': role, 'text': text})
    return web.json_response({'status': 'ok'})

app.add_routes(routes)
app.router.add_static('/static', static_path)

async def start_server(host='localhost', port=8000):
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host, port)
    print(f"Gym Server running on http://{host}:{port}")
    await site.start()
    return runner

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_server())
    loop.run_forever()
