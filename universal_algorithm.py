from qgis.core import (QgsProcessing, QgsProcessingAlgorithm, 
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFeatureSink,
                       QgsProcessingException, QgsFeatureRequest,
                       QgsCoordinateTransform, QgsFeature,
                       QgsGeometry, QgsFeatureSink, QgsSpatialIndex, QgsFields,
                       QgsWkbTypes)

class UniversalJoinAlgorithm(QgsProcessingAlgorithm):
    INPUT_AREA = 'INPUT_AREA'
    INPUT_GRID = 'INPUT_GRID'
    INPUT_DATA = 'INPUT_DATA'
    OUTPUT = 'OUTPUT'

    def createInstance(self): return UniversalJoinAlgorithm()
    def name(self): return 'universal_raster_point_join'
    def displayName(self): return 'Raster-to-Point Spatial Join'
    def group(self): return 'Vector Analysis'
    def groupId(self): return 'vector_analysis'
    def shortHelpString(self): return "Checks for polygon intersection, converts grid cells to centroids, and joins attributes from a data layer. Features automatic CRS handling."

    def initAlgorithm(self, config=None):
        self.addParameter(QgsProcessingParameterFeatureSource(
            self.INPUT_AREA, 'Area Mask (e.g., Planning Area)', 
            [QgsProcessing.TypeVectorPolygon]))
            
        self.addParameter(QgsProcessingParameterFeatureSource(
            self.INPUT_GRID, 'Grid Layer (e.g., UTM or Census Polygons)', 
            [QgsProcessing.TypeVectorPolygon]))
            
        self.addParameter(QgsProcessingParameterFeatureSource(
            self.INPUT_DATA, 'Data Layer (e.g., Species, Demographics)', 
            [QgsProcessing.TypeVector]))
        
        self.addParameter(QgsProcessingParameterFeatureSink(
            self.OUTPUT, 'Result (Points with combined attributes)'))

    def processAlgorithm(self, parameters, context, feedback):
        area_source = self.parameterAsSource(parameters, self.INPUT_AREA, context)
        grid_source = self.parameterAsSource(parameters, self.INPUT_GRID, context)
        data_source = self.parameterAsSource(parameters, self.INPUT_DATA, context)

        target_crs = area_source.sourceCrs()
        grid_crs = grid_source.sourceCrs()
        data_crs = data_source.sourceCrs()

        # Combine fields: Grid fields first, then Data fields
        out_fields = QgsFields()
        for field in grid_source.fields(): out_fields.append(field)
        for field in data_source.fields(): out_fields.append(field)

        (sink, dest_id) = self.parameterAsSink(
            parameters, self.OUTPUT, context,
            out_fields, QgsWkbTypes.Point, target_crs)

        if sink is None:
            raise QgsProcessingException('Error creating the output file.')

        # Prepare coordinate transformations
        xform_area_to_grid = QgsCoordinateTransform(target_crs, grid_crs, context.transformContext())
        xform_grid_to_data = QgsCoordinateTransform(grid_crs, data_crs, context.transformContext())
        xform_grid_to_target = QgsCoordinateTransform(grid_crs, target_crs, context.transformContext())

        feedback.pushInfo("Creating spatial index for the Data Layer...")
        data_index = QgsSpatialIndex(data_source.getFeatures())
        data_features = {f.id(): f for f in data_source.getFeatures()}

        total = area_source.featureCount()
        count = 0
        
        for area_feat in area_source.getFeatures():
            if feedback.isCanceled(): break
            
            area_geom = area_feat.geometry()
            area_geom_in_grid_crs = QgsGeometry(area_geom)
            area_geom_in_grid_crs.transform(xform_area_to_grid)
            
            # Bounding box filter for performance
            request = QgsFeatureRequest().setFilterRect(area_geom_in_grid_crs.boundingBox())
            
            for grid_feat in grid_source.getFeatures(request):
                if feedback.isCanceled(): break
                
                # 1. Check if the Area Mask intersects the FULL Grid Polygon
                if area_geom_in_grid_crs.intersects(grid_feat.geometry()):
                    
                    # 2. Only if it intersects, calculate the centroid
                    grid_centroid = grid_feat.geometry().centroid()
                    
                    search_point_data = QgsGeometry(grid_centroid)
                    search_point_data.transform(xform_grid_to_data)
                    
                    # 3. Spatial join with the Data Layer
                    candidate_ids = data_index.intersects(search_point_data.boundingBox())
                    
                    for d_id in candidate_ids:
                        data_feat = data_features[d_id]
                        
                        if data_feat.geometry().intersects(search_point_data):
                            
                            # 4. Create the final feature
                            out_feat = QgsFeature(out_fields)
                            
                            final_geom = QgsGeometry(grid_centroid)
                            final_geom.transform(xform_grid_to_target)
                            
                            out_feat.setGeometry(final_geom)
                            
                            # 5. Merge attributes
                            attrs = grid_feat.attributes() + data_feat.attributes()
                            out_feat.setAttributes(attrs)
                            
                            sink.addFeature(out_feat, QgsFeatureSink.FastInsert)
            
            count += 1
            if total > 0:
                feedback.setProgress(int(count / total * 100))

        return {self.OUTPUT: dest_id}
