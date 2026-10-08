== curl ==
# POST /api/watches  {"url":"https://example.com/pricing","selector":".price","interval":3600,"alert_url":"https://…"}
# GET  /api/watches
# POST /api/watches/1/check
# GET  /api/watches/1/snapshots
# CLI: changewatch add https://example.com/pricing --selector .price --interval 3600

== session plan ==
# Session 1: fetcher (selector + normalize) + differ → tests
# Session 2: scheduler + alerts + api → tests
# Session 3: web templates (diff view) + cli → screenshots → README → CI/Docker/Pages → tag
