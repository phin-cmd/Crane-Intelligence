"""
Database Management API for Admin Panel
Provides real-time database table management, CRUD operations, and monitoring
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import text, inspect, MetaData
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

from ...core.database import get_db, engine
from ...core.auth import get_current_user
from ...models.user import User

router = APIRouter()

# Database table metadata
TABLE_METADATA = {
    "users": {
        "name": "Users",
        "description": "User accounts and authentication",
        "icon": "users",
        "color": "blue"
    },
    "equipment": {
        "name": "Equipment",
        "description": "Crane and heavy machinery tracking",
        "icon": "truck",
        "color": "green"
    },
    "companies": {
        "name": "Companies",
        "description": "Company information and ownership",
        "icon": "building",
        "color": "purple"
    },
    "maintenance_records": {
        "name": "Maintenance Records",
        "description": "Equipment maintenance history",
        "icon": "wrench",
        "color": "orange"
    },
    "inspection_records": {
        "name": "Inspection Records",
        "description": "Equipment inspection reports",
        "icon": "clipboard-check",
        "color": "yellow"
    },
    "valuation_records": {
        "name": "Valuation Records",
        "description": "Equipment valuation history",
        "icon": "dollar-sign",
        "color": "green"
    },
    "cranes": {
        "name": "Cranes",
        "description": "Crane inventory and specifications",
        "icon": "truck",
        "color": "blue"
    },
    "crane_analyses": {
        "name": "Crane Analyses",
        "description": "Crane analysis results and scores",
        "icon": "chart-line",
        "color": "indigo"
    },
    "crane_listings": {
        "name": "Crane Listings",
        "description": "Market crane listings and data",
        "icon": "list",
        "color": "teal"
    },
    "market_trends": {
        "name": "Market Trends",
        "description": "Market trend analysis data",
        "icon": "trending-up",
        "color": "pink"
    },
    "broker_networks": {
        "name": "Broker Networks",
        "description": "Broker and dealer network data",
        "icon": "network-wired",
        "color": "cyan"
    },
    "performance_metrics": {
        "name": "Performance Metrics",
        "description": "System performance tracking",
        "icon": "gauge",
        "color": "red"
    },
    "crane_valuation_analyses": {
        "name": "Valuation Analyses",
        "description": "Detailed valuation analysis results",
        "icon": "calculator",
        "color": "emerald"
    },
    "market_intelligence": {
        "name": "Market Intelligence",
        "description": "Market intelligence reports",
        "icon": "brain",
        "color": "violet"
    },
    "rental_rates": {
        "name": "Rental Rates",
        "description": "Equipment rental rate data",
        "icon": "clock",
        "color": "amber"
    },
    "data_refresh_logs": {
        "name": "Data Refresh Logs",
        "description": "Data synchronization logs",
        "icon": "refresh",
        "color": "slate"
    },
    "admin_users": {
        "name": "Admin Users",
        "description": "Administrative user accounts",
        "icon": "user-shield",
        "color": "red"
    },
    "content_items": {
        "name": "Content Items",
        "description": "CMS content management",
        "icon": "file-text",
        "color": "blue"
    },
    "media_files": {
        "name": "Media Files",
        "description": "Uploaded media and assets",
        "icon": "image",
        "color": "green"
    },
    "system_settings": {
        "name": "System Settings",
        "description": "Platform configuration settings",
        "icon": "cog",
        "color": "gray"
    },
    "system_logs": {
        "name": "System Logs",
        "description": "Application and system logs",
        "icon": "file-alt",
        "color": "yellow"
    },
    "audit_logs": {
        "name": "Audit Logs",
        "description": "User action audit trail",
        "icon": "history",
        "color": "indigo"
    },
    "notifications": {
        "name": "Notifications",
        "description": "System notifications and alerts",
        "icon": "bell",
        "color": "orange"
    },
    "data_sources": {
        "name": "Data Sources",
        "description": "External data source configurations",
        "icon": "database",
        "color": "teal"
    },
    "background_jobs": {
        "name": "Background Jobs",
        "description": "Scheduled and background tasks",
        "icon": "tasks",
        "color": "purple"
    },
    "email_templates": {
        "name": "Email Templates",
        "description": "Email template management",
        "icon": "envelope",
        "color": "blue"
    },
    "security_events": {
        "name": "Security Events",
        "description": "Security monitoring and events",
        "icon": "shield-alt",
        "color": "red"
    },
    "email_subscriptions": {
        "name": "Email Subscriptions",
        "description": "Newsletter and email subscriptions",
        "icon": "mail-bulk",
        "color": "green"
    }
}

@router.get("/database/tables")
async def get_database_tables(
    db: Session = Depends(get_db)
    # current_user: User = Depends(get_current_user)  # Temporarily disabled for testing
):
    """Get all database tables with metadata and statistics"""
    try:
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        result = []
        for table_name in tables:
            # Get table metadata (use predefined or generate default)
            metadata = TABLE_METADATA.get(table_name, {
                "name": table_name.replace("_", " ").title(),
                "description": f"Database table: {table_name}",
                "icon": "table",
                "color": "gray"
            })
            
            # Get table statistics
            try:
                count_query = text(f"SELECT COUNT(*) FROM {table_name}")
                count_result = db.execute(count_query)
                record_count = count_result.scalar()
            except Exception as e:
                print(f"Error counting records in {table_name}: {e}")
                record_count = 0
            
            # Get table columns
            columns = inspector.get_columns(table_name)
            column_count = len(columns)
            
            # Get table size (approximate) - simplified for SQLite
            try:
                # For SQLite, estimate size based on record count
                table_size = record_count * 100  # Rough estimate
            except:
                table_size = 0
            
            result.append({
                "table_name": table_name,
                "display_name": metadata["name"],
                "description": metadata["description"],
                "icon": metadata["icon"],
                "color": metadata["color"],
                "record_count": record_count,
                "column_count": column_count,
                "approximate_size": table_size,
                "last_updated": datetime.now().isoformat()
            })
        
        return {
            "success": True,
            "tables": result,
            "total_tables": len(result)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch database tables: {str(e)}"
        )

@router.get("/database/tables/{table_name}/columns")
async def get_table_columns(
    table_name: str,
    db: Session = Depends(get_db)
    # current_user: User = Depends(get_current_user)  # Temporarily disabled for testing
):
    """Get column information for a specific table"""
    try:
        inspector = inspect(engine)
        
        if table_name not in inspector.get_table_names():
            raise HTTPException(
                status_code=404,
                detail=f"Table '{table_name}' not found"
            )
        
        columns = inspector.get_columns(table_name)
        primary_keys = inspector.get_pk_constraint(table_name)
        foreign_keys = inspector.get_foreign_keys(table_name)
        
        # Create foreign key lookup
        fk_lookup = {}
        for fk in foreign_keys:
            for column in fk['constrained_columns']:
                fk_lookup[column] = {
                    "referenced_table": fk['referred_table'],
                    "referenced_column": fk['referred_columns'][0] if fk['referred_columns'] else None
                }
        
        result = []
        for column in columns:
            column_info = {
                "name": column['name'],
                "type": str(column['type']),
                "nullable": column['nullable'],
                "default": str(column['default']) if column['default'] is not None else None,
                "primary_key": column['name'] in primary_keys['constrained_columns'],
                "foreign_key": fk_lookup.get(column['name']),
                "autoincrement": column.get('autoincrement', False),
                "comment": column.get('comment')
            }
            result.append(column_info)
        
        return {
            "success": True,
            "table_name": table_name,
            "columns": result,
            "total_columns": len(result)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch table columns: {str(e)}"
        )

@router.get("/database/tables/{table_name}/records")
async def get_table_records(
    table_name: str,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    sort_by: Optional[str] = Query(None),
    sort_order: str = Query("asc", regex="^(asc|desc)$"),
    filters: Optional[str] = Query(None),
    db: Session = Depends(get_db)
    # current_user: User = Depends(get_current_user)  # Temporarily disabled for testing
):
    """Get records from a specific table with pagination, search, and filtering"""
    try:
        inspector = inspect(engine)
        
        if table_name not in inspector.get_table_names():
            raise HTTPException(
                status_code=404,
                detail=f"Table '{table_name}' not found"
            )
        
        # Get table columns for search
        columns = inspector.get_columns(table_name)
        column_names = [col['name'] for col in columns]
        
        # Build base query
        base_query = f"SELECT * FROM {table_name}"
        count_query = f"SELECT COUNT(*) as count FROM {table_name}"
        
        # Add search conditions
        where_conditions = []
        params = {}
        
        if search:
            search_conditions = []
            for i, col in enumerate(column_names):
                search_conditions.append(f"{col} LIKE :search_{i}")
                params[f"search_{i}"] = f"%{search}%"
            where_conditions.append(f"({' OR '.join(search_conditions)})")
        
        # Add filters
        if filters:
            try:
                filter_dict = json.loads(filters)
                for field, value in filter_dict.items():
                    if field in column_names and value is not None:
                        if isinstance(value, str):
                            where_conditions.append(f"{field} = :filter_{field}")
                            params[f"filter_{field}"] = value
                        elif isinstance(value, dict):
                            if 'min' in value:
                                where_conditions.append(f"{field} >= :filter_{field}_min")
                                params[f"filter_{field}_min"] = value['min']
                            if 'max' in value:
                                where_conditions.append(f"{field} <= :filter_{field}_max")
                                params[f"filter_{field}_max"] = value['max']
            except json.JSONDecodeError:
                pass
        
        # Apply WHERE conditions
        if where_conditions:
            where_clause = " AND ".join(where_conditions)
            base_query += f" WHERE {where_clause}"
            count_query += f" WHERE {where_clause}"
        
        # Add sorting
        if sort_by and sort_by in column_names:
            base_query += f" ORDER BY {sort_by} {sort_order.upper()}"
        
        # Add pagination
        offset = (page - 1) * size
        base_query += f" LIMIT {size} OFFSET {offset}"
        
        # Execute queries
        records_result = db.execute(text(base_query), params).fetchall()
        count_result = db.execute(text(count_query), params).fetchone()
        
        total_records = count_result[0] if count_result else 0
        total_pages = (total_records + size - 1) // size
        
        # Convert records to dictionaries
        records = []
        for record in records_result:
            record_dict = {}
            for i, column in enumerate(column_names):
                value = record[i]
                # Convert datetime objects to ISO format
                if hasattr(value, 'isoformat'):
                    record_dict[column] = value.isoformat()
                else:
                    record_dict[column] = value
            records.append(record_dict)
        
        return {
            "success": True,
            "table_name": table_name,
            "records": records,
            "pagination": {
                "page": page,
                "size": size,
                "total_records": total_records,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1
            },
            "search": search,
            "sort_by": sort_by,
            "sort_order": sort_order
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch table records: {str(e)}"
        )

@router.get("/database/tables/{table_name}/stats")
async def get_table_stats(
    table_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get detailed statistics for a specific table"""
    try:
        inspector = inspect(engine)
        
        if table_name not in inspector.get_table_names():
            raise HTTPException(
                status_code=404,
                detail=f"Table '{table_name}' not found"
            )
        
        # Get basic count
        count_query = text(f"SELECT COUNT(*) as count FROM {table_name}")
        count_result = db.execute(count_query).fetchone()
        total_records = count_result[0] if count_result else 0
        
        # Get column statistics
        columns = inspector.get_columns(table_name)
        column_stats = {}
        
        for column in columns:
            col_name = column['name']
            col_type = str(column['type']).lower()
            
            stats = {
                "name": col_name,
                "type": col_type,
                "nullable": column['nullable'],
                "null_count": 0,
                "unique_count": 0,
                "distinct_count": 0
            }
            
            # Get null count
            null_query = text(f"SELECT COUNT(*) FROM {table_name} WHERE {col_name} IS NULL")
            null_result = db.execute(null_query).fetchone()
            stats["null_count"] = null_result[0] if null_result else 0
            
            # Get unique count
            unique_query = text(f"SELECT COUNT(DISTINCT {col_name}) FROM {table_name}")
            unique_result = db.execute(unique_query).fetchone()
            stats["unique_count"] = unique_result[0] if unique_result else 0
            
            # Get distinct count (same as unique for most cases)
            stats["distinct_count"] = stats["unique_count"]
            
            # For numeric columns, get min/max/avg
            if 'int' in col_type or 'float' in col_type or 'numeric' in col_type or 'decimal' in col_type:
                try:
                    numeric_query = text(f"""
                        SELECT 
                            MIN({col_name}) as min_val,
                            MAX({col_name}) as max_val,
                            AVG({col_name}) as avg_val
                        FROM {table_name} 
                        WHERE {col_name} IS NOT NULL
                    """)
                    numeric_result = db.execute(numeric_query).fetchone()
                    if numeric_result:
                        stats["min_value"] = float(numeric_result[0]) if numeric_result[0] is not None else None
                        stats["max_value"] = float(numeric_result[1]) if numeric_result[1] is not None else None
                        stats["avg_value"] = float(numeric_result[2]) if numeric_result[2] is not None else None
                except:
                    pass
            
            # For string columns, get most common values
            if 'varchar' in col_type or 'text' in col_type or 'string' in col_type:
                try:
                    common_query = text(f"""
                        SELECT {col_name}, COUNT(*) as count 
                        FROM {table_name} 
                        WHERE {col_name} IS NOT NULL 
                        GROUP BY {col_name} 
                        ORDER BY count DESC 
                        LIMIT 10
                    """)
                    common_result = db.execute(common_query).fetchall()
                    stats["most_common_values"] = [
                        {"value": row[0], "count": row[1]} 
                        for row in common_result
                    ]
                except:
                    pass
            
            column_stats[col_name] = stats
        
        return {
            "success": True,
            "table_name": table_name,
            "total_records": total_records,
            "column_count": len(columns),
            "column_stats": column_stats,
            "last_updated": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch table statistics: {str(e)}"
        )

@router.post("/database/tables/{table_name}/records")
async def create_table_record(
    table_name: str,
    record_data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new record in a specific table"""
    try:
        inspector = inspect(engine)
        
        if table_name not in inspector.get_table_names():
            raise HTTPException(
                status_code=404,
                detail=f"Table '{table_name}' not found"
            )
        
        # Get table columns
        columns = inspector.get_columns(table_name)
        column_names = [col['name'] for col in columns]
        
        # Validate and prepare data
        insert_data = {}
        for col in columns:
            col_name = col['name']
            if col_name in record_data:
                insert_data[col_name] = record_data[col_name]
            elif not col['nullable'] and col.get('default') is None:
                raise HTTPException(
                    status_code=400,
                    detail=f"Required field '{col_name}' is missing"
                )
        
        # Build insert query
        columns_str = ", ".join(insert_data.keys())
        values_str = ", ".join([f":{key}" for key in insert_data.keys()])
        insert_query = text(f"INSERT INTO {table_name} ({columns_str}) VALUES ({values_str})")
        
        # Execute insert
        result = db.execute(insert_query, insert_data)
        db.commit()
        
        # Get the inserted record
        if hasattr(result, 'lastrowid') and result.lastrowid:
            select_query = text(f"SELECT * FROM {table_name} WHERE id = :id")
            new_record = db.execute(select_query, {"id": result.lastrowid}).fetchone()
            
            if new_record:
                record_dict = {}
                for i, column in enumerate(column_names):
                    value = new_record[i]
                    if hasattr(value, 'isoformat'):
                        record_dict[column] = value.isoformat()
                    else:
                        record_dict[column] = value
                
                return {
                    "success": True,
                    "message": "Record created successfully",
                    "record": record_dict
                }
        
        return {
            "success": True,
            "message": "Record created successfully"
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create record: {str(e)}"
        )

@router.put("/database/tables/{table_name}/records/{record_id}")
async def update_table_record(
    table_name: str,
    record_id: int,
    record_data: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a record in a specific table"""
    try:
        inspector = inspect(engine)
        
        if table_name not in inspector.get_table_names():
            raise HTTPException(
                status_code=404,
                detail=f"Table '{table_name}' not found"
            )
        
        # Get table columns
        columns = inspector.get_columns(table_name)
        column_names = [col['name'] for col in columns]
        
        # Check if record exists
        check_query = text(f"SELECT COUNT(*) FROM {table_name} WHERE id = :id")
        check_result = db.execute(check_query, {"id": record_id}).fetchone()
        
        if not check_result or check_result[0] == 0:
            raise HTTPException(
                status_code=404,
                detail=f"Record with id {record_id} not found"
            )
        
        # Prepare update data
        update_data = {}
        for col in columns:
            col_name = col['name']
            if col_name in record_data and col_name != 'id':  # Don't update primary key
                update_data[col_name] = record_data[col_name]
        
        if not update_data:
            raise HTTPException(
                status_code=400,
                detail="No valid fields to update"
            )
        
        # Build update query
        set_clauses = [f"{key} = :{key}" for key in update_data.keys()]
        update_query = text(f"UPDATE {table_name} SET {', '.join(set_clauses)} WHERE id = :id")
        
        update_data['id'] = record_id
        
        # Execute update
        db.execute(update_query, update_data)
        db.commit()
        
        # Get updated record
        select_query = text(f"SELECT * FROM {table_name} WHERE id = :id")
        updated_record = db.execute(select_query, {"id": record_id}).fetchone()
        
        if updated_record:
            record_dict = {}
            for i, column in enumerate(column_names):
                value = updated_record[i]
                if hasattr(value, 'isoformat'):
                    record_dict[column] = value.isoformat()
                else:
                    record_dict[column] = value
            
            return {
                "success": True,
                "message": "Record updated successfully",
                "record": record_dict
            }
        
        return {
            "success": True,
            "message": "Record updated successfully"
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update record: {str(e)}"
        )

@router.delete("/database/tables/{table_name}/records/{record_id}")
async def delete_table_record(
    table_name: str,
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a record from a specific table"""
    try:
        inspector = inspect(engine)
        
        if table_name not in inspector.get_table_names():
            raise HTTPException(
                status_code=404,
                detail=f"Table '{table_name}' not found"
            )
        
        # Check if record exists
        check_query = text(f"SELECT COUNT(*) FROM {table_name} WHERE id = :id")
        check_result = db.execute(check_query, {"id": record_id}).fetchone()
        
        if not check_result or check_result[0] == 0:
            raise HTTPException(
                status_code=404,
                detail=f"Record with id {record_id} not found"
            )
        
        # Execute delete
        delete_query = text(f"DELETE FROM {table_name} WHERE id = :id")
        db.execute(delete_query, {"id": record_id})
        db.commit()
        
        return {
            "success": True,
            "message": "Record deleted successfully"
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete record: {str(e)}"
        )

@router.get("/database/overview")
async def get_database_overview(
    db: Session = Depends(get_db)
    # current_user: User = Depends(get_current_user)  # Temporarily disabled for testing
):
    """Get overall database statistics and health"""
    try:
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        total_tables = len(tables)
        total_records = 0
        total_size = 0
        
        table_stats = []
        for table_name in tables:
            # Get record count
            try:
                count_query = text(f"SELECT COUNT(*) FROM {table_name}")
                count_result = db.execute(count_query)
                record_count = count_result.scalar()
            except Exception as e:
                print(f"Error counting records in {table_name}: {e}")
                record_count = 0
            total_records += record_count
            
            # Get approximate size
            try:
                size_query = text(f"""
                    SELECT SUM(LENGTH(CAST(*) AS TEXT)) as size
                    FROM {table_name}
                """)
                size_result = db.execute(size_query).fetchone()
                table_size = size_result[0] if size_result and size_result[0] else 0
                total_size += table_size
            except:
                table_size = 0
            
            table_stats.append({
                "table_name": table_name,
                "record_count": record_count,
                "size": table_size,
                "display_name": TABLE_METADATA.get(table_name, {}).get("name", table_name)
            })
        
        # Sort by record count
        table_stats.sort(key=lambda x: x["record_count"], reverse=True)
        
        return {
            "success": True,
            "overview": {
                "total_tables": total_tables,
                "total_records": total_records,
                "total_size": total_size,
                "database_type": "SQLite",
                "last_updated": datetime.now().isoformat()
            },
            "table_stats": table_stats[:10],  # Top 10 tables by record count
            "health_status": "healthy" if total_records > 0 else "empty"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch database overview: {str(e)}"
        )
