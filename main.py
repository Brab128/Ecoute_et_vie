from fastapi import FastAPI, Response
import geopandas as gpd, matplotlib.pyplot as plt, requests, io

app = FastAPI()

@app.get("/carte/{code}")
def carte(code: str, couleur: str = "#4A90D9"):
    data = requests.get("https://geo.api.gouv.fr/departements?fields=contour,code").json()
    gdf = gpd.GeoDataFrame.from_features([
        {"type": "Feature", "geometry": d["contour"], "properties": {"code": d["code"]}}
        for d in data if "contour" in d
    ])
    fig, ax = plt.subplots(figsize=(6, 6))
    gdf[gdf["code"] == code].plot(ax=ax, color=couleur)
    ax.axis("off")
    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight", dpi=150)
    plt.close()
    return Response(content=buf.getvalue(), media_type="image/png")
