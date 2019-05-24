from luc import searcher
from flask import Flask, request, jsonify

app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
app.config['JSON_AS_ASCII'] = False
index = "path_to_index_folder"

s = searcher.Searcher(index)


@app.route('/')
def home():
    with open(index + "/last_updated.txt") as f:
        return f.read()


@app.route('/reload')
def reload():
    global s
    s = searcher.Searcher(index)
    return "done"


@app.route('/views')
def search_views():
    dmy = request.args.get('date', None)
    period = request.args.get('period', 'year')
    if dmy:
        dmy = dmy.split("-")
    seg = request.args.get('segment', None)
    seg, sid = which_segment(seg)
    res = dict()
    res["response"] = s.search_views(dmy=dmy, period=period, site_id=sid, segment=seg)
    return jsonify(res)


@app.route('/visits')
def search_visits():
    dmy = request.args.get('date', None)
    period = request.args.get('period', 'year')
    if dmy:
        dmy = dmy.split("-")
    seg = request.args.get('segment', None)
    seg, sid = which_segment(seg)
    res = dict()
    res["response"] = s.search_visits(dmy=dmy, period=period, site_id=sid, segment=seg)
    return jsonify(res)


@app.route('/country')
def search_country():
    dmy = request.args.get('date', None)
    period = request.args.get('period', 'year')
    if dmy:
        dmy = dmy.split("-")
    seg = request.args.get('segment', None)
    seg, sid = which_segment(seg)
    res = dict()
    res["response"] = s.search_country(dmy=dmy, period=period, site_id=sid, segment=seg)
    return jsonify(res)


@app.route('/urls')
def search_urls():
    dmy = request.args.get('date', None)
    period = request.args.get('period', 'year')
    if dmy:
        dmy = dmy.split("-")
    seg = request.args.get('segment', None)
    seg, sid = which_segment(seg, route="urls")
    res = dict()
    res["response"] = s.search_urls(dmy=dmy, period=period, site_id=sid, segment=seg)
    return jsonify(res)


@app.route('/handle')
def search_hanlde():
    dmy = request.args.get('date', None)
    period = request.args.get('period', 'year')
    segment = None
    if dmy:
        dmy = dmy.split("-")
    h = request.args.get('h')
    seg = request.args.get('segment', None)
    sid = [2, 4]
    res = dict()
    if seg == "views":
        sid = 2
        segment = "pageUrl=@lindat.mff.cuni.cz/repository/xmlui/handle"
        res["response"] = s.search_handle(dmy=dmy, period=period, site_id=sid, handle=h, segment=segment)
    elif seg == "downloads":
        sid = 4
        res["response"] = s.search_handle(dmy=dmy, period=period, site_id=sid, handle=h, segment=segment)
    else:
        res = dict()
        sid = 2
        segment = "pageUrl=@lindat.mff.cuni.cz/repository/xmlui/handle"
        res["response"] = {}
        res["response"]["views"] = s.search_handle(dmy=dmy, period=period, site_id=sid, handle=h, segment=segment)
        sid = 4
        res["response"]["downloads"] = s.search_handle(dmy=dmy, period=period, site_id=sid, handle=h, segment=None)

    return jsonify(res)


def which_segment(seg, route=None):
    sid = [2, 4]
    if seg == "repository":
        if route == "urls":
            seg = "pageUrl=@lindat.mff.cuni.cz/repository/xmlui/handle"
        else:
            seg = "pageUrl=@lindat.mff.cuni.cz/repository"
        sid = 2
    elif seg == "downloads":
        seg = None
        sid = 4
    elif seg == "lrt":
        if route == "urls":
            seg = "pageUrl=@lindat.mff.cuni.cz/repository/xmlui/handle;pageUrl=@/LRT-"
        else:
            seg = "pageUrl=@lindat.mff.cuni.cz/repository;pageUrl=@/LRT-"
        sid = 2
    elif seg == "lrt-downloads":
        seg = "pageUrl=@lindat.mff.cuni.cz/repository;pageUrl=@/LRT-"
        sid = 4
    elif seg == "services":
        seg = "pageUrl=@lindat.mff.cuni.cz/services"
        sid = 2
    elif seg == "others":
        seg = "pageUrl!@lindat.mff.cuni.cz"
        sid = 2
    else:
        seg = None
    return seg, sid

if __name__ == '__main__':
    app.run(host='0.0.0.0')
