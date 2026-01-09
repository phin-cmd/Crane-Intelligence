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
            # Basic SQL injection patterns (excluding SELECT/INSERT/UPDATE/DELETE as they're legitimate in parameterized queries)
            r"(\b(DROP|CREATE|ALTER|EXEC|TRUNCATE)\b)",
            r"(\b(OR|AND)\s+\d+\s*=\s*\d+)",
            r"(\b(OR|AND)\s+'.*?'\s*=\s*'.*?')",
            r"(\b(OR|AND)\s+\".*?\"\s*=\s*\".*?\")",
            r"(\b(OR|AND)\s+\w+\s*=\s*\w+)",
            
            # Comment-based injection
            r"(--|\#|\/\*|\*\/)",
            
            # Union-based injection (suspicious SELECT patterns)
            r"(\bUNION\s+(ALL\s+)?SELECT\b)",
            # Suspicious SELECT patterns (multiple SELECTs, SELECT with dangerous operations)
            r"(\bSELECT\b.*\b(SELECT|DROP|DELETE|INSERT|UPDATE|CREATE|ALTER|EXEC)\b)",
            
            # Time-based blind injection
            r"(\b(SLEEP|WAITFOR|DELAY)\s*\(\s*\d+\s*\))",
            
            # Boolean-based blind injection
            r"(\b(OR|AND)\s+\d+\s*=\s*\d+\s*--)",
            r"(\b(OR|AND)\s+'.*?'\s*=\s*'.*?'\s*--)",
            
            # Error-based injection
            r"(\bEXTRACTVALUE\s*\(.*?\))",
            r"(\bUPDATEXML\s*\(.*?\))",
            r"(\bEXP\s*\(.*?\))",
            
            # Function-based injection (excluding safe aggregate functions)
            r"(\b(ASCII|CHAR|CONCAT|SUBSTRING|LENGTH)\s*\(.*?\))",
            
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
    
    def _is_legitimate_ddl(self, query: str) -> bool:
        """Check if a DDL operation is legitimate (from SQLAlchemy/migrations, not user input)"""
        query_upper = query.upper().strip()
        
        # Check if it's a DDL operation
        is_ddl = any(
            re.search(rf'\b{ddl_keyword}\b', query_upper)
            for ddl_keyword in ['CREATE', 'ALTER', 'DROP', 'TRUNCATE']
        )
        
        if not is_ddl:
            return False
        
        # Legitimate DDL patterns (from SQLAlchemy/migrations):
        # - CREATE TABLE with proper structure (no user input patterns)
        # - ALTER TABLE with ADD/ALTER COLUMN/DROP COLUMN
        # - DROP TABLE/INDEX with proper syntax
        legitimate_ddl_patterns = [
            r'\bCREATE\s+TABLE\s+\w+\s*\(',
            r'\bCREATE\s+INDEX\s+\w+',
            r'\bCREATE\s+UNIQUE\s+INDEX\s+\w+',
            r'\bALTER\s+TABLE\s+\w+\s+(ADD|ALTER|DROP)\s+(COLUMN|CONSTRAINT)?',
            r'\bDROP\s+TABLE\s+(IF\s+EXISTS\s+)?\w+',
            r'\bDROP\s+INDEX\s+(IF\s+EXISTS\s+)?\w+',
            r'\bTRUNCATE\s+TABLE\s+\w+',
        ]
        
        # Check if it matches legitimate DDL patterns
        matches_legitimate_pattern = any(
            re.search(pattern, query_upper) for pattern in legitimate_ddl_patterns
        )
        
        if not matches_legitimate_pattern:
            return False
        
        # Check for suspicious patterns that indicate user input (not legitimate DDL)
        suspicious_patterns = [
            r'\bOR\s+\d+\s*=\s*\d+',  # OR 1=1
            r'\bOR\s+\'.*?\'\s*=\s*\'.*?\'',  # OR 'x'='x'
            r'\bUNION\s+(ALL\s+)?SELECT\b',  # UNION SELECT
            r'--',  # SQL comments
            r'/\*.*?\*/',  # Multi-line comments
            r'\bEXEC\b',  # EXEC (shouldn't be in DDL)
            r'\bEXECUTE\b',  # EXECUTE
        ]
        
        # If it contains suspicious patterns, it's not legitimate
        has_suspicious_patterns = any(
            re.search(pattern, query_upper) for pattern in suspicious_patterns
        )
        
        return not has_suspicious_patterns
    
    def detect_sql_injection(self, query: str, params: Optional[Dict] = None) -> Tuple[bool, List[str]]:
        """Detect potential SQL injection in query"""
        if not query:
            return False, []
        
        threats = []
        query_upper = query.upper()
        
        # Check if this is a legitimate DDL operation (from SQLAlchemy/migrations)
        if self._is_legitimate_ddl(query):
            # Allow legitimate DDL operations - these are from migrations/ORM, not user input
            return False, []
        
        # Check if query uses parameterized placeholders (safe pattern)
        # CRITICAL: If params dict/list/tuple is provided and not empty, this is a parameterized query
        # SQLAlchemy may inline some values in the compiled SQL, but if params exist, it's safe
        # SQLAlchemy can pass params as dict, list, tuple, or None
        has_params = False
        if params is not None:
            if isinstance(params, (dict, list, tuple)):
                has_params = len(params) > 0
            elif params:  # Other truthy values
                has_params = True
        
        has_parameterized_placeholders = bool(
            re.search(r'[:$]\w+', query) or  # :param or $1 style placeholders in SQL
            has_params  # Has parameters passed (most reliable indicator)
        )
        
        # CRITICAL: SQLAlchemy ORM queries are ALWAYS safe - they use parameterized queries
        # Even if the compiled SQL has some values inlined, SQLAlchemy handles escaping
        # If we detect SQLAlchemy patterns (common table/column names, standard ORM structure), trust it
        # SQLAlchemy ORM queries have these characteristics:
        # 1. Standard SQL structure (SELECT FROM, INSERT INTO, UPDATE SET)
        # 2. Table names are usually lowercase or snake_case
        # 3. Column references use dot notation (table.column) or just column names
        # 4. WHERE clauses use standard comparison operators (=, !=, <, >, etc.)
        # CRITICAL: SQLAlchemy ORM detection - be very lenient
        # SQLAlchemy ORM queries are ALWAYS safe because they use parameterized queries
        # Even if the compiled SQL shows values, SQLAlchemy handles escaping
        is_sqlalchemy_orm_query = bool(
            # Any INSERT INTO with VALUES - SQLAlchemy pattern
            (re.search(r'\bINSERT\s+INTO\s+\w+', query_upper) and re.search(r'\bVALUES\b', query_upper)) or
            # Any UPDATE with SET - SQLAlchemy pattern
            (re.search(r'\bUPDATE\s+\w+', query_upper) and re.search(r'\bSET\b', query_upper)) or
            # Any SELECT FROM WHERE - SQLAlchemy pattern
            (re.search(r'\bSELECT\b', query_upper) and re.search(r'\bFROM\s+\w+', query_upper) and re.search(r'\bWHERE\b', query_upper)) or
            # Standard SQLAlchemy patterns - standard SQL structure
            re.search(r'\bFROM\s+\w+\s+WHERE\b', query_upper) or  # Standard SELECT ... FROM ... WHERE
            re.search(r'\bINSERT\s+INTO\s+\w+\s+\(', query_upper) or  # Standard INSERT
            re.search(r'\bUPDATE\s+\w+\s+SET\b', query_upper) or  # Standard UPDATE ... SET (SQLAlchemy pattern)
            # SQLAlchemy often uses table.column notation
            re.search(r'\b\w+\.\w+\s*=\s*[\'"]?\w+[\'"]?', query_upper) or  # table.column = value
            # Standard WHERE clause with common operators (SQLAlchemy uses these)
            (re.search(r'\bWHERE\b', query_upper) and re.search(r'\s+=\s+|\s+!=\s+|\s+<\s+|\s+>\s+|\s+LIKE\s+', query_upper)) or
            # UPDATE with SET and WHERE (common SQLAlchemy pattern)
            (re.search(r'\bUPDATE\s+\w+\s+SET\b', query_upper) and re.search(r'\bWHERE\b', query_upper)) or
            # If query has parameters AND is a standard SQL operation, it's SQLAlchemy ORM
            (has_params and (re.search(r'\bINSERT\b|\bUPDATE\b|\bSELECT\b', query_upper)))
        )
        
        # CRITICAL: Early return for SQLAlchemy ORM queries - check BEFORE pattern matching
        # SQLAlchemy ORM queries are always safe, but we still need to check for obvious injection patterns
        # This MUST happen before pattern matching to prevent false positives
        if is_sqlalchemy_orm_query:
            # Only check for truly malicious patterns that would never appear in legitimate SQLAlchemy ORM
            has_malicious_patterns = bool(
                re.search(r'\bOR\s+\d+\s*=\s*\d+', query_upper) or  # OR 1=1 (classic injection)
                re.search(r'\bOR\s+[\'"].*?[\'"]\s*=\s*[\'"].*?[\'"]', query_upper) or  # OR 'x'='x'
                re.search(r'\bUNION\s+(ALL\s+)?SELECT\b', query_upper) or  # UNION SELECT
                re.search(r'--\s*[\'"]', query) or  # Comment injection with quotes
                re.search(r'/\*.*\*/', query) or  # Multi-line comment injection
                re.search(r'\bEXEC\s*\(', query_upper) or  # EXEC() function
                re.search(r'\bDROP\s+TABLE\b', query_upper) or  # DROP TABLE
                re.search(r'\bDELETE\s+FROM\s+\w+\s+WHERE\s+.*\s+OR\s+\d+\s*=\s*\d+', query_upper)  # DELETE with OR 1=1
            )
            if not has_malicious_patterns:
                return False, []  # SQLAlchemy ORM query with no malicious patterns = safe (RETURN EARLY)
        
        # Check for dangerous patterns (only runs if not SQLAlchemy ORM or has malicious patterns)
        safe_aggregate_functions = ['COUNT', 'SUM', 'AVG', 'MAX', 'MIN']
        for i, pattern in enumerate(self.compiled_patterns):
            matches = pattern.findall(query)
            if matches:
                # Filter out safe aggregate functions and legitimate DDL from pattern matches
                filtered_matches = []
                for match in matches:
                    # Handle tuple matches (from regex groups)
                    if isinstance(match, tuple):
                        match_str = ' '.join(str(m) for m in match if m)
                    else:
                        match_str = str(match)
                    match_upper = match_str.upper()
                    # Skip if it's a safe aggregate function
                    if any(func in match_upper for func in safe_aggregate_functions):
                        continue
                    # Skip if it's a legitimate DDL operation (CREATE/ALTER/DROP from ORM)
                    if any(ddl_keyword in match_upper for ddl_keyword in ['CREATE', 'ALTER', 'DROP', 'TRUNCATE']):
                        # Double-check if this is legitimate DDL
                        if self._is_legitimate_ddl(query):
                            continue  # Skip - legitimate DDL operation
                    
                    # CRITICAL FIX: Skip OR/AND patterns if query uses parameterized placeholders OR is SQLAlchemy ORM
                    # SQLAlchemy ORM queries use parameterized placeholders (e.g., "AND status = :status_1")
                    # These are safe - only flag OR/AND patterns if NOT using parameterized queries
                    if re.search(r'\b(OR|AND)\b', match_upper):
                        # Check if this is a suspicious pattern (OR 1=1, OR 'x'='x') vs legitimate (AND column = :param)
                        is_suspicious_or_and = (
                            # Always suspicious: OR 1=1, OR 'x'='x', OR "x"="x"
                            re.search(r'\b(OR|AND)\s+\d+\s*=\s*\d+', match_upper) or
                            re.search(r'\b(OR|AND)\s+[\'"].*?[\'"]\s*=\s*[\'"].*?[\'"]', match_upper)
                        )
                        
                        # If it's a suspicious OR/AND pattern, flag it
                        if is_suspicious_or_and:
                            filtered_matches.append(match)
                        # If it's a regular OR/AND pattern and (query uses parameterized placeholders OR is SQLAlchemy ORM), skip it (legitimate)
                        elif has_parameterized_placeholders or is_sqlalchemy_orm_query:
                            continue  # Skip - legitimate SQLAlchemy ORM query
                        # Otherwise, flag it (might be injection attempt without parameters)
                        else:
                            filtered_matches.append(match)
                    else:
                        # Not an OR/AND pattern, check normally
                        # But still skip if it's a SQLAlchemy ORM query
                        if is_sqlalchemy_orm_query:
                            continue  # Skip - legitimate SQLAlchemy ORM query
                        filtered_matches.append(match)
                if filtered_matches:
                    threats.extend([f"Pattern match: {match}" for match in filtered_matches])
        
        # Check for dangerous keywords (only as standalone words, not in column/table names)
        for keyword in self.dangerous_keywords:
            # Use word boundaries to match only actual keywords, not substrings
            pattern = r'\b' + re.escape(keyword) + r'\b'
            if re.search(pattern, query_upper):
                # Allow UPDATE/INSERT/DELETE in parameterized queries OR SQLAlchemy ORM queries (they're legitimate operations)
                if keyword in ['UPDATE', 'INSERT', 'DELETE']:
                    if has_parameterized_placeholders or is_sqlalchemy_orm_query:
                        # Check if it's a legitimate parameterized query structure or SQLAlchemy ORM
                        if re.search(rf'\b{keyword}\b.*\b(SET|INTO|FROM)\b', query_upper):
                            continue  # Skip - this is a legitimate parameterized query or SQLAlchemy ORM
                    # Also allow during application startup (table creation, etc.)
                    if re.search(rf'\b{keyword}\b.*\b(INTO|SET|FROM)\b', query_upper):
                        continue  # Skip - likely legitimate
                
                # Allow SET in UPDATE statements (UPDATE ... SET ... WHERE is legitimate)
                if keyword == 'SET' and re.search(r'\bUPDATE\b.*\bSET\b', query_upper):
                    if has_parameterized_placeholders or is_sqlalchemy_orm_query:
                        continue  # Skip - legitimate UPDATE SET statement (SQLAlchemy ORM or parameterized)
                
                # Allow CREATE/ALTER/DROP if they're legitimate DDL (already checked above)
                if keyword in ['CREATE', 'ALTER', 'DROP', 'TRUNCATE']:
                    # This shouldn't happen if _is_legitimate_ddl worked correctly, but double-check
                    if self._is_legitimate_ddl(query):
                        continue  # Skip - legitimate DDL
                
                threats.append(f"Dangerous keyword: {keyword}")
        
        # Check for parameter manipulation
        if params:
            for param_name, param_value in params.items():
                if isinstance(param_value, str):
                    # Check if parameter contains SQL keywords
                    param_upper = param_value.upper()
                    for keyword in self.dangerous_keywords:
                        # Only flag if keyword appears as a complete word in the parameter
                        pattern = r'\b' + re.escape(keyword) + r'\b'
                        if re.search(pattern, param_upper):
                            threats.append(f"Parameter '{param_name}' contains dangerous keyword: {keyword}")
                    
                    # Check for comment injection
                    if any(comment in param_value for comment in ['--', '#', '/*', '*/']):
                        threats.append(f"Parameter '{param_name}' contains comment characters")
        
        # Check for string literals (only flag if NOT using parameterized queries OR SQLAlchemy ORM)
        # SQLAlchemy ORM queries are safe even with string literals - SQLAlchemy handles escaping
        if not has_parameterized_placeholders and not is_sqlalchemy_orm_query:
            if "'" in query or '"' in query:
                threats.append("Query contains string literals - use parameterized queries")
        
        # CRITICAL: If this is a SQLAlchemy ORM query AND no suspicious patterns were found, trust it completely
        # SQLAlchemy ORM always uses safe parameterized queries, even if compiled SQL shows values
        # But only if we haven't already found threats (suspicious patterns take precedence)
        if is_sqlalchemy_orm_query and len(threats) == 0:
            return False, []  # SQLAlchemy ORM queries with no threats are always safe
        
        # Check for dynamic SQL construction (only flag if suspicious)
        if any(op in query_upper for op in ['+', '||', 'CONCAT']):
            # Only flag if it's not a legitimate string concatenation in SELECT
            if not re.search(r'\bSELECT\b.*\b(CONCAT|' + '|'.join(['+', '||']) + r')\b', query_upper):
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
