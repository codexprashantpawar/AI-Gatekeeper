"""Live web view: http://localhost:8000  (Ctrl+C = quit)"""
import argparse, json, os, re, sys, threading, time, webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import cv2
import torch
from app.config import settings
from app.detectors.hf_objects import HFObjectDetector
from app.detectors.plate import PlateDetector, PlateReader
from app.evidence import crop, save_event
from app.types import Detection

GREEN, BLUE = (0, 255, 0), (255, 140, 0)
INFER_W = 640
GW, GH = 160, 90
MAX_EVENTS = 30
IMG = {".jpg", ".jpeg", ".png", ".bmp"}
OK_EXT = IMG | {".mp4", ".avi", ".mov", ".mkv"}
MAX_UP = 500 << 20
UP = settings.output_dir / "uploads"

PAGE = """<!doctype html><html><head><meta charset="utf-8"><title>AI Gate</title>
<style>
*{box-sizing:border-box}
body{margin:0;background:#020a02;color:#33ff33;font-family:"Courier New",monospace;height:100vh;display:flex;flex-direction:column}
header{padding:8px 16px;border-bottom:1px solid #1a7a1a;display:flex;justify-content:space-between;font-size:14px;letter-spacing:2px}
.rec{color:#f33;animation:b 1s steps(2) infinite}@keyframes b{50%{opacity:0}}
main{flex:1;display:grid;grid-template-columns:1fr 380px;gap:10px;padding:10px;min-height:0}
.vid{position:relative;border:1px solid #1a7a1a;background:#000;display:flex;align-items:center;justify-content:center;min-height:0;box-shadow:0 0 18px #0f03}
.vid img{max-width:100%;max-height:100%}
.cross{position:absolute;top:50%;left:50%;width:50px;height:50px;margin:-25px;pointer-events:none;background:linear-gradient(#3f3,#3f3) center/100% 1px no-repeat,linear-gradient(#3f3,#3f3) center/1px 100% no-repeat}
.stat{position:absolute;left:14px;top:10px;font-size:15px;text-shadow:0 0 6px #3f3;z-index:2}
side{display:flex;flex-direction:column;gap:10px;min-height:0;overflow-y:auto}
.card{border:1px solid #1a7a1a;background:#041004;padding:10px;box-shadow:0 0 12px #0f02}
.card h3{margin:0 0 8px;font-size:12px;letter-spacing:3px;color:#1fb81f;font-weight:normal}
#plate img{width:100%;max-height:130px;object-fit:contain;background:#000;border:1px solid #145214;display:block}
#pt{font-size:34px;font-weight:bold;text-align:center;margin-top:8px;text-shadow:0 0 10px #3f3;letter-spacing:4px;word-break:break-all}
#pm{text-align:center;font-size:12px;color:#1fb81f}
.list{flex:1;overflow-y:auto;min-height:140px}
.ev{display:flex;gap:10px;margin-bottom:8px;border:1px solid #145214;padding:6px;background:#020a02}
.ev img{width:110px;height:70px;object-fit:cover;background:#000}
.ev b{display:block;font-size:14px}.ev span{font-size:12px;color:#1fb81f}
.ev.plate{border-color:#3f3}
#pv img,#pv video{width:100%;max-height:110px;object-fit:contain;background:#000;border:1px solid #145214;margin:8px 0;display:block}
button{background:#041004;color:#3f3;border:1px solid #3f3;font-family:inherit;padding:8px;cursor:pointer;letter-spacing:2px}
button:hover{background:#3f3;color:#000}
::-webkit-scrollbar{width:8px}::-webkit-scrollbar-thumb{background:#1a7a1a}
</style></head><body>
<header><div>GATE-AI v1.0 // TARGET ACQUISITION</div><div><span class="rec">&#9679; REC</span> &nbsp; <span id="clk"></span></div></header>
<main>
<div class="vid"><div class="stat" id="st">...</div><img src="/stream"><div class="cross"></div></div>
<side>
<div class="card" id="plate"><h3>&gt; NUMBER PLATE</h3>
<img id="pi" style="display:none"><div id="pt">-- -- ----</div><div id="pm">no plate yet</div></div>
<div class="card list"><h3>&gt; DETECTED LOG</h3><div id="ev"></div></div>
<div class="card"><h3>&gt; UPLOAD VIDEO / IMAGE</h3>
<input type="file" id="f" accept="image/*,video/*" hidden>
<button onclick="document.getElementById('f').click()">[ CHOOSE FILE ]</button>
<div id="pv"></div>
<button id="sc" style="display:none">[ SCAN ]</button></div>
<button onclick="fetch('/camera',{method:'POST'})">[ LIVE CAMERA ]</button>
<button onclick="fetch('/save',{method:'POST'})">[ SAVE EVIDENCE ]</button>
</side></main>
<script>
let last=-1,lp=-1;
const $=i=>document.getElementById(i);
setInterval(()=>$("clk").textContent=new Date().toLocaleTimeString(),500);
async function tick(){
 try{
  const s=await (await fetch("/api/state")).json();
  $("st").textContent=s.status.toUpperCase();
  if(s.plate&&s.plate.id!==lp){lp=s.plate.id;
   $("pi").src="/img/plate?"+lp;$("pi").style.display="block";
   $("pt").textContent=s.plate.text||"UNREAD";$("pm").textContent=s.plate.time+" // conf "+s.plate.conf;}
  if(!s.plate&&lp!==-1){lp=-1;$("pi").style.display="none";$("pt").textContent="-- -- ----";$("pm").textContent="no plate yet";}
  const top=s.events.length?s.events[0].id:-1;
  if(top!==last){last=top;
   $("ev").innerHTML=s.events.map(e=>`<div class="ev ${e.kind}"><img src="/img/${e.id}"><div><b>${(e.text||e.label).toUpperCase()}</b><span>${e.kind} // ${e.conf}<br>${e.time}</span></div></div>`).join("");}
 }catch(e){}
}
let file=null;
$("f").onchange=e=>{file=e.target.files[0];if(!file)return;
 const u=URL.createObjectURL(file);
 $("pv").innerHTML=/(mp4|avi|mov|mkv)$/i.test(file.name)?`<video src="${u}" muted controls></video>`:`<img src="${u}">`;
 $("sc").style.display="block";};
$("sc").onclick=async()=>{if(!file)return;
 $("st").textContent="SCANNING "+file.name+"...";
 try{const r=await fetch("/upload?name="+encodeURIComponent(file.name),{method:"POST",body:file});
  if(!r.ok)alert("Upload failed: "+await r.text());}
 catch(_){alert("Upload rejected (jpg/png/bmp/mp4/avi/mov/mkv only, max 500 MB)");}};
setInterval(tick,600);tick();
</script></body></html>"""


class State:
    def __init__(self):
        self.lock = threading.Lock()
        self.jpg, self.status, self.ms = None, "starting", 0
        self.events, self.imgs, self.plate = [], {}, None
        self.nid, self.save = 0, False
        self.src, self.cam, self.label = None, "", "CAMERA"

    def add(self, d, img):
        if img.size == 0:
            return
        ok, buf = cv2.imencode(".jpg", img, [cv2.IMWRITE_JPEG_QUALITY, 85])
        if not ok:
            return
        text = d.extra.get("text") or ""
        with self.lock:
            self.nid += 1
            ev = dict(id=self.nid, kind=d.kind, label=d.label, text=text,
                      conf=f"{d.confidence:.0%}", time=time.strftime("%H:%M:%S"))
            self.imgs[self.nid] = buf.tobytes()
            self.events.insert(0, ev)
            for old in self.events[MAX_EVENTS:]:
                self.imgs.pop(old["id"], None)
            del self.events[MAX_EVENTS:]
            if d.kind == "plate":
                self.imgs["plate"] = self.imgs[self.nid]
                self.plate = ev

S = State()


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def send(self, body, ctype, code=200):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        p = self.path.split("?")[0]
        if p == "/":
            self.send(PAGE.encode(), "text/html; charset=utf-8")
        elif p == "/api/state":
            with S.lock:
                body = json.dumps(dict(status=S.status, plate=S.plate, events=S.events))
            self.send(body.encode(), "application/json")
        elif p.startswith("/img/"):
            k = p[5:]
            with S.lock:
                b = S.imgs.get(k if k == "plate" else int(k) if k.isdigit() else -1)
            self.send(b or b"", "image/jpeg", 200 if b else 404)
        elif p == "/stream":
            self.send_response(200)
            self.send_header("Content-Type", "multipart/x-mixed-replace; boundary=f")
            self.end_headers()
            try:
                while True:
                    b = S.jpg
                    if b:
                        self.wfile.write(b"--f\r\nContent-Type: image/jpeg\r\nContent-Length: %d\r\n\r\n" % len(b))
                        self.wfile.write(b + b"\r\n")
                    time.sleep(0.04)
            except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError, OSError):
                pass
        else:
            self.send(b"", "text/plain", 404)

    def do_POST(self):
        u = urlparse(self.path)
        if u.path == "/save":
            S.save = True
        elif u.path == "/camera":
            S.src = S.cam
        elif u.path == "/upload":
            n = int(self.headers.get("Content-Length") or 0)
            name = re.sub(r"[^\w.\-]", "_", Path(parse_qs(u.query).get("name", [""])[0]).name)
            if Path(name).suffix.lower() not in OK_EXT or not 0 < n <= MAX_UP:
                return self.send(b"unsupported file type or size", "text/plain", 400)
            UP.mkdir(parents=True, exist_ok=True)
            dst = UP / f"{int(time.time())}_{name}"
            with open(dst, "wb") as f:
                while n:
                    b = self.rfile.read(min(1 << 20, n))
                    if not b:
                        break
                    f.write(b)
                    n -= len(b)
            S.src = str(dst)
        self.send(b"ok", "text/plain")


def gray(f):
    return cv2.resize(cv2.cvtColor(f, cv2.COLOR_BGR2GRAY), (GW, GH)).astype("float32")


def brackets(img, x1, y1, x2, y2, col, t=2):
    n = max(14, min(x2 - x1, y2 - y1) // 4)
    for x, y, sx, sy in ((x1, y1, 1, 1), (x2, y1, -1, 1), (x1, y2, 1, -1), (x2, y2, -1, -1)):
        cv2.line(img, (x, y), (x + sx * n, y), col, t)
        cv2.line(img, (x, y), (x, y + sy * n), col, t)


class Reader(threading.Thread):
    """Keeps only the newest camera frame, so the display never lags."""

    def __init__(self, url):
        super().__init__(daemon=True)
        self.url = int(url) if str(url).isdigit() else url
        self.frame, self.lock = None, threading.Lock()
        self.stop, self.ok = False, False
        self.seq = self.seen = 0
        self.sync = False

    def run(self):
        while not self.stop:
            url = self.url
            local = self.sync = Path(str(url)).is_file()
            if local and Path(str(url)).suffix.lower() in IMG:
                with self.lock:
                    self.frame = cv2.imread(str(url))
                    self.seq += 1
                self.ok = self.frame is not None
                while not self.stop and self.url == url:
                    time.sleep(0.1)
                continue
            cap = cv2.VideoCapture(url)
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            if not cap.isOpened():
                self.ok = False
                time.sleep(1)
                continue
            fps = cap.get(cv2.CAP_PROP_FPS) or 25
            while not self.stop and self.url == url:
                ok, f = cap.read()
                if not ok:
                    self.ok = local  # a file just ended: play it again
                    break
                with self.lock:
                    self.frame = f
                    self.seq += 1
                self.ok = True
                if local:  # file: hold until the AI has seen this frame, then skip ahead to stay in real time
                    t = time.time()
                    while self.seen < self.seq and not self.stop and self.url == url and time.time() - t < 15:
                        time.sleep(0.02)
                    for _ in range(int((time.time() - t) * fps)):
                        cap.grab()
            cap.release()

    def get(self):
        with self.lock:
            return None if self.frame is None else self.frame.copy()


class Detector(threading.Thread):
    """Runs AI in the background on the latest frame."""

    def __init__(self, reader):
        super().__init__(daemon=True)
        self.reader, self.stop = reader, False
        self.objs = HFObjectDetector(settings.hf_object_model, settings.conf_objects)
        self.plates = PlateDetector(settings.plate_weights, settings.conf_plate)
        self.ocr = PlateReader(settings.ocr_model)
        self.out, self.ms = ([], None, 0), 0

    def run(self):
        while not self.stop:
            f = self.reader.get()
            if f is None:
                time.sleep(0.05)
                continue
            seq = self.reader.seq
            t = time.time()
            h, w = f.shape[:2]
            s = INFER_W / w if w > INFER_W else 1.0
            small = cv2.resize(f, (int(w * s), int(h * s))) if s < 1 else f
            dets = [Detection(d.kind, d.label, d.confidence, tuple(v / s for v in d.bbox))
                    for d in self.objs.detect(small)]
            for p in self.plates.detect(f):
                p.extra["text"] = self.ocr.read(crop(f, p.bbox, 0.1))
                dets.append(p)
            self.out = (dets, gray(f), t)
            self.ms = int((time.time() - t) * 1000)
            self.reader.seen = seq


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url", default=settings.camera_url.rstrip("/") + "/video",
                    help="phone URL, .../video stream, RTSP, or 0 for laptop webcam")
    ap.add_argument("--port", type=int, default=8000)
    a = ap.parse_args()

    torch.set_num_threads(max(1, (os.cpu_count() or 4) - 2))
    reader = Reader(a.url)
    S.cam = reader.url
    reader.start()
    detector = Detector(reader)
    detector.start()
    srv = ThreadingHTTPServer(("127.0.0.1", a.port), H)
    srv.daemon_threads = True
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    url = f"http://localhost:{a.port}"
    print(f"Live view running at {url}  (Ctrl+C = quit)")
    webbrowser.open(url)

    last = {}
    try:
        while True:
            if S.src:
                reader.url, S.src = S.src, None
                S.label = "CAMERA" if reader.url == S.cam else Path(reader.url).name.split("_", 1)[-1]
                last.clear()
                with S.lock:
                    S.events.clear()
                    S.imgs.clear()
                    S.plate = None
                with reader.lock:
                    reader.frame = None
                detector.out = ([], None, 0)
            frame = reader.get()
            if frame is None:
                time.sleep(0.03)
                continue
            if reader.sync and reader.seen < reader.seq:  # uploaded file: show a frame only with its own boxes
                S.status = f"scanning {S.label}..."
                time.sleep(0.02)
                continue
            dets, ref, t0 = detector.out
            h, w = frame.shape[:2]
            (dx, dy), resp = cv2.phaseCorrelate(ref, gray(frame)) if ref is not None and not reader.sync else ((0, 0), 1)
            if not reader.sync and (time.time() - t0 > 5 or resp < 0.05):
                dets = []
            dx, dy = dx * w / GW, dy * h / GH
            dets = [Detection(d.kind, d.label, d.confidence,
                              (d.bbox[0] + dx, d.bbox[1] + dy, d.bbox[2] + dx, d.bbox[3] + dy),
                              extra=d.extra) for d in dets]

            view = frame.copy()
            now = time.time()
            for d in dets:
                x1, y1, x2, y2 = map(int, d.bbox)
                col = BLUE if d.kind == "vehicle" else GREEN
                brackets(view, x1 + 5, y1 + 5, x2 + 5, y2 + 5, (0, 70, 0), 3)
                brackets(view, x1, y1, x2, y2, col, 3)
                tag = d.extra.get("text") or ("number plate" if d.kind == "plate" else d.label)
                txt = f"{tag.upper()} {d.confidence:.0%}"
                (tw, th), _ = cv2.getTextSize(txt, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)
                y0 = max(th + 12, y1)
                cv2.rectangle(view, (x1, y0 - th - 12), (x1 + tw + 10, y0), col, -1)
                cv2.putText(view, txt, (x1 + 5, y0 - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1)

                cx, cy = (d.bbox[0] + d.bbox[2]) / 2, (d.bbox[1] + d.bbox[3]) / 2
                key = (d.kind, d.extra.get("text") or d.label, int(cx * 4 / w), int(cy * 4 / h))
                if now - last.get(key, 0) > settings.cooldown_seconds:
                    last[key] = now
                    S.add(d, crop(frame, d.bbox, 0.1))

            if not reader.ok:
                st = "camera disconnected - reconnecting"
            elif frame.mean() < 15:
                st = "image too dark / camera covered"
            else:
                st = f"{S.label} | AI: {detector.ms} ms/frame | detections: {len(dets)}"

            if w > 1280:
             view = cv2.resize(view, (1280, int(h * 1280 / w)))
            ok, buf = cv2.imencode(".jpg", view, [cv2.IMWRITE_JPEG_QUALITY, 92])
            if ok:
                S.jpg = buf.tobytes()
            S.status = st

            if S.save:
                meta, folder = save_event(frame, dets, settings.camera_id)
                print("saved", folder)
            S.save = False
            time.sleep(0.02)
    except KeyboardInterrupt:
        pass
    finally:
        reader.stop = detector.stop = True
        detector.join(5)
        srv.shutdown()


if __name__ == "__main__":
    main()