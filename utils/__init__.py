"""
工具函数模块
"""
import os
import json
import hashlib
import random
import string
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from pathlib import Path
import logging
import base64
import re

logger = logging.getLogger(__name__)

def generate_session_id(length: int = 16) -> str:
    """
    生成随机会话ID
    
    Args:
        length: ID长度
    
    Returns:
        会话ID字符串
    """
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def generate_user_id(prefix: str = "user") -> str:
    """
    生成用户ID
    
    Args:
        prefix: ID前缀
    
    Returns:
        用户ID字符串
    """
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    random_str = ''.join(random.choices(string.digits, k=6))
    return f"{prefix}_{timestamp}_{random_str}"

def safe_json_loads(json_str: str) -> Any:
    """
    安全地解析JSON字符串
    
    Args:
        json_str: JSON字符串
    
    Returns:
        解析后的对象，解析失败返回None
    """
    try:
        return json.loads(json_str)
    except (json.JSONDecodeError, TypeError):
        return None

def safe_json_dumps(data: Any, ensure_ascii: bool = False) -> str:
    """
    安全地将对象转换为JSON字符串
    
    Args:
        data: 要转换的数据
        ensure_ascii: 是否确保ASCII编码
    
    Returns:
        JSON字符串，转换失败返回空字符串
    """
    try:
        return json.dumps(data, ensure_ascii=ensure_ascii, default=str)
    except (TypeError, ValueError):
        return ""

def validate_email(email: str) -> bool:
    """
    验证邮箱格式
    
    Args:
        email: 邮箱地址
    
    Returns:
        是否有效
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone: str) -> bool:
    """
    验证手机号格式（中国）
    
    Args:
        phone: 手机号
    
    Returns:
        是否有效
    """
    pattern = r'^1[3-9]\d{9}$'
    return re.match(pattern, phone) is not None

def format_datetime(dt: datetime, fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    格式化日期时间
    
    Args:
        dt: 日期时间对象
        fmt: 格式字符串
    
    Returns:
        格式化后的字符串
    """
    return dt.strftime(fmt)

def parse_datetime(dt_str: str, fmt: str = "%Y-%m-%d %H:%M:%S") -> Optional[datetime]:
    """
    解析日期时间字符串
    
    Args:
        dt_str: 日期时间字符串
        fmt: 格式字符串
    
    Returns:
        日期时间对象，解析失败返回None
    """
    try:
        return datetime.strptime(dt_str, fmt)
    except (ValueError, TypeError):
        return None

def calculate_time_diff(start: datetime, end: datetime) -> Dict[str, int]:
    """
    计算时间差
    
    Args:
        start: 开始时间
        end: 结束时间
    
    Returns:
        包含天数、小时、分钟、秒的字典
    """
    diff = end - start
    
    days = diff.days
    seconds = diff.seconds
    
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    
    return {
        "days": days,
        "hours": hours,
        "minutes": minutes,
        "seconds": seconds,
        "total_seconds": int(diff.total_seconds())
    }

def mask_sensitive_data(data: str, keep_start: int = 3, keep_end: int = 4) -> str:
    """
    脱敏敏感数据
    
    Args:
        data: 原始数据
        keep_start: 保留开头的字符数
        keep_end: 保留结尾的字符数
    
    Returns:
        脱敏后的数据
    """
    if not data or len(data) <= keep_start + keep_end:
        return "*" * len(data)
    
    return data[:keep_start] + "*" * (len(data) - keep_start - keep_end) + data[-keep_end:]

def format_file_size(size_bytes: int) -> str:
    """
    格式化文件大小
    
    Args:
        size_bytes: 文件大小（字节）
    
    Returns:
        格式化后的字符串
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"

def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    截断文本
    
    Args:
        text: 原始文本
        max_length: 最大长度
        suffix: 后缀字符串
    
    Returns:
        截断后的文本
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix

def extract_urls(text: str) -> List[str]:
    """
    提取文本中的URL
    
    Args:
        text: 原始文本
    
    Returns:
        URL列表
    """
    pattern = r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+(?:[/?#][^\s]*)?'
    return re.findall(pattern, text)

def extract_hashtags(text: str) -> List[str]:
    """
    提取文本中的话题标签
    
    Args:
        text: 原始文本
    
    Returns:
        话题标签列表
    """
    pattern = r'#(\w+)'
    return re.findall(pattern, text)

def calculate_md5(data: Union[str, bytes]) -> str:
    """
    计算MD5哈希
    
    Args:
        data: 字符串或字节数据
    
    Returns:
        MD5哈希值
    """
    if isinstance(data, str):
        data = data.encode('utf-8')
    
    return hashlib.md5(data).hexdigest()

def calculate_sha256(data: Union[str, bytes]) -> str:
    """
    计算SHA256哈希
    
    Args:
        data: 字符串或字节数据
    
    Returns:
        SHA256哈希值
    """
    if isinstance(data, str):
        data = data.encode('utf-8')
    
    return hashlib.sha256(data).hexdigest()

def base64_encode(data: Union[str, bytes]) -> str:
    """
    Base64编码
    
    Args:
        data: 字符串或字节数据
    
    Returns:
        Base64编码字符串
    """
    if isinstance(data, str):
        data = data.encode('utf-8')
    
    return base64.b64encode(data).decode('utf-8')

def base64_decode(data: str) -> bytes:
    """
    Base64解码
    
    Args:
        data: Base64编码字符串
    
    Returns:
        解码后的字节数据
    """
    return base64.b64decode(data)

def retry_on_exception(func, max_attempts: int = 3, delay: float = 1.0, 
                      exceptions: tuple = (Exception,)):
    """
    异常重试装饰器
    
    Args:
        func: 要装饰的函数
        max_attempts: 最大尝试次数
        delay: 重试延迟（秒）
        exceptions: 要捕获的异常类型
    
    Returns:
        装饰后的函数
    """
    import time
    
    def wrapper(*args, **kwargs):
        last_exception = None
        
        for attempt in range(max_attempts):
            try:
                return func(*args, **kwargs)
            except exceptions as e:
                last_exception = e
                logger.warning(f"函数 {func.__name__} 第 {attempt + 1} 次尝试失败: {e}")
                
                if attempt < max_attempts - 1:
                    time.sleep(delay * (2 ** attempt))  # 指数退避
        
        raise last_exception
    
    return wrapper

def time_it(func):
    """
    计时装饰器
    
    Args:
        func: 要装饰的函数
    
    Returns:
        装饰后的函数
    """
    import time
    
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        logger.info(f"函数 {func.__name__} 执行时间: {end_time - start_time:.3f} 秒")
        return result
    
    return wrapper

def chunk_list(lst: List, chunk_size: int) -> List[List]:
    """
    将列表分块
    
    Args:
        lst: 原始列表
        chunk_size: 每块大小
    
    Returns:
        分块后的列表
    """
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

def flatten_list(nested_list: List) -> List:
    """
    展平嵌套列表
    
    Args:
        nested_list: 嵌套列表
    
    Returns:
        展平后的列表
    """
    result = []
    for item in nested_list:
        if isinstance(item, list):
            result.extend(flatten_list(item))
        else:
            result.append(item)
    return result

def merge_dicts(dict1: Dict, dict2: Dict) -> Dict:
    """
    深度合并两个字典
    
    Args:
        dict1: 第一个字典
        dict2: 第二个字典
    
    Returns:
        合并后的字典
    """
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dicts(result[key], value)
        else:
            result[key] = value
    
    return result

def get_env_variable(key: str, default: Any = None) -> Any:
    """
    获取环境变量
    
    Args:
        key: 环境变量键
        default: 默认值
    
    Returns:
        环境变量值
    """
    return os.environ.get(key, default)

def ensure_directory(path: Union[str, Path]) -> bool:
    """
    确保目录存在
    
    Args:
        path: 目录路径
    
    Returns:
        是否成功
    """
    try:
        Path(path).mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"创建目录失败 {path}: {e}")
        return False

def cleanup_old_files(directory: Union[str, Path], pattern: str = "*", 
                     max_age_days: int = 7) -> int:
    """
    清理旧文件
    
    Args:
        directory: 目录路径
        pattern: 文件模式
        max_age_days: 最大保存天数
    
    Returns:
        删除的文件数量
    """
    try:
        dir_path = Path(directory)
        if not dir_path.exists() or not dir_path.is_dir():
            return 0
        
        cutoff_time = datetime.now() - timedelta(days=max_age_days)
        deleted_count = 0
        
        for file_path in dir_path.glob(pattern):
            if file_path.is_file():
                file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                if file_mtime < cutoff_time:
                    try:
                        file_path.unlink()
                        deleted_count += 1
                        logger.debug(f"已删除旧文件: {file_path}")
                    except Exception as e:
                        logger.error(f"删除文件失败 {file_path}: {e}")
        
        logger.info(f"清理完成: 删除了 {deleted_count} 个文件")
        return deleted_count
        
    except Exception as e:
        logger.error(f"清理文件失败: {e}")
        return 0