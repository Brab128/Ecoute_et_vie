from fastapi import FastAPI, Response
import geopandas as gpd
import matplotlib.pyplot as plt
import requests
import io
from shapely.geometry import shape

app = FastAPI()

@app.get("/carte/{code}")
def carte(code: str, couleur: str = "#4A90D9"):
    data = requests.get(
        "https://geo.api.gouv.fr/departements?fields=contour,code,nom"
    ).json()

    rows = []
    for d in data:
        if "contour" in d:
            rows.append({
                "code": d["code"],
                "nom": d.get("nom", ""),
                "geometry": shape(d["contour"])
            })

    gdf = gpd.GeoDataFrame(rows, crs="EPSG:4326")
    dep = gdf[gdf["code"] == code]

    if dep.empty:
        return {"error": f"Département {code} non trouvé"}

    fig, ax = plt.subplots(figsize=(6, 6))
    dep.plot(ax=ax, color=couleur, edgecolor="white")
    ax.axis("off")

    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight", dpi=150)
    plt.close()

    return Response(content=buf.getvalue(), media_type="image/png")
