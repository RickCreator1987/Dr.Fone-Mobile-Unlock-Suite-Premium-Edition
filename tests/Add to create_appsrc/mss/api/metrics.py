from mss.api.metrics import metrics_response

@app.get("/metrics")
def metrics() -> Response:
    return metrics_response()