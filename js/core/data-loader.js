/**
 * Crane Intelligence - Centralized Data Loader
 * Version: 1.0.0
 * Last Updated: 2025-10-15
 * 
 * This module loads and manages crane database from centralized JSON file.
 * Single source of truth for all crane data across the application.
 */

(function(window) {
    'use strict';

    // Crane Database Cache
    let craneDatabase = null;
    let manufacturers = null;

    /**
     * Load crane database from JSON file
     * @returns {Promise<Object>} Crane database object
     */
    async function loadCraneDatabase() {
        if (craneDatabase) {
            return craneDatabase;
        }

        try {
            const response = await fetch('/data/crane-database.json?v=' + Date.now());
            if (!response.ok) {
                throw new Error('Failed to load crane database');
            }
            
            const data = await response.json();
            craneDatabase = data;
            manufacturers = Object.keys(data.manufacturers);
            
            console.log('✅ Crane database loaded:', {
                version: data.version,
                manufacturers: manufacturers.length,
                totalModels: getTotalModels()
            });
            
            return craneDatabase;
        } catch (error) {
            console.error('❌ Error loading crane database:', error);
            // Fallback to embedded data if JSON fails
            return loadFallbackDatabase();
        }
    }

    /**
     * Get list of all manufacturers
     * @returns {Array<string>} Array of manufacturer names
     */
    function getManufacturers() {
        if (!manufacturers) {
            console.warn('⚠️ Crane database not loaded yet');
            return [];
        }
        return manufacturers;
    }

    /**
     * Get models for a specific manufacturer
     * @param {string} manufacturer - Manufacturer name
     * @returns {Array<Object>} Array of crane models
     */
    function getModels(manufacturer) {
        if (!craneDatabase) {
            console.warn('⚠️ Crane database not loaded yet');
            return [];
        }

        const manufacturerData = craneDatabase.manufacturers[manufacturer];
        if (!manufacturerData) {
            console.warn(`⚠️ Manufacturer "${manufacturer}" not found`);
            return [];
        }

        return manufacturerData.models || [];
    }

    /**
     * Get specific model details
     * @param {string} manufacturer - Manufacturer name
     * @param {string} modelName - Model name
     * @returns {Object|null} Model details or null if not found
     */
    function getModelDetails(manufacturer, modelName) {
        const models = getModels(manufacturer);
        return models.find(m => m.model === modelName) || null;
    }

    /**
     * Get total number of models across all manufacturers
     * @returns {number} Total model count
     */
    function getTotalModels() {
        if (!craneDatabase) return 0;
        
        return Object.values(craneDatabase.manufacturers).reduce((total, mfr) => {
            return total + (mfr.models ? mfr.models.length : 0);
        }, 0);
    }

    /**
     * Get manufacturer metadata
     * @param {string} manufacturer - Manufacturer name
     * @returns {Object|null} Manufacturer metadata
     */
    function getManufacturerInfo(manufacturer) {
        if (!craneDatabase) return null;
        
        const mfr = craneDatabase.manufacturers[manufacturer];
        if (!mfr) return null;

        return {
            name: mfr.name,
            country: mfr.country,
            totalModels: mfr.totalModels || (mfr.models ? mfr.models.length : 0)
        };
    }

    /**
     * Search models across all manufacturers
     * @param {string} query - Search query
     * @returns {Array<Object>} Array of matching models with manufacturer info
     */
    function searchModels(query) {
        if (!craneDatabase) return [];
        
        const results = [];
        const searchTerm = query.toLowerCase();

        Object.entries(craneDatabase.manufacturers).forEach(([mfrName, mfrData]) => {
            mfrData.models.forEach(model => {
                if (model.model.toLowerCase().includes(searchTerm) ||
                    model.type.toLowerCase().includes(searchTerm)) {
                    results.push({
                        manufacturer: mfrName,
                        ...model
                    });
                }
            });
        });

        return results;
    }

    /**
     * Fallback database (embedded in code for offline support)
     * This should match the JSON structure but with minimal data
     */
    function loadFallbackDatabase() {
        console.warn('⚠️ Using fallback embedded database');
        
        // Return minimal embedded database
        return {
            version: '1.0.0-fallback',
            manufacturers: {
                'Liebherr': {
                    name: 'Liebherr',
                    country: 'Germany',
                    models: [
                        {"model": "LTM 1200-5.1", "capacity": 200, "type": "All-Terrain Crane", "boomLength": 72},
                        {"model": "LTM 1500-8.1", "capacity": 500, "type": "All-Terrain Crane", "boomLength": 84}
                    ]
                }
            }
        };
    }

    /**
     * Format crane database for legacy code compatibility
     * Returns object in old format: { "Manufacturer": [models...] }
     */
    function getLegacyFormat() {
        if (!craneDatabase) return {};
        
        const legacy = {};
        Object.entries(craneDatabase.manufacturers).forEach(([name, data]) => {
            legacy[name] = data.models || [];
        });
        return legacy;
    }

    // Export public API
    window.CraneDataLoader = {
        load: loadCraneDatabase,
        getManufacturers: getManufacturers,
        getModels: getModels,
        getModelDetails: getModelDetails,
        getTotalModels: getTotalModels,
        getManufacturerInfo: getManufacturerInfo,
        searchModels: searchModels,
        getLegacyFormat: getLegacyFormat
    };

    // Auto-load on DOMContentLoaded
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', loadCraneDatabase);
    } else {
        loadCraneDatabase();
    }

})(window);

