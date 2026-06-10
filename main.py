from fastapi import FastAPI, Response
from pydantic import BaseModel
from typing import List, Optional
import geopandas as gpd
import matplotlib.pyplot as plt
import requests
import io
from shapely.geometry import shape

app = FastAPI()

# --- Modèles ---

class CarteGeoJSON(BaseModel):
    geojson: dict
    couleur: str = "#4A90D9"
    largeur: int = 6
    hauteur: int = 6

class Entite(BaseModel):
    code: str
    nom: str = ""
    contour: dict

class CarteEntites(BaseModel):
    entites: List[Entite]
    couleur: str = "#4A90D9"
    largeur: int = 6
    hauteur: int = 6
    
class CarteEntites(BaseModel):
    entites: List[Entite]
    couleur: str = "#4A90D9"        # couleur de remplissage
    couleur_contour: str = "black"  # couleur du contour
    epaisseur_contour: float = 1.0  # épaisseur du trait
    remplissage: bool = True        # False = contours seuls
    fond: str = "white"             # couleur du fond
    largeur: int = 6
    hauteur: int = 6
    dpi: int = 150
# --- Helper commun ---

def render_gdf(gdf, req):
    fig, ax = plt.subplots(figsize=(req.largeur, req.hauteur))
    fig.patch.set_facecolor(req.fond)
    
    facecolor = req.couleur if req.remplissage else "none"
    
    gdf.plot(
        ax=ax,
        color=facecolor,
        edgecolor=req.couleur_contour,
        linewidth=req.epaisseur_contour
    )
    ax.axis("off")
    ax.set_facecolor(req.fond)
    
    buf = io.BytesIO()
    plt.savefig(buf, format="png", bbox_inches="tight", dpi=req.dpi, facecolor=req.fond)
    plt.close()
    return Response(content=buf.getvalue(), media_type="image/png")

# --- Endpoint 1 : GeoJSON brut ---

@app.post("/carte")
def carte_geojson(req: CarteGeoJSON):
    geojson = req.geojson
    if geojson.get("type") == "FeatureCollection":
        features = geojson["features"]
    elif geojson.get("type") == "Feature":
        features = [geojson]
    else:
        features = [{"type": "Feature", "geometry": geojson, "properties": {}}]
    gdf = gpd.GeoDataFrame.from_features(features).set_crs("EPSG:4326")
    return render_gdf(gdf, req.couleur, req.largeur, req.hauteur)

# --- Endpoint 2 : liste d'entités avec contour ---

@app.post("/carte/entites")
def carte_entites(req: CarteEntites):
    rows = [
        {"code": e.code, "nom": e.nom, "geometry": shape(e.contour)}
        for e in req.entites
    ]
    gdf = gpd.GeoDataFrame(rows, geometry="geometry", crs="EPSG:4326")
    return render_gdf(gdf, req.couleur, req.largeur, req.hauteur)

# --- Endpoint 3 : par code département (GET) ---

@app.get("/carte/{code}")
def carte_departement(code: str, couleur: str = "#4A90D9"):
    data = requests.get(
        "https://geo.api.gouv.fr/departements?fields=nom,code&geometry=contour"
    ).json()
    rows = [
        {"code": d["code"], "nom": d.get("nom", ""), "geometry": shape(d["geometry"])}
        for d in data if "geometry" in d
    ]
    gdf = gpd.GeoDataFrame(rows, geometry="geometry", crs="EPSG:4326")
    dep = gdf[gdf["code"] == code]
    if dep.empty:
        return {"error": f"Département {code} non trouvé"}
    return render_gdf(dep, couleur, 6, 6)
