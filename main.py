from fastapi import FastAPI, Response
import geopandas as gpd
import matplotlib.pyplot as plt
import requests
import io

app = FastAPI()

@app.get("/carte/{code}")
def carte(code: str, couleur: str = "#4A90D9"):
    # URL corrigée : format GeoJSON avec géométrie incluse
    url = "https://geo.api.gouv.fr/departements?fields=nom,code&geometry=contour&format=geojson"
    geojson = requests.get(url).json()

    gdf = gpd.GeoDataFrame.from_features(geojson["features"])
    gdf = gdf.set_crs("EPSG:4326")

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
