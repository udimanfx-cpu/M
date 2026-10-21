import asyncio, json, re
from contextlib import asynccontextmanager
from typing import Set
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

clients: Set[WebSocket] = set()
tiktok_client = None
tiktok_task = None
current_username = None

async def broadcast(payload):
    dead=[]
    message=json.dumps(payload, ensure_ascii=False)
    for ws in list(clients):
        try: await ws.send_text(message)
        except Exception: dead.append(ws)
    for ws in dead: clients.discard(ws)

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await stop_tiktok()

app=FastAPI(title='TikTok Printer Bridge', lifespan=lifespan)
app.mount('/static', StaticFiles(directory='.'), name='static')

@app.get('/')
async def index(): return FileResponse('index.html')

class ConnectBody(BaseModel): username: str

async def stop_tiktok():
    global tiktok_client, tiktok_task, current_username
    client=tiktok_client; task=tiktok_task
    tiktok_client=None; tiktok_task=None; current_username=None
    if client:
        try: await client.stop()
        except Exception: pass
    if task and not task.done():
        task.cancel()
        try: await task
        except BaseException: pass

@app.post('/api/connect')
async def connect(body: ConnectBody):
    global tiktok_client, tiktok_task, current_username
    username=re.sub(r'^@','',body.username.strip())
    if not username or not re.fullmatch(r'[A-Za-z0-9._]{1,50}',username):
        raise HTTPException(400,'Username TikTok tidak valid.')
    await stop_tiktok()
    try:
        from TikTokLive import TikTokLiveClient
        from TikTokLive.events import ConnectEvent, DisconnectEvent, CommentEvent, LikeEvent, GiftEvent
    except Exception as e:
        raise HTTPException(500,'Pustaka TikTokLive belum terpasang. Jalankan installer terlebih dahulu.') from e
    client=TikTokLiveClient(unique_id='@'+username)
    tiktok_client=client; current_username=username

    @client.on(ConnectEvent)
    async def on_connect(event):
        await broadcast({'type':'status','message':'Terhubung ke LIVE @'+username})

    @client.on(DisconnectEvent)
    async def on_disconnect(event):
        await broadcast({'type':'status','message':'Koneksi LIVE terputus'})

    @client.on(CommentEvent)
    async def on_comment(event):
        await broadcast({'type':'comment','nickname':getattr(event.user,'nickname','Penonton'),'unique_id':getattr(event.user,'unique_id',''),'comment':getattr(event,'comment','')})

    @client.on(LikeEvent)
    async def on_like(event):
        await broadcast({'type':'like','nickname':getattr(event.user,'nickname','Penonton'),'count':getattr(event,'count',1),'total':getattr(event,'total',0)})

    @client.on(GiftEvent)
    async def on_gift(event):
        # For streakable gifts, process only the final event to avoid duplicate prints.
        streakable=getattr(event.gift,'streakable',False)
        streaking=getattr(event,'streaking',False)
        if streakable and streaking: return
        await broadcast({'type':'gift','nickname':getattr(event.user,'nickname','Penonton'),'gift':getattr(event.gift,'name','Gift'),'repeat_count':getattr(event,'repeat_count',1),'diamond_count':getattr(event.gift,'diamond_count',0)})

    async def runner():
        try:
            await client.start()
        except asyncio.CancelledError: raise
        except Exception as e:
            await broadcast({'type':'error','message':'Gagal tersambung: '+str(e)[:220]})
    tiktok_task=asyncio.create_task(runner())
    await broadcast({'type':'status','message':'Sedang menghubungkan ke @'+username+'…'})
    return {'ok':True,'message':'Sedang menghubungkan ke @'+username+'…'}

@app.post('/api/disconnect')
async def disconnect():
    await stop_tiktok()
    await broadcast({'type':'status','message':'Terputus dari TikTok LIVE'})
    return {'ok':True}

@app.websocket('/ws')
async def websocket_endpoint(ws: WebSocket):
    await ws.accept(); clients.add(ws)
    await ws.send_text(json.dumps({'type':'status','message':'Server siap'}))
    try:
        while True: await ws.receive_text()
    except WebSocketDisconnect: clients.discard(ws)
    except Exception: clients.discard(ws)
