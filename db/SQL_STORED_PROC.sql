CREATE EXTENSION dblink;
CREATE EXTENSION postgis_raster;

DELIMITER \\
CREATE OR REPLACE FUNCTION czs.czs_test_connection_table(schemaname VARCHAR(255), tablename VARCHAR(255), db_host VARCHAR(255), db_port INTEGER, db_name VARCHAR(255), db_user VARCHAR(255), db_password VARCHAR(255))
RETURNS TABLE(i INTEGER)
LANGUAGE plpgsql
AS $$
BEGIN
	RETURN QUERY
	SELECT *
	FROM czs.dblink (
	    'dbname=' || db_name || ' port=' || db_port || ' host=' || db_host || ' user=' || db_user || ' password=' || db_password,
	    'SELECT COUNT(*) FROM ' || schemaname || '.' || tablename
	) AS t1(i INTEGER);
END;$$
;


DELIMITER \\
CREATE OR REPLACE FUNCTION czs.czs_get_geometry_table(schemaname VARCHAR(255), tablename VARCHAR(255), db_host VARCHAR(255), db_port INTEGER, db_name VARCHAR(255), db_user VARCHAR(255), db_password VARCHAR(255), out_crs INT)
RETURNS GEOMETRY
LANGUAGE plpgsql
AS $$
DECLARE
	geom GEOMETRY;
	geom_field_name VARCHAR(100);
		
BEGIN
	-- Get the geometry field name of the external table
	SELECT *
	FROM czs.dblink (
	    'dbname=' || db_name || ' port=' || db_port || ' host=' || db_host || ' user=' || db_user || ' password=' || db_password,
	    'SELECT f_geometry_column FROM geometry_columns'
	) AS t1(geom_col VARCHAR(100)) INTO geom_field_name;
	
	-- Make a union of the geometries for the external table
	SELECT *
	FROM czs.dblink (
	    'dbname=' || db_name || ' port=' || db_port || ' host=' || db_host || ' user=' || db_user || ' password=' || db_password,
	    'SELECT ST_Transform(ST_UNION(' || geom_field_name || '), ' || out_crs || ') FROM ' || schemaname || '.' || tablename
	) AS t1(geom GEOMETRY) INTO geom;
	
	
-------------
	--SELECT ST_Transform(ST_union(ST_Polygon(rast)), 4617) FROM czs.riverice_attawapiskat INTO geom;
	--SELECT ST_Multi(ST_Transform(ST_union(ST_Polygon(rast)), 4617)) FROM czs.raster_file_halifax_mask INTO geom;
-------------
	
	IF ST_GeometryType(geom) <> 'ST_MultiPolygon' THEN
	   geom = ST_Buffer(geom, 1); -- 0.00001 is 1 meter
	END IF;
	
	RETURN geom;
END;$$
;


																  																			  
DELIMITER \\
CREATE OR REPLACE PROCEDURE czs.czs_add_collection_feature(parent_uuid uuid, metadata_uuid uuid, coll_name VARCHAR(100), 
																			  coll_title_en VARCHAR(255), coll_title_fr VARCHAR(255), coll_desc_en TEXT, coll_desc_fr TEXT,
																			  coll_keywords_en CHARACTER VARYING(255)[], coll_keywords_fr CHARACTER VARYING(255)[],
																			  collection_crs INTEGER, provider_type VARCHAR(30), provider_name VARCHAR(30), extent_bbox REAL[], extent_crs VARCHAR(255),
																			  extent_temporal_begin DATE, extent_temporal_end DATE,
																	        link_type VARCHAR(255), link_rel VARCHAR(30), link_title TEXT, link_href TEXT, link_hreflang VARCHAR(30),
																			  tablename VARCHAR(2550), data_id_field VARCHAR(255), data_queryables CHARACTER VARYING(255)[], 
																			  db_host VARCHAR(255), db_port INTEGER, db_name VARCHAR(255), db_user VARCHAR(255), db_password VARCHAR(255), db_search_path CHARACTER VARYING(255)[])
LANGUAGE plpgsql
AS $$
DECLARE
	coll_uuid UUID;
	res INTEGER;
	geom GEOMETRY;
	
BEGIN
	-- Validate table name is set
	IF tablename IS NULL OR LENGTH(TRIM(tablename)) = 0 THEN
		RAISE EXCEPTION 'Table Name not set.'
		         USING ERRCODE = 'XXQUA';
	END IF;

	-- Validate data id field is set
	IF data_id_field IS NULL OR LENGTH(TRIM(data_id_field)) = 0 THEN
		RAISE EXCEPTION 'Data ID Field not set.'
		         USING ERRCODE = 'XXQUA';
	END IF;

	-- Validate db_host is set
	IF db_host IS NULL OR LENGTH(TRIM(db_host)) = 0 THEN
		RAISE EXCEPTION 'Database Host not set.'
		         USING ERRCODE = 'XXQUA';
	END IF;

	-- Validate db_name is set
	IF db_name IS NULL OR LENGTH(TRIM(db_name)) = 0 THEN
		RAISE EXCEPTION 'Database Name not set.'
		         USING ERRCODE = 'XXQUA';
	END IF;

	-- Validate db_user is set
	IF db_user IS NULL OR LENGTH(TRIM(db_user)) = 0 THEN
		RAISE EXCEPTION 'Database User not set.'
		         USING ERRCODE = 'XXQUA';
	END IF;

	-- Validate db_password is set
	IF db_password IS NULL OR LENGTH(TRIM(db_password)) = 0 THEN
		RAISE EXCEPTION 'Database Password not set.'
		         USING ERRCODE = 'XXQUA';
	END IF;

	-- Validate db_search_path is set
	IF db_search_path IS NULL OR CARDINALITY(db_search_path) = 0 THEN
		RAISE EXCEPTION 'Database Search Path not set.'
		         USING ERRCODE = 'XXQUA';
	END IF;
	
	-- Make sure search path includes 'public'
	IF 'public' <> ANY(db_search_path) THEN
		db_search_path = ARRAY_APPEND(db_search_path, 'public');
	END IF;

	-- Validate the connection to the table
	BEGIN
		SELECT czs.czs_test_connection_table(db_search_path[1], tablename, db_host, db_port, db_name, db_user, db_password) INTO res;
   EXCEPTION
   	WHEN OTHERS THEN
         RAISE EXCEPTION 'Table % not found in the specified database connection', (db_search_path[1] || '.' || tablename) 
			         USING ERRCODE = 'XXQUA';
   END;
	
	-- Calculate the geometry from the table features
	BEGIN
		SELECT czs.czs_get_geometry_table(db_search_path[1], tablename, db_host, db_port, db_name, db_user, db_password, 4617) INTO geom;
		
   EXCEPTION
   	WHEN OTHERS THEN
         RAISE EXCEPTION 'Unable to create the resulting geometry from the input table'
					   USING ERRCODE = 'XXQUA';
   END;
	
	-- Add the collection
	CALL czs.czs_add_collection(parent_uuid, metadata_uuid, coll_name, coll_title_en, coll_title_fr, coll_desc_en, coll_desc_fr, coll_keywords_en, coll_keywords_fr,
										 collection_crs, provider_type, provider_name,
										 extent_bbox, extent_crs, extent_temporal_begin, extent_temporal_end, geom,
										 link_type, link_rel, link_title, link_href, link_hreflang, coll_uuid);

	-- Add the provider 'feature' specific information
	INSERT INTO czs.provider_feature_postgres
		(collection_uuid, max_extraction_area, max_feature_elements, data_queryables, data_id_field, data_table, data_host, data_port, data_dbname, data_user, data_password, data_search_path)
		VALUES
		(coll_uuid, 999, 20, data_queryables, data_id_field, tablename, db_host, db_port, db_name, db_user, db_password, db_search_path);
END;$$
;

																	   																			   
DELIMITER \\
CREATE OR REPLACE PROCEDURE czs.czs_add_collection_coverage(parent_uuid uuid, metadata_uuid uuid, coll_name VARCHAR(100), 
																			   coll_title_en VARCHAR(255), coll_title_fr VARCHAR(255), coll_desc_en TEXT, coll_desc_fr TEXT,
																			   coll_keywords_en CHARACTER VARYING(255)[], coll_keywords_fr CHARACTER VARYING(255)[],
																			   collection_crs INTEGER, provider_type VARCHAR(30), provider_name VARCHAR(30), extent_bbox REAL[], extent_crs VARCHAR(255),
																			   extent_temporal_begin DATE, extent_temporal_end DATE, geom_wkt TEXT, geom_crs INTEGER,
																	         link_type VARCHAR(255), link_rel VARCHAR(30), link_title TEXT, link_href TEXT, link_hreflang VARCHAR(30),
																			   cov_data TEXT, format_name VARCHAR(60), format_mimetype VARCHAR(60))
LANGUAGE plpgsql
AS $$
DECLARE
	coll_uuid uuid;
	geom_poly GEOMETRY(MultiPolygon,4617);
BEGIN

	-- Calculate the geometry from the table features
	BEGIN
		SELECT ST_Transform(ST_Multi(ST_GeomFromText(geom_wkt, geom_crs)), 4617) INTO geom_poly;
   EXCEPTION
   	WHEN OTHERS THEN
         RAISE EXCEPTION 'Unable to create the resulting geometry from the provided geometry wkt'
					   USING ERRCODE = 'XXQUA';
   END;

	-- Add the collection
	CALL czs.czs_add_collection(parent_uuid, metadata_uuid, coll_name, coll_title_en, coll_title_fr, coll_desc_en, coll_desc_fr, coll_keywords_en, coll_keywords_fr,
										 collection_crs, provider_type, provider_name,
										 extent_bbox, extent_crs, extent_temporal_begin, extent_temporal_end, geom_poly,
										 link_type, link_rel, link_title, link_href, link_hreflang, coll_uuid);

	-- Add the provider 'coverage' specific information
	INSERT INTO czs.provider_coverage_rasterio
		(collection_uuid, max_extraction_area, data, format_name, format_mimetype)
		VALUES
		(coll_uuid, 20, cov_data, format_name, format_mimetype);
END;$$
;


DELIMITER \\
CREATE OR REPLACE PROCEDURE czs.czs_add_collection(parent_uuid uuid, metadata_uuid uuid, coll_name VARCHAR(100), 
																	coll_title_en VARCHAR(255), coll_title_fr VARCHAR(255), coll_desc_en TEXT, coll_desc_fr TEXT,
																	coll_keywords_en CHARACTER VARYING(255)[], coll_keywords_fr CHARACTER VARYING(255)[],
																	collection_crs INTEGER, provider_type VARCHAR(30), provider_name VARCHAR(30), extent_bbox REAL[], extent_crs VARCHAR(255),
																	extent_temporal_begin DATE, extent_temporal_end DATE, geom GEOMETRY(MultiPolygon,4617),
																	link_type VARCHAR(255), link_rel VARCHAR(30), link_title TEXT, link_href TEXT, link_hreflang VARCHAR(30),
																	coll_uuid INOUT uuid)
LANGUAGE plpgsql
AS $$
DECLARE

BEGIN

	-- Validate provider type
	IF NOT (provider_type = 'feature' OR provider_type = 'coverage') THEN
		RAISE EXCEPTION 'Invalid provider type.'
		         USING ERRCODE = 'XXQUA';
	END IF;

	-- Validate parent_uuid is set
	IF parent_uuid IS NULL THEN
		RAISE EXCEPTION 'Parent UUID not set.'
		         USING ERRCODE = 'XXQUA';
	END IF;

	-- Validate collection name is set
	IF coll_name IS NULL OR LENGTH(TRIM(coll_name)) = 0 THEN
		RAISE EXCEPTION 'Collection Name not set.'
		         USING ERRCODE = 'XXQUA';
	END IF;

	-- Validate collection name doesn't already exist
	IF (SELECT COUNT(*) FROM czs.czs_collection WHERE collection_name = coll_name) > 0 THEN
		RAISE EXCEPTION 'Collection Name % already exists.', coll_name
		         USING ERRCODE = 'XXQUA';
	END IF;

	-- Validate collection title English is set
	IF coll_title_en IS NULL OR LENGTH(TRIM(coll_title_en)) = 0 THEN
		RAISE EXCEPTION 'Collection title in English not set.'
		         USING ERRCODE = 'XXQUA';
	END IF;

	-- Validate collection title French is set
	IF coll_title_fr IS NULL OR LENGTH(TRIM(coll_title_fr)) = 0 THEN
		RAISE EXCEPTION 'Collection title in French not set.'
		         USING ERRCODE = 'XXQUA';
	END IF;
	
	-- Validate the provider name is set
	IF provider_name IS NULL OR LENGTH(TRIM(provider_name)) = 0 THEN
		RAISE EXCEPTION 'Provider name is not set.'
         USING ERRCODE = 'XXQUA';
	END IF;
	
	-- Validate the extent_bbox is set
	IF extent_bbox IS NULL OR CARDINALITY(extent_bbox) = 0 THEN
		RAISE EXCEPTION 'Extent BBox is not set.'
         USING ERRCODE = 'XXQUA';
	END IF;
	
	-- Validate the extent_crs is set
	IF extent_crs IS NULL OR LENGTH(TRIM(extent_crs)) = 0 THEN
		RAISE EXCEPTION 'Extent CRS is not set.'
         USING ERRCODE = 'XXQUA';
	END IF;
	
	-- Proceed
	INSERT INTO czs.czs_collection
	(parent_uuid, metadata_identifier, collection_name, collection_type, collection_title_en, collection_title_fr, collection_description_en, collection_description_fr,
	 collection_keywords_en, collection_keywords_fr, collection_crs, provider_type, provider_name,
	 extents_spatial_bbox, extents_spatial_crs, extents_temporal_begin, extents_temporal_end,
	 geom)
	VALUES
	(parent_uuid, metadata_uuid, coll_name, 'collection', coll_title_en, coll_title_fr, coll_desc_en, coll_desc_fr,
	 coll_keywords_en, coll_keywords_fr, collection_crs, provider_type, provider_name, extent_bbox, extent_crs, extent_temporal_begin, extent_temporal_end,
	 geom) RETURNING collection_uuid INTO coll_uuid;

 	INSERT INTO czs.link
 	(collection_uuid, type, rel, title, href, hreflang)
 	VALUES
 	(coll_uuid, link_type, link_rel, link_title, link_href, link_hreflang);
END;$$
;


DELIMITER \\
CREATE OR REPLACE PROCEDURE czs.czs_update_collection_geom(coll_name VARCHAR(255), INOUT res NUMERIC)
LANGUAGE plpgsql
AS $$
DECLARE
	ds VARCHAR(100);
	tablename VARCHAR(100);
	db_host VARCHAR(100);
	db_port INTEGER;
	db_name VARCHAR(100);
	db_user VARCHAR(100);
	db_password VARCHAR(100);
	geom_poly GEOMETRY(MultiPolygon,4617);
	
BEGIN
	-- Query the information on the collection
   SELECT INTO ds, tablename, db_host, db_port, db_name, db_user, db_password
	       data_search_path[1], data_table, data_host, data_port, data_dbname, data_user, data_password 
	FROM czs.v_czs_collections WHERE collection_name = coll_name AND provider_type = 'feature';
   
	-- Calculate the geometry from the table features
	BEGIN
		SELECT czs.czs_get_geometry_table(ds, tablename, db_host, db_port, db_name, db_user, db_password, 4617) INTO geom_poly;
   EXCEPTION
   	WHEN OTHERS THEN
         RAISE EXCEPTION 'Unable to create the resulting geometry from the input table'
					   USING ERRCODE = 'XXQUA';
   END;
	
	-- Update the geometry
	UPDATE czs.czs_collection
	SET geom = geom_poly
	WHERE collection_name = coll_name;
	GET DIAGNOSTICS res = ROW_COUNT;
END;$$
;


DELIMITER \\
CREATE OR REPLACE PROCEDURE czs.czs_delete_collection(coll_name VARCHAR(255), INOUT res NUMERIC)
LANGUAGE plpgsql
AS $$
DECLARE

BEGIN
	-- Delete the collection and let the constraint do the cascading
	DELETE FROM czs.czs_collection
	WHERE collection_name = coll_name;
	GET DIAGNOSTICS res = ROW_COUNT;
END;$$
;


DELIMITER \\
CREATE OR REPLACE PROCEDURE czs.czs_add_parent(_theme_uuid uuid, _title_en VARCHAR(255), _title_fr VARCHAR(255), INOUT res uuid)
LANGUAGE plpgsql
AS $$
DECLARE

BEGIN
   -- Validate theme_uuid is set
	IF _theme_uuid IS NULL THEN
		RAISE EXCEPTION 'Theme UUID not set.'
		         USING ERRCODE = 'XXQUA';
	END IF;

	-- Validate the parent title in English
   IF _title_en IS NULL OR LENGTH(TRIM(_title_en)) = 0 THEN
   	RAISE EXCEPTION 'Parent title in English not set.'
		         USING ERRCODE = 'XXQUA';
   END IF;

	-- Validate the parent title in French
   IF _title_fr IS NULL OR LENGTH(TRIM(_title_fr)) = 0 THEN
   	RAISE EXCEPTION 'Parent title in French not set.'
		         USING ERRCODE = 'XXQUA';
   END IF;

	-- Validate the parent title_en doesn't already exists
   IF (SELECT COUNT(*) FROM czs.czs_collection_parent WHERE title_en=_title_en) > 0 THEN
   	RAISE EXCEPTION 'Parent title in English already exists.'
		         USING ERRCODE = 'XXQUA';
   END IF;

	-- Validate the parent title_fr doesn't already exists
   IF (SELECT COUNT(*) FROM czs.czs_collection_parent WHERE title_fr=_title_fr) > 0 THEN
   	RAISE EXCEPTION 'Parent title in French already exists.'
		         USING ERRCODE = 'XXQUA';
   END IF;

	-- Insert the parent
	INSERT INTO czs.czs_collection_parent
	(theme_uuid, title_en, title_fr)
	VALUES
	(_theme_uuid, _title_en, _title_fr) RETURNING parent_uuid INTO res;
END;$$
;


DELIMITER \\
CREATE OR REPLACE PROCEDURE czs.czs_delete_parent(_parent_uuid uuid, INOUT res NUMERIC)
LANGUAGE plpgsql
AS $$
DECLARE

BEGIN
   -- Validate parent_uuid is set
	IF _parent_uuid IS NULL THEN
		RAISE EXCEPTION 'Parent UUID not set.'
		         USING ERRCODE = 'XXQUA';
	END IF;

	-- Validate the parent has no Collections
	IF (SELECT COUNT(*) FROM czs.czs_collection WHERE parent_uuid=_parent_uuid) > 0 THEN
		RAISE EXCEPTION 'Can''t delete a Parent which has has linked Collections.'
		         USING ERRCODE = 'XXQUA';
	END IF;

	-- Delete the parent
	DELETE FROM czs.czs_collection_parent
	WHERE parent_uuid = _parent_uuid;
	GET DIAGNOSTICS res = ROW_COUNT;
END;$$
;
