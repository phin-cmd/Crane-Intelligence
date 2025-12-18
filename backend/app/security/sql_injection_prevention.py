"""
SQL Injection Prevention
Advanced SQL injection detection and prevention system
"""

import re
import logging
import hashlib
from typing import Dict, Any, List, Optional, Tuple, Union
from sqlalchemy import text, and_, or_, not_
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import asyncpg
import psycopg2
from psycopg2 import sql

logger = logging.getLogger(__name__)

class SQLInjectionDetector:
    """Advanced SQL Injection Detection System"""
    
    def __init__(self):
        # SQL injection patterns
        self.injection_patterns = [
            # Basic SQL injection patterns
            r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION)\b)",
            r"(\b(OR|AND)\s+\d+\s*=\s*\d+)",
            r"(\b(OR|AND)\s+'.*?'\s*=\s*'.*?')",
            r"(\b(OR|AND)\s+\".*?\"\s*=\s*\".*?\")",
            r"(\b(OR|AND)\s+\w+\s*=\s*\w+)",
            
            # Comment-based injection
            r"(--|\#|\/\*|\*\/)",
            
            # Union-based injection
            r"(\bUNION\s+(ALL\s+)?SELECT\b)",
            
            # Time-based blind injection
            r"(\b(SLEEP|WAITFOR|DELAY)\s*\(\s*\d+\s*\))",
            
            # Boolean-based blind injection
            r"(\b(OR|AND)\s+\d+\s*=\s*\d+\s*--)",
            r"(\b(OR|AND)\s+'.*?'\s*=\s*'.*?'\s*--)",
            
            # Error-based injection
            r"(\bEXTRACTVALUE\s*\(.*?\))",
            r"(\bUPDATEXML\s*\(.*?\))",
            r"(\bEXP\s*\(.*?\))",
            
            # Function-based injection
            r"(\b(ASCII|CHAR|CONCAT|SUBSTRING|LENGTH|COUNT|SUM|AVG|MAX|MIN)\s*\(.*?\))",
            
            # System function injection
            r"(\b(USER|DATABASE|VERSION|SCHEMA|TABLE_NAME|COLUMN_NAME)\s*\(.*?\))",
            
            # Information schema injection
            r"(\bINFORMATION_SCHEMA\b)",
            r"(\b(SYSOBJECTS|SYSCOLUMNS|SYSTABLES)\b)",
            
            # PostgreSQL specific
            r"(\bpg_sleep\s*\(.*?\))",
            r"(\bpg_user\b)",
            r"(\bpg_database\b)",
            
            # MySQL specific
            r"(\buser\s*\(.*?\))",
            r"(\bdatabase\s*\(.*?\))",
            r"(\bversion\s*\(.*?\))",
            
            # SQL Server specific
            r"(\bxp_cmdshell\b)",
            r"(\bsp_executesql\b)",
            r"(\bOPENROWSET\b)",
            
            # Oracle specific
            r"(\bDUAL\b)",
            r"(\bUSER_TABLES\b)",
            r"(\bUSER_TAB_COLUMNS\b)",
        ]
        
        # Compile patterns for performance
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.injection_patterns]
        
        # Whitelist of safe SQL keywords
        self.safe_keywords = {
            "SELECT", "FROM", "WHERE", "ORDER", "BY", "GROUP", "HAVING",
            "LIMIT", "OFFSET", "JOIN", "INNER", "LEFT", "RIGHT", "OUTER",
            "ON", "AS", "ASC", "DESC", "DISTINCT", "COUNT", "SUM", "AVG",
            "MIN", "MAX", "CASE", "WHEN", "THEN", "ELSE", "END", "IS",
            "NULL", "NOT", "IN", "BETWEEN", "LIKE", "EXISTS", "AND", "OR"
        }
        
        # Dangerous SQL keywords
        self.dangerous_keywords = {
            "DROP", "DELETE", "INSERT", "UPDATE", "ALTER", "CREATE",
            "EXEC", "EXECUTE", "UNION", "SCRIPT", "TRUNCATE", "GRANT",
            "REVOKE", "COMMIT", "ROLLBACK", "SAVEPOINT", "CALL",
            "DECLARE", "SET", "SHOW", "DESCRIBE", "EXPLAIN"
        }
    
    def detect_sql_injection(self, query: str, params: Optional[Dict] = None) -> Tuple[bool, List[str]]:
        """Detect potential SQL injection in query"""
        if not query:
            return False, []
        
        threats = []
        
        # Check for dangerous patterns
        for pattern in self.compiled_patterns:
            matches = pattern.findall(query)
            if matches:
                threats.extend([f"Pattern match: {match}" for match in matches])
        
        # Check for dangerous keywords
        query_upper = query.upper()
        for keyword in self.dangerous_keywords:
            if keyword in query_upper:
                threats.append(f"Dangerous keyword: {keyword}")
        
        # Check for parameter manipulation
        if params:
            for param_name, param_value in params.items():
                if isinstance(param_value, str):
                    # Check if parameter contains SQL keywords
                    param_upper = param_value.upper()
                    for keyword in self.dangerous_keywords:
                        if keyword in param_upper:
                            threats.append(f"Parameter '{param_name}' contains dangerous keyword: {keyword}")
                    
                    # Check for comment injection
                    if any(comment in param_value for comment in ['--', '#', '/*', '*/']):
                        threats.append(f"Parameter '{param_name}' contains comment characters")
        
        # Check for string concatenation
        if "'" in query or '"' in query:
            threats.append("Query contains string literals - use parameterized queries")
        
        # Check for dynamic SQL construction
        if any(op in query_upper for op in ['+', '||', 'CONCAT']):
            threats.append("Query appears to use string concatenation")
        
        return len(threats) > 0, threats
    
    def sanitize_query(self, query: str) -> str:
        """Sanitize SQL query by removing dangerous elements"""
        if not query:
            return ""
        
        # Remove comments
        sanitized = re.sub(r'--.*$', '', query, flags=re.MULTILINE)
        sanitized = re.sub(r'/\*.*?\*/', '', sanitized, flags=re.DOTALL)
        sanitized = re.sub(r'#.*$', '', sanitized, flags=re.MULTILINE)
        
        # Remove multiple spaces
        sanitized = re.sub(r'\s+', ' ', sanitized)
        
        return sanitized.strip()
    
    def validate_query_structure(self, query: str) -> Tuple[bool, List[str]]:
        """Validate SQL query structure"""
        if not query:
            return False, ["Empty query"]
        
        issues = []
        
        # Check for balanced parentheses
        paren_count = query.count('(') - query.count(')')
        if paren_count != 0:
            issues.append("Unbalanced parentheses")
        
        # Check for balanced quotes
        single_quotes = query.count("'") % 2
        double_quotes = query.count('"') % 2
        if single_quotes != 0:
            issues.append("Unbalanced single quotes")
        if double_quotes != 0:
            issues.append("Unbalanced double quotes")
        
        # Check for suspicious patterns
        if ';' in query and not query.strip().endswith(';'):
            issues.append("Multiple statements detected")
        
        return len(issues) == 0, issues

class SQLInjectionPrevention:
    """SQL Injection Prevention System"""
    
    def __init__(self, db_session: Optional[Session] = None):
        self.db_session = db_session
        self.detector = SQLInjectionDetector()
        self.query_cache = {}
        self.blocked_queries = set()
    
    def create_parameterized_query(self, base_query: str, params: Dict[str, Any]) -> Tuple[str, List[Any]]:
        """Create parameterized query to prevent SQL injection"""
        try:
            # Detect potential injection
            is_injection, threats = self.detector.detect_sql_injection(base_query, params)
            if is_injection:
                logger.warning(f"Potential SQL injection detected: {threats}")
                raise ValueError(f"Potential SQL injection: {', '.join(threats)}")
            
            # Validate query structure
            is_valid, issues = self.detector.validate_query_structure(base_query)
            if not is_valid:
                raise ValueError(f"Invalid query structure: {', '.join(issues)}")
            
            # Create parameterized query
            param_list = []
            param_index = 1
            
            for key, value in params.items():
                placeholder = f"${param_index}"
                base_query = base_query.replace(f":{key}", placeholder)
                param_list.append(value)
                param_index += 1
            
            return base_query, param_list
            
        except Exception as e:
            logger.error(f"Error creating parameterized query: {e}")
            raise
    
    def execute_safe_query(self, query: str, params: Optional[Dict[str, Any]] = None, 
                         user_id: Optional[int] = None) -> Any:
        """Execute query with SQL injection prevention"""
        try:
            # Check if query is blocked
            query_hash = hashlib.sha256(query.encode()).hexdigest()
            if query_hash in self.blocked_queries:
                raise ValueError("Query is blocked due to security concerns")
            
            # Detect injection
            is_injection, threats = self.detector.detect_sql_injection(query, params)
            if is_injection:
                logger.warning(f"SQL injection attempt blocked: {threats}")
                self.blocked_queries.add(query_hash)
                raise ValueError(f"SQL injection attempt blocked: {', '.join(threats)}")
            
            # Validate query structure
            is_valid, issues = self.detector.validate_query_structure(query)
            if not is_valid:
                raise ValueError(f"Invalid query structure: {', '.join(issues)}")
            
            # Execute query with parameterized approach
            if self.db_session:
                if params:
                    result = self.db_session.execute(text(query), params)
                else:
                    result = self.db_session.execute(text(query))
                
                return result
            else:
                raise ValueError("No database session available")
                
        except Exception as e:
            logger.error(f"Error executing safe query: {e}")
            raise
    
    def create_safe_select_query(self, table: str, columns: List[str] = None, 
                                where_clause: Optional[str] = None,
                                order_by: Optional[str] = None,
                                limit: Optional[int] = None) -> str:
        """Create a safe SELECT query"""
        try:
            # Validate table name
            if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', table):
                raise ValueError("Invalid table name")
            
            # Build query
            if columns:
                # Validate column names
                for col in columns:
                    if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', col):
                        raise ValueError(f"Invalid column name: {col}")
                columns_str = ', '.join(columns)
            else:
                columns_str = '*'
            
            query = f"SELECT {columns_str} FROM {table}"
            
            # Add WHERE clause if provided
            if where_clause:
                # Basic validation of WHERE clause
                if self.detector.detect_sql_injection(where_clause)[0]:
                    raise ValueError("WHERE clause contains potential SQL injection")
                query += f" WHERE {where_clause}"
            
            # Add ORDER BY if provided
            if order_by:
                if self.detector.detect_sql_injection(order_by)[0]:
                    raise ValueError("ORDER BY clause contains potential SQL injection")
                query += f" ORDER BY {order_by}"
            
            # Add LIMIT if provided
            if limit:
                if not isinstance(limit, int) or limit <= 0:
                    raise ValueError("Invalid LIMIT value")
                query += f" LIMIT {limit}"
            
            return query
            
        except Exception as e:
            logger.error(f"Error creating safe SELECT query: {e}")
            raise
    
    def create_safe_insert_query(self, table: str, data: Dict[str, Any]) -> Tuple[str, List[Any]]:
        """Create a safe INSERT query"""
        try:
            # Validate table name
            if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', table):
                raise ValueError("Invalid table name")
            
            # Validate column names and values
            columns = []
            values = []
            param_list = []
            
            for column, value in data.items():
                if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', column):
                    raise ValueError(f"Invalid column name: {column}")
                
                columns.append(column)
                values.append(f"${len(param_list) + 1}")
                param_list.append(value)
            
            query = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({', '.join(values)})"
            
            return query, param_list
            
        except Exception as e:
            logger.error(f"Error creating safe INSERT query: {e}")
            raise
    
    def create_safe_update_query(self, table: str, data: Dict[str, Any], 
                               where_clause: str, where_params: Dict[str, Any]) -> Tuple[str, List[Any]]:
        """Create a safe UPDATE query"""
        try:
            # Validate table name
            if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', table):
                raise ValueError("Invalid table name")
            
            # Check WHERE clause for injection
            if self.detector.detect_sql_injection(where_clause, where_params)[0]:
                raise ValueError("WHERE clause contains potential SQL injection")
            
            # Build SET clause
            set_clauses = []
            param_list = []
            
            for column, value in data.items():
                if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', column):
                    raise ValueError(f"Invalid column name: {column}")
                
                set_clauses.append(f"{column} = ${len(param_list) + 1}")
                param_list.append(value)
            
            # Add WHERE parameters
            for key, value in where_params.items():
                param_list.append(value)
            
            query = f"UPDATE {table} SET {', '.join(set_clauses)} WHERE {where_clause}"
            
            return query, param_list
            
        except Exception as e:
            logger.error(f"Error creating safe UPDATE query: {e}")
            raise
    
    def create_safe_delete_query(self, table: str, where_clause: str, 
                               where_params: Dict[str, Any]) -> Tuple[str, List[Any]]:
        """Create a safe DELETE query"""
        try:
            # Validate table name
            if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', table):
                raise ValueError("Invalid table name")
            
            # Check WHERE clause for injection
            if self.detector.detect_sql_injection(where_clause, where_params)[0]:
                raise ValueError("WHERE clause contains potential SQL injection")
            
            # Build parameter list
            param_list = []
            for key, value in where_params.items():
                param_list.append(value)
            
            query = f"DELETE FROM {table} WHERE {where_clause}"
            
            return query, param_list
            
        except Exception as e:
            logger.error(f"Error creating safe DELETE query: {e}")
            raise
    
    def get_query_security_report(self, query: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Get comprehensive security report for query"""
        try:
            # Detect injection
            is_injection, threats = self.detector.detect_sql_injection(query, params)
            
            # Validate structure
            is_valid, issues = self.detector.validate_query_structure(query)
            
            # Check for dangerous keywords
            dangerous_keywords = []
            query_upper = query.upper()
            for keyword in self.detector.dangerous_keywords:
                if keyword in query_upper:
                    dangerous_keywords.append(keyword)
            
            # Calculate risk score
            risk_score = 0
            if is_injection:
                risk_score += 50
            if not is_valid:
                risk_score += 30
            if dangerous_keywords:
                risk_score += len(dangerous_keywords) * 10
            if params:
                for param_value in params.values():
                    if isinstance(param_value, str) and any(char in param_value for char in ['--', '#', '/*', '*/']):
                        risk_score += 20
            
            return {
                "query_hash": hashlib.sha256(query.encode()).hexdigest(),
                "is_safe": not is_injection and is_valid,
                "risk_score": min(100, risk_score),
                "injection_detected": is_injection,
                "threats": threats,
                "structure_valid": is_valid,
                "structure_issues": issues,
                "dangerous_keywords": dangerous_keywords,
                "parameter_count": len(params) if params else 0,
                "query_length": len(query),
                "recommendations": self._get_security_recommendations(is_injection, is_valid, dangerous_keywords)
            }
            
        except Exception as e:
            logger.error(f"Error generating security report: {e}")
            return {"error": str(e)}
    
    def _get_security_recommendations(self, is_injection: bool, is_valid: bool, 
                                    dangerous_keywords: List[str]) -> List[str]:
        """Get security recommendations based on analysis"""
        recommendations = []
        
        if is_injection:
            recommendations.append("Use parameterized queries to prevent SQL injection")
            recommendations.append("Validate and sanitize all input parameters")
        
        if not is_valid:
            recommendations.append("Fix query structure issues")
            recommendations.append("Ensure balanced parentheses and quotes")
        
        if dangerous_keywords:
            recommendations.append("Avoid using dangerous SQL keywords in user input")
            recommendations.append("Implement proper access controls")
        
        if not recommendations:
            recommendations.append("Query appears to be secure")
        
        return recommendations
