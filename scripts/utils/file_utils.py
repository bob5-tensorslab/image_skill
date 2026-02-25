#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件解析工具模块
提供通用的文件名解析功能
"""

import os
import re
import logging
from datetime import datetime
logger = logging.getLogger(__name__)


def parse_result_filename(filename, prompts_data, face_names):
    """
    解析结果文件名，提取prompt_key和face_name
    
    Args:
        filename: 文件名，如 "001_contemplative_brunette_male_bald2.png"
        prompts_data: prompt数据字典，用于验证prompt_key
        face_names: 脸图文件名列表，按长度逆序排序
    
    Returns:
        dict: 包含解析结果的字典，如果解析失败返回None
        {
            'filename': str,      # 原文件名
            'seq_num': int,       # 序号
            'prompt_key': str,    # prompt键
            'face_name': str      # 脸图名称
        }
    """
    # 尝试标准格式: {序号:03d}_{prompt_key}_{face_name}.{ext}
    match = re.match(r'^(\d{3})_(.+)\.(jpg|png|jpeg|webp)$', filename)
    if match:
        seq_num, remaining, _ = match.groups()
        
        # 通过脸图文件名包含匹配来定位
        face_name = None
        prompt_key = None
        
        # 按长度逆序尝试匹配脸图名
        for candidate_face_name in face_names:
            if candidate_face_name in remaining:
                # 找到脸图名在文件名中的位置
                face_name_pos = remaining.find(candidate_face_name)
                if face_name_pos > 0:  # 确保脸图名前面有内容（prompt_key）
                    face_name = candidate_face_name
                    # 提取prompt_key（脸图名前面的部分，去掉末尾的下划线）
                    prompt_key = remaining[:face_name_pos].strip('_')
                    if prompt_key in prompts_data:
                        break
        
        if face_name and prompt_key:
            return {
                'filename': filename,
                'seq_num': int(seq_num),
                'prompt_key': prompt_key,
                'face_name': face_name
            }
        else:
            logger.warning(f"无法解析文件名: {filename}, remaining: {remaining}")
            return None
    else:
        logger.warning(f"无法匹配文件名格式: {filename}")
        return None


def parse_result_filenames(filenames, prompts_data, face_names):
    """
    批量解析结果文件名
    
    Args:
        filenames: 文件名列表
        prompts_data: prompt数据字典
        face_names: 脸图文件名列表，按长度逆序排序
    
    Returns:
        list: 解析成功的文件信息列表，按序号排序
    """
    parsed_files = []
    
    for filename in filenames:
        result = parse_result_filename(filename, prompts_data, face_names)
        if result:
            parsed_files.append(result)
    
    # 按序号排序
    parsed_files.sort(key=lambda x: x['seq_num'])
    
    return parsed_files


def get_face_name_to_path_mapping(face_dir):
    """
    获取脸图文件名到完整路径的映射，按长度逆序排序
    
    Args:
        face_dir: 脸图目录路径
    
    Returns:
        tuple: (face_name_to_path_dict, face_names_list)
    """
    if not os.path.exists(face_dir):
        logger.error(f"脸图目录不存在: {face_dir}")
        return {}, []
    
    face_files = os.listdir(face_dir)
    face_files = [os.path.join(face_dir, file) for file in face_files 
                  if file.lower().endswith((".png", ".jpg", ".jpeg", ".webp"))]
    
    # 创建脸图文件名到完整路径的映射，按长度逆序排序
    face_name_to_path = {}
    face_names = []
    for face_file in face_files:
        face_name = os.path.splitext(os.path.basename(face_file))[0]
        face_name_to_path[face_name] = face_file
        face_names.append(face_name)
    
    # 按长度逆序排序，优先匹配最长的脸图名
    face_names.sort(key=len, reverse=True)
    
    logger.info(f"找到{len(face_names)}张脸图，按长度逆序排序")
    
    return face_name_to_path, face_names


def get_result_files(result_dir, supported_extensions=('.jpg', '.png', '.jpeg', '.webp')):
    """
    获取结果目录中的图片文件列表
    
    Args:
        result_dir: 结果目录路径
        supported_extensions: 支持的图片扩展名
    
    Returns:
        list: 图片文件名列表
    """
    if not os.path.exists(result_dir):
        logger.error(f"结果目录不存在: {result_dir}")
        return []
    
    files = [f for f in os.listdir(result_dir) 
             if f.lower().endswith(supported_extensions)]
    
    logger.info(f"找到{len(files)}个图片文件")
    return files


def infer_prompt_and_face_dir(result_dir_name):
    """
    根据结果目录名推断prompt文件和脸图目录
    
    Args:
        result_dir_name: 结果目录名称
    
    Returns:
        tuple: (prompt_file_path, face_dir) 或 (None, None)
    """
    if "single_female" in result_dir_name:
        return "prompts/single_female.yml", "source_faces/face_female"
    elif "single_male" in result_dir_name:
        return "prompts/single_male.yml", "source_faces/face_male"
    else:
        logger.error(f"无法从目录名推断prompt文件和脸图目录: {result_dir_name}")
        return None, None


def make_save_dir(prompt_file_path, result_base_dir, seed):
    prompt_name = os.path.basename(prompt_file_path).split(".")[0]
    current_date = datetime.now().strftime("%Y%m%d_%H%M%S")
    save_dir = os.path.join(result_base_dir, f"{prompt_name}__{current_date}__{seed}")
    os.makedirs(save_dir, exist_ok=True)
    return save_dir