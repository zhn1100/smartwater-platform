"""
JWT工具模块
"""
import jwt
from datetime import datetime, timedelta
from .config import AuthConfig

class JWTManager:
    """JWT管理器"""
    
    @staticmethod
    def create_access_token(user_info):
        """创建访问令牌"""
        payload = {
            'user_info': user_info,
            'exp': datetime.utcnow() + AuthConfig.ACCESS_TOKEN_EXPIRES,
            'iat': datetime.utcnow(),
            'type': 'access'
        }
        return jwt.encode(
            payload, 
            AuthConfig.SECRET_KEY, 
            algorithm=AuthConfig.JWT_ALGORITHM
        )
    
    @staticmethod
    def create_refresh_token(user_info):
        """创建刷新令牌"""
        payload = {
            'user_info': user_info,
            'exp': datetime.utcnow() + AuthConfig.REFRESH_TOKEN_EXPIRES,
            'iat': datetime.utcnow(),
            'type': 'refresh'
        }
        return jwt.encode(
            payload,
            AuthConfig.SECRET_KEY,
            algorithm=AuthConfig.JWT_ALGORITHM
        )
    
    @staticmethod
    def verify_token(token):
        """验证令牌"""
        try:
            payload = jwt.decode(
                token,
                AuthConfig.SECRET_KEY,
                algorithms=[AuthConfig.JWT_ALGORITHM]
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise ValueError("令牌已过期")
        except jwt.InvalidTokenError:
            raise ValueError("无效的令牌")
    
    @staticmethod
    def refresh_access_token(refresh_token):
        """使用刷新令牌获取新的访问令牌"""
        try:
            payload = JWTManager.verify_token(refresh_token)
            if payload.get('type') != 'refresh':
                raise ValueError("无效的刷新令牌类型")
            
            # 创建新的访问令牌
            user_info = payload['user_info']
            new_access_token = JWTManager.create_access_token(user_info)
            
            return new_access_token
        except Exception as e:
            raise ValueError(f"刷新令牌失败: {str(e)}")
    
    @staticmethod
    def create_tokens(user_info):
        """创建访问令牌和刷新令牌对"""
        access_token = JWTManager.create_access_token(user_info)
        refresh_token = JWTManager.create_refresh_token(user_info)
        
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'token_type': 'Bearer',
            'expires_in': int(AuthConfig.ACCESS_TOKEN_EXPIRES.total_seconds()),
            'user_info': user_info
        }
