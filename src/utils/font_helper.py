# utils/font_helper.py - 创建新的字体辅助类

import pygame

class FontHelper:
    """兼容性字体辅助类，处理 FontManager 和 pygame.font.Font 对象"""
    
    @staticmethod
    def get_font(font_manager, size_name='medium'):
        """安全地获取字体对象"""
        if hasattr(font_manager, size_name):
            # font_manager 是 FontManager 实例
            font = getattr(font_manager, size_name)
            if font is None and hasattr(font_manager, 'ensure_initialized'):
                font_manager.ensure_initialized()
                font = getattr(font_manager, size_name)
            return font
        elif isinstance(font_manager, pygame.font.Font):
            # font_manager 是 pygame.font.Font 实例
            return font_manager
        else:
            # 回退到系统字体
            size_map = {'small': 20, 'medium': 24, 'large': 32}
            return pygame.font.SysFont(None, size_map.get(size_name, 24))
    
    @staticmethod
    def ensure_initialized(font_manager):
        """确保字体管理器已初始化"""
        if hasattr(font_manager, 'ensure_initialized'):
            font_manager.ensure_initialized()
        elif hasattr(font_manager, 'initialize_fonts'):
            if not hasattr(font_manager, 'small') or font_manager.small is None:
                font_manager.initialize_fonts()
        # 如果是 pygame.font.Font 对象，不需要初始化