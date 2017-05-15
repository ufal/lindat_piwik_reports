from luc import searcher
from flask import Flask, request, jsonify
from datetime import date

app = Flask(__name__)
index = "path_to_index_folder"


@app.route('/')
def home():
    with open(index + "/last_updated.txt") as f:
        return f.read()


@app.route('/views')
def search_views():
    s = searcher.Searcher(index)
    dmy = request.args.get('date', None)
    if dmy:
        dmy = dmy.split("-")
    seg = request.args.get('segment', None)
    seg, sid = which_segment(seg)
    return jsonify(s.search_views(dmy=dmy, site_id=sid, segment=seg))


@app.route('/visits')
def search_visits():
    s = searcher.Searcher(index)
    dmy = request.args.get('date', None)
    if dmy:
        dmy = dmy.split("-")
    seg = request.args.get('segment', None)
    seg, sid = which_segment(seg)
    return jsonify(s.search_visits(dmy=dmy, site_id=sid, segment=seg))


@app.route('/country')
def search_country():
    s = searcher.Searcher(index)
    dmy = request.args.get('date', None)
    if dmy:
        dmy = dmy.split("-")
    seg = request.args.get('segment', None)
    seg, sid = which_segment(seg)
    return jsonify(s.search_country(dmy=dmy, site_id=sid, segment=seg))


@app.route('/urls')
def search_urls():
    s = searcher.Searcher(index)
    dmy = request.args.get('date', None)
    if dmy:
        dmy = dmy.split("-")
    seg = request.args.get('segment', None)
    seg, sid = which_segment(seg)
    return jsonify(s.search_urls(dmy=dmy, site_id=sid, segment=seg))


@app.route('/handle')
def search_hanlde():
    s = searcher.Searcher(index)
    dmy = request.args.get('date', None)
    if dmy:
        dmy = dmy.split("-")
    h = request.args.get('h')
    seg = request.args.get('segment', None)
    sid = [2, 4]
    if seg == "views":
        sid = 2
    elif seg == "downloads":
        sid = 4
    return jsonify(s.search_handle(dmy=dmy, site_id=sid, handle=h))


def which_segment(seg):
    sid = [2, 4]
    if seg == "repository":
        seg = "pageUrl=@lindat.mff.cuni.cz/repository"
        sid = 2
    elif seg == "downloads":
        seg = None
        sid = 4
    elif seg == "lrt":
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


