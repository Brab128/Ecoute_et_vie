from fastapi import FastAPI, Response
from pydantic import BaseModel
import geopandas as gpd
import matplotlib.pyplot as plt
import io
from shapely.geometry import shape

app = FastAPI()

class CarteRequest(BaseModel):
    geojson: dict          # Le GeoJSON envoyé par n8n
    couleur: str = "#4A90D9"
    largeur: int = 6
    hauteur: int = 6

@app.post("/carte")
def carte(req: CarteRequest):
    # Accepte FeatureCollection ou Feature unique
    geojson = req.geojson

    if geojson.get("type") == "FeatureCollection":
        features = geojson["features"]
    elif geojson.get("type") == "Feature":
        features = [geojson]
    else:
        # Géométrie brute
        features = [{"type": "Feature", "geometry": geojson, "properties": {}}]

    gdf = gpd.GeoDataFrame.from_features(features)
    gdf = gdf.set_crs("EPSG:4326")

    fig, ax = plt.subplots(figsize=(req.largeur, req.hauteur))
    gdf.plot(ax=ax, color=req.couleur, edgecolor="white")
    ax.axis("off")

    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight", dpi=150)
    plt.close()

    return Response(content=buf.getvalue(), media_type="image/png")
