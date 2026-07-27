"""
Authentication Service
Handles JWT-based authentication for customer portal
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional
import jwt
import bcrypt
import psycopg2
from psycopg2.extras import RealDictCursor

logger = logging.getLogger(__name__)


class AuthService:
    """Service for authentication and authorization"""
    
    def __init__(self):
        self.secret_key = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
        self.algorithm = os.getenv('JWT_ALGORITHM', 'HS256')
        self.access_token_expire_minutes = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', '30'))
        self.refresh_token_expire_days = int(os.getenv('REFRESH_TOKEN_EXPIRE_DAYS', '7'))
        
        self.db_host = os.getenv('DB_HOST', 'localhost')
        self.db_name = os.getenv('DB_NAME', 'infrahardening')
        self.db_user = os.getenv('DB_USER', 'postgres')
        self.db_password = os.getenv('DB_PASSWORD', 'password')
    
    def get_db_connection(self):
        """Get database connection"""
        conn = psycopg2.connect(
            host=self.db_host,
            database=self.db_name,
            user=self.db_user,
            password=self.db_password,
            cursor_factory=RealDictCursor
        )
        return conn
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )
    
    def create_access_token(self, data: Dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({
            'exp': expire,
            'iat': datetime.utcnow(),
            'type': 'access'
        })
        
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def create_refresh_token(self, data: Dict) -> str:
        """Create JWT refresh token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        
        to_encode.update({
            'exp': expire,
            'iat': datetime.utcnow(),
            'type': 'refresh'
        })
        
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def decode_token(self, token: str) -> Optional[Dict]:
        """Decode and validate JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            return None
        except jwt.InvalidTokenError:
            logger.warning("Invalid token")
            return None
    
    def register_user(self, email: str, password: str, name: str, 
                     customer_id: Optional[str] = None) -> Dict:
        """Register a new user"""
        try:
            conn = self.get_db_connection()
            
            with conn.cursor() as cur:
                # Check if user already exists
                cur.execute("SELECT id FROM portal_users WHERE email = %s", (email,))
                if cur.fetchone():
                    return {'success': False, 'error': 'User already exists'}
                
                # Hash password
                hashed_password = self.hash_password(password)
                
                # Create user
                if customer_id:
                    cur.execute("""
                        INSERT INTO portal_users (email, password_hash, name, customer_id, role)
                        VALUES (%s, %s, %s, %s, 'customer')
                        RETURNING id
                    """, (email, hashed_password, name, customer_id))
                else:
                    cur.execute("""
                        INSERT INTO portal_users (email, password_hash, name, role)
                        VALUES (%s, %s, %s, 'admin')
                        RETURNING id
                    """, (email, hashed_password, name))
                
                user_id = cur.fetchone()['id']
                conn.commit()
                
                logger.info(f"Registered user {user_id}")
                return {'success': True, 'user_id': user_id}
                
        except Exception as e:
            conn.rollback()
            logger.error(f"Error registering user: {e}")
            return {'success': False, 'error': str(e)}
        finally:
            conn.close()
    
    def authenticate_user(self, email: str, password: str) -> Optional[Dict]:
        """Authenticate user with email and password"""
        try:
            conn = self.get_db_connection()
            
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id, email, password_hash, name, role, customer_id, is_active
                    FROM portal_users WHERE email = %s
                """, (email,))
                user = cur.fetchone()
                
                if not user:
                    logger.warning(f"User not found: {email}")
                    return None
                
                if not user['is_active']:
                    logger.warning(f"User account disabled: {email}")
                    return None
                
                if not self.verify_password(password, user['password_hash']):
                    logger.warning(f"Invalid password for user: {email}")
                    return None
                
                # Update last login
                cur.execute("""
                    UPDATE portal_users SET last_login = CURRENT_TIMESTAMP WHERE id = %s
                """, (user['id'],))
                conn.commit()
                
                logger.info(f"User authenticated: {email}")
                return {
                    'id': user['id'],
                    'email': user['email'],
                    'name': user['name'],
                    'role': user['role'],
                    'customer_id': user['customer_id']
                }
                
        except Exception as e:
            logger.error(f"Error authenticating user: {e}")
            return None
        finally:
            conn.close()
    
    def login(self, email: str, password: str) -> Dict:
        """Login user and return tokens"""
        user = self.authenticate_user(email, password)
        
        if not user:
            return {'success': False, 'error': 'Invalid credentials'}
        
        # Create tokens
        access_token = self.create_access_token({
            'sub': user['id'],
            'email': user['email'],
            'role': user['role'],
            'customer_id': user['customer_id']
        })
        
        refresh_token = self.create_refresh_token({
            'sub': user['id'],
            'email': user['email']
        })
        
        return {
            'success': True,
            'access_token': access_token,
            'refresh_token': refresh_token,
            'token_type': 'bearer',
            'expires_in': self.access_token_expire_minutes * 60,
            'user': {
                'id': user['id'],
                'email': user['email'],
                'name': user['name'],
                'role': user['role']
            }
        }
    
    def refresh_access_token(self, refresh_token: str) -> Dict:
        """Refresh access token using refresh token"""
        payload = self.decode_token(refresh_token)
        
        if not payload or payload.get('type') != 'refresh':
            return {'success': False, 'error': 'Invalid refresh token'}
        
        # Get user info
        user_id = payload.get('sub')
        user = self.get_user_by_id(user_id)
        
        if not user:
            return {'success': False, 'error': 'User not found'}
        
        # Create new access token
        access_token = self.create_access_token({
            'sub': user['id'],
            'email': user['email'],
            'role': user['role'],
            'customer_id': user['customer_id']
        })
        
        return {
            'success': True,
            'access_token': access_token,
            'token_type': 'bearer',
            'expires_in': self.access_token_expire_minutes * 60
        }
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """Get user by ID"""
        try:
            conn = self.get_db_connection()
            
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id, email, name, role, customer_id, is_active
                    FROM portal_users WHERE id = %s
                """, (user_id,))
                user = cur.fetchone()
                
                if user:
                    return {
                        'id': user['id'],
                        'email': user['email'],
                        'name': user['name'],
                        'role': user['role'],
                        'customer_id': user['customer_id']
                    }
                
                return None
                
        except Exception as e:
            logger.error(f"Error getting user: {e}")
            return None
        finally:
            conn.close()
    
    def logout(self, token: str) -> Dict:
        """Logout user (invalidate token)"""
        # In production, add token to blacklist in Redis/database
        payload = self.decode_token(token)
        
        if payload:
            logger.info(f"User logged out: {payload.get('sub')}")
            return {'success': True}
        
        return {'success': False, 'error': 'Invalid token'}
    
    def verify_token(self, token: str) -> Optional[Dict]:
        """Verify token and return user info"""
        payload = self.decode_token(token)
        
        if payload and payload.get('type') == 'access':
            user = self.get_user_by_id(payload.get('sub'))
            
            if user and user['is_active']:
                return user
        
        return None


# Database schema for portal users (add to main schema)
PORTAL_USERS_SCHEMA = """
-- Portal Users Table
CREATE TABLE IF NOT EXISTS portal_users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'customer' CHECK (role IN ('admin', 'customer', 'support')),
    customer_id UUID REFERENCES customers(id) ON DELETE SET NULL,
    is_active BOOLEAN DEFAULT true,
    last_login TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_portal_users_email ON portal_users(email);
CREATE INDEX idx_portal_users_customer_id ON portal_users(customer_id);

-- Trigger for updated_at
CREATE TRIGGER update_portal_users_updated_at 
    BEFORE UPDATE ON portal_users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
"""


def setup_auth_schema():
    """Setup authentication schema in database"""
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            database=os.getenv('DB_NAME', 'infrahardening'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', 'password')
        )
        
        with conn.cursor() as cur:
            # Execute schema
            cur.execute(PORTAL_USERS_SCHEMA)
            conn.commit()
            
            logger.info("Authentication schema setup completed")
            
    except Exception as e:
        logger.error(f"Error setting up auth schema: {e}")
        raise
    finally:
        conn.close()


if __name__ == '__main__':
    # Setup schema
    setup_auth_schema()
    
    # Create admin user
    auth = AuthService()
    result = auth.register_user(
        email='admin@infrahardening.com',
        password='admin123',
        name='System Administrator'
    )
    print(f"Admin user creation result: {result}")
