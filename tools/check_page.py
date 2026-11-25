"""Run the page's scripts in QuickJS against a stub DOM and print what they render.

    python tools/check_page.py index.html <folder with the quickjs and esprima packages> [element ids ...]

There is no browser where this site is built. This catches a script that does not parse or throws,
and shows the text a few elements end up with. It does not check layout.
"""
import json
import re
import sys

sys.path.insert(0, sys.argv[2])
import esprima  # noqa: E402
import quickjs  # noqa: E402

html = open(sys.argv[1], encoding="utf-8").read()
data = dict(re.findall(r'<script type="application/json" id="([^"]+)">(.*?)</script>', html, re.S))
scripts = re.findall(r"<script>\n(.*?)\n</script>", html, re.S)
for script in scripts:
    esprima.parseScript(script)
print("scripts parse:", len(scripts), "data blocks:", sorted(data))

STUB = r"""
var __els = {};
function El(id){ this.id=id; this.innerHTML=''; this.textContent=''; this.value=''; this.children=[]; this.style={}; this.dataset={};
  this.classList={add:function(){},remove:function(){},toggle:function(){},contains:function(){return false;}}; this.attrs={}; this.listeners={}; }
El.prototype.addEventListener=function(t,f){ (this.listeners[t]=this.listeners[t]||[]).push(f); };
El.prototype.setAttribute=function(k,v){ this.attrs[k]=v; };
El.prototype.getAttribute=function(k){ return this.attrs[k]===undefined?null:this.attrs[k]; };
El.prototype.removeAttribute=function(k){ delete this.attrs[k]; };
El.prototype.querySelector=function(){ return new El('q'); };
El.prototype.querySelectorAll=function(){ return []; };
El.prototype.appendChild=function(c){ this.children.push(c); return c; };
El.prototype.closest=function(){ return null; };
El.prototype.focus=function(){}; El.prototype.scrollIntoView=function(){};
El.prototype.insertAdjacentHTML=function(p,h){ this.innerHTML+=h; };
var __data = %s;
var document = {
  getElementById:function(id){ if(__data[id]!==undefined){ var e=new El(id); e.textContent=__data[id]; return e; }
    if(!__els[id]) __els[id]=new El(id); return __els[id]; },
  querySelector:function(){ return new El('q'); }, querySelectorAll:function(){ return []; },
  createElement:function(t){ return new El(t); }, addEventListener:function(){}, body:new El('body'), documentElement:new El('html')
};
var window = { addEventListener:function(){}, matchMedia:function(){ return {matches:false, addEventListener:function(){}}; },
  location:{hash:''}, scrollTo:function(){}, innerWidth:1200, requestAnimationFrame:function(f){ f(); } };
var location = window.location, navigator = {clipboard:{writeText:function(){}}}, history = {replaceState:function(){}};
var localStorage = {getItem:function(){return null;}, setItem:function(){}};
function setTimeout(f){ return 0; } function clearTimeout(){}
"""

# A select starts on its first option, as in a browser. One whose options a script fills in starts on "0".
selected = {}
for ident, inner in re.findall(r'<select[^>]*\sid="([^"]+)"[^>]*>(.*?)</select>', html, re.S):
    first = re.search(r'<option[^>]*\svalue="([^"]*)"', inner)
    selected[ident] = first.group(1) if first else "0"

ctx = quickjs.Context()
ctx.eval(STUB % json.dumps(data))
ctx.eval("var __selected = %s; var __plain = document.getElementById; document.getElementById = function(id){ var e = __plain(id); "
         "if (__selected[id] !== undefined && e.value === '') e.value = __selected[id]; return e; };" % json.dumps(selected))
for n, script in enumerate(scripts):
    try:
        ctx.eval(script)
    except Exception as e:  # a script that throws on load is the thing to find
        print(f"script {n} threw: {e}")
        sys.exit(1)
filled = json.loads(ctx.eval("JSON.stringify(Object.keys(__els).filter(function(k){return __els[k].innerHTML || __els[k].textContent;}))"))
print("elements filled:", len(filled), "of", int(ctx.eval("Object.keys(__els).length")))
for element in sys.argv[3:]:
    text = ctx.eval("(__els[%s]||{innerHTML:''}).innerHTML" % json.dumps(element))
    print(f"[{element}]", re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", text))[:700])
