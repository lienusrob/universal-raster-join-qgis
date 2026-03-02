# Universal Raster-to-Point Spatial Join (QGIS Plugin)

A high-performance QGIS processing algorithm designed to solve the "Polygon-on-Polygon" bottleneck when intersecting large grid datasets (UTM quadrants) with reference data (like species registers) within a specific planning area.

*Ein hochperformantes QGIS-Plugin zur Lösung des "Polygon-auf-Polygon"-Flaschenhalses bei der Verschneidung großer Rasterdaten (z.B.  UTM-Kacheln) mit Sachdaten (z.B. Artenkataster vom BFN ) innerhalb eines Planungsgebietes.*

## 🚀 Features
* **Lightning Fast:** Converts grid polygons to centroids on-the-fly to perform a highly optimized spatial point-in-polygon join.
* **The "Centroid Trap" Fix:** Accurately checks if the area mask intersects the *entire* grid cell before extracting the centroid, ensuring edge-cases along narrow corridors (like linear infrastructure) are never missed.
* **Universal CRS Handling:** Automatically harmonizes Coordinate Reference Systems (CRS) across the Area Mask, the Grid Layer, and the Data Layer.
* **In-Memory Spatial Index:** Uses `QgsSpatialIndex` for lightning-fast data retrieval even with massive reference datasets.

## 🛠️ Installation
1. Download this repository as a `.zip` file (Click `Code` > `Download ZIP`).
2. Extract the folder and rename it to `universal_raster_join`.
3. Move the folder to your QGIS plugins directory:
   * **Windows:** `%APPDATA%\QGIS\QGIS3\profiles\default\python\plugins\`
   * **macOS:** `~/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/`
   * **Linux:** `~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/`
4. Restart QGIS, go to **Plugins > Manage and Install Plugins**, and check the box next to **Universal Raster Join**.

## 📍 Usage
Find the tool in the QGIS Processing Toolbox under **Universal Tools > Vector Analysis > Raster-to-Point Spatial Join**.
1. **Area Mask:** Your project boundary / planning area (Polygon).
2. **Grid Layer:** The spatial grid, e.g., a UTM 1km grid or INSPIRE 100m grid (Polygon).
3. **Data Layer:** Your reference dataset containing the attributes, e.g., species observations or demographic data (Point/Polygon/Line).
