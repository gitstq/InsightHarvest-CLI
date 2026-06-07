"""数据缓存模块 - 本地文件缓存系统"""

import os
import json
import time
import hashlib
import sys


class Cache:
    """基于文件系统的本地缓存，支持TTL过期"""

    _instance = None

    def __new__(cls, cache_dir=None, ttl=3600):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, cache_dir=None, ttl=3600):
        if self._initialized:
            return
        self._initialized = True

        self.cache_dir = cache_dir or os.path.join(
            os.path.expanduser("~"),
            ".insight_harvest",
            "cache"
        )
        self.ttl = ttl  # 默认TTL: 1小时

        # 确保缓存目录存在
        if not os.path.exists(self.cache_dir):
            try:
                os.makedirs(self.cache_dir, exist_ok=True)
            except OSError as e:
                sys.stderr.write("警告: 无法创建缓存目录: {}\n".format(str(e)))

    def _make_key(self, source, identifier):
        """生成缓存键的文件名"""
        raw = "{}:{}".format(source, identifier)
        key_hash = hashlib.md5(raw.encode("utf-8")).hexdigest()
        return key_hash

    def _get_path(self, key):
        """获取缓存文件路径"""
        return os.path.join(self.cache_dir, key + ".json")

    def get(self, source, identifier):
        """读取缓存，返回数据或None"""
        key = self._make_key(source, identifier)
        path = self._get_path(key)

        if not os.path.exists(path):
            return None

        try:
            with open(path, "r", encoding="utf-8") as f:
                entry = json.load(f)

            # 检查是否过期
            if time.time() - entry.get("timestamp", 0) > self.ttl:
                self.delete(source, identifier)
                return None

            return entry.get("data")
        except (json.JSONDecodeError, IOError, KeyError):
            return None

    def set(self, source, identifier, data):
        """写入缓存"""
        key = self._make_key(source, identifier)
        path = self._get_path(key)

        entry = {
            "source": source,
            "identifier": identifier,
            "timestamp": time.time(),
            "data": data,
        }

        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(entry, f, ensure_ascii=False, default=str)
        except (IOError, OSError) as e:
            sys.stderr.write("警告: 无法写入缓存: {}\n".format(str(e)))

    def delete(self, source, identifier):
        """删除缓存条目"""
        key = self._make_key(source, identifier)
        path = self._get_path(key)
        if os.path.exists(path):
            try:
                os.remove(path)
            except OSError:
                pass

    def clear(self):
        """清空所有缓存"""
        if not os.path.exists(self.cache_dir):
            return
        for filename in os.listdir(self.cache_dir):
            if filename.endswith(".json"):
                try:
                    os.remove(os.path.join(self.cache_dir, filename))
                except OSError:
                    pass

    def cleanup_expired(self):
        """清理所有过期缓存"""
        if not os.path.exists(self.cache_dir):
            return
        count = 0
        for filename in os.listdir(self.cache_dir):
            if not filename.endswith(".json"):
                continue
            path = os.path.join(self.cache_dir, filename)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    entry = json.load(f)
                if time.time() - entry.get("timestamp", 0) > self.ttl:
                    os.remove(path)
                    count += 1
            except (json.JSONDecodeError, IOError, KeyError, OSError):
                continue
        return count

    def stats(self):
        """返回缓存统计信息"""
        total = 0
        expired = 0
        size = 0
        if not os.path.exists(self.cache_dir):
            return {"total": 0, "expired": 0, "size_bytes": 0}

        for filename in os.listdir(self.cache_dir):
            if not filename.endswith(".json"):
                continue
            path = os.path.join(self.cache_dir, filename)
            total += 1
            size += os.path.getsize(path)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    entry = json.load(f)
                if time.time() - entry.get("timestamp", 0) > self.ttl:
                    expired += 1
            except (json.JSONDecodeError, IOError, KeyError):
                expired += 1

        return {
            "total": total,
            "expired": expired,
            "size_bytes": size,
        }

    def __repr__(self):
        return "Cache(dir={!r}, ttl={})".format(self.cache_dir, self.ttl)
