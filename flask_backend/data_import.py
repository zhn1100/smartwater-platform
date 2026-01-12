#!/usr/bin/env python3
"""
数据导入脚本 - 将Excel数据导入SQLite数据库
"""
import pandas as pd
import sqlite3
import numpy as np
import os
from datetime import datetime

# 数据库路径
DB_PATH = os.path.join(os.path.dirname(__file__), '../backend/data/monitoring.db')

def clean_value(val):
    """清洗数据值：如果不是数字，返回0"""
    if pd.isna(val):
        return 0.0
    try:
        # 尝试转换为浮点数
        return float(val)
    except (ValueError, TypeError):
        # 如果是字符串，检查是否包含数字
        if isinstance(val, str):
            # 尝试提取数字
            import re
            numbers = re.findall(r'[-+]?\d*\.\d+|\d+', val)
            if numbers:
                return float(numbers[0])
        return 0.0

def format_datetime(dt):
    """格式化日期时间为字符串"""
    if pd.isna(dt):
        return None
    if isinstance(dt, pd.Timestamp):
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    elif isinstance(dt, datetime):
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    elif isinstance(dt, str):
        return dt
    else:
        return str(dt)

def import_water_level(conn):
    """导入水位数据"""
    print('导入水位数据...')
    df = pd.read_excel('../backend/data/水位.xlsx')
    
    # 重命名列
    df.columns = ['measure_time', 'upstream', 'downstream']
    
    cursor = conn.cursor()
    count = 0
    
    for _, row in df.iterrows():
        measure_time = format_datetime(row['measure_time'])
        if not measure_time:
            continue
        
        # 处理上游水位
        if not pd.isna(row['upstream']):
            value = clean_value(row['upstream'])
            cursor.execute('''
                INSERT INTO measurement (type_id, instrument_id, measure_time, value)
                VALUES (?, ?, ?, ?)
            ''', (3, '上游', measure_time, value))  # type_id=3 是水位
            count += 1
        
        # 处理下游水位
        if not pd.isna(row['downstream']):
            value = clean_value(row['downstream'])
            cursor.execute('''
                INSERT INTO measurement (type_id, instrument_id, measure_time, value)
                VALUES (?, ?, ?, ?)
            ''', (3, '下游', measure_time, value))
            count += 1
    
    print(f'  导入 {count} 条水位记录')
    return count

def import_tension_line(conn):
    """导入引张线数据"""
    print('导入引张线数据...')
    df = pd.read_excel('../backend/data/引张线.xlsx')
    
    # 第一列是观测时间，第二列是水位，后面是各个仪器
    time_col = df.columns[0]
    water_level_col = df.columns[1]
    instrument_cols = df.columns[2:]
    
    cursor = conn.cursor()
    count = 0
    
    for _, row in df.iterrows():
        measure_time = format_datetime(row[time_col])
        if not measure_time:
            continue
            
        water_level = clean_value(row[water_level_col]) if not pd.isna(row[water_level_col]) else None
        
        for col in instrument_cols:
            instrument_id = col
            value = clean_value(row[col])
            
            cursor.execute('''
                INSERT INTO measurement (type_id, instrument_id, measure_time, value, water_level)
                VALUES (?, ?, ?, ?, ?)
            ''', (1, instrument_id, measure_time, value, water_level))  # type_id=1 是引张线
            count += 1
    
    print(f'  导入 {count} 条引张线记录')
    return count

def import_static_level(conn):
    """导入静力水准数据"""
    print('导入静力水准数据...')
    df = pd.read_excel('../backend/data/静力水准.xlsx')
    
    # 第一列是观测时间，后面是各个仪器
    time_col = df.columns[0]
    instrument_cols = df.columns[1:]
    
    cursor = conn.cursor()
    count = 0
    
    for _, row in df.iterrows():
        measure_time = format_datetime(row[time_col])
        if not measure_time:
            continue
        
        for col in instrument_cols:
            instrument_id = col
            value = clean_value(row[col])
            
            cursor.execute('''
                INSERT INTO measurement (type_id, instrument_id, measure_time, value)
                VALUES (?, ?, ?, ?)
            ''', (2, instrument_id, measure_time, value))  # type_id=2 是静力水准
            count += 1
    
    print(f'  导入 {count} 条静力水准记录')
    return count

def import_inverted_pendulum(conn):
    """导入倒垂线数据"""
    print('导入倒垂线数据...')
    
    # 读取前两行获取仪器和通道信息
    df_header = pd.read_excel('../backend/data/倒垂线.xlsx', header=None, nrows=2)
    
    # 分析数据结构
    print('  分析倒垂线数据结构...')
    
    # 第一行：仪器编号 (IP1, nan, IP3, nan, IP5, nan, ...)
    # 第二行：通道信息 (观测时间, 左右岸CH1, 上下游CH2, 左右岸CH1, 上下游CH2, ...)
    
    # 构建仪器-通道映射
    instrument_channel_map = []
    last_instrument = None
    
    # 从第1列开始（第0列是"观测时间"）
    for col_idx in range(1, len(df_header.columns)):
        instrument = df_header.iloc[0, col_idx]
        channel = df_header.iloc[1, col_idx]
        
        # 处理仪器编号：如果为空，使用上一个非空仪器
        if pd.isna(instrument):
            instrument = last_instrument
        else:
            last_instrument = instrument
        
        # 如果没有仪器信息，跳过
        if pd.isna(instrument):
            continue
        
        # 处理通道信息
        if pd.isna(channel):
            channel = 'CH1'  # 默认值
        
        # 简化通道名称
        if '左右岸CH1' in str(channel):
            channel_suffix = 'CH1'
        elif '上下游CH2' in str(channel):
            channel_suffix = 'CH2'
        else:
            channel_suffix = str(channel)
        
        # 组合仪器ID: IP1-CH1, IP1-CH2 等
        instrument_id = f'{instrument}-{channel_suffix}'
        instrument_channel_map.append((col_idx, instrument_id))
    
    print(f'  发现 {len(instrument_channel_map)} 个仪器通道组合')
    
    # 显示映射关系
    print('  仪器通道映射:')
    for i, (col_idx, instrument_id) in enumerate(instrument_channel_map[:6]):  # 显示前6个
        print(f'    列{col_idx} -> {instrument_id}')
    if len(instrument_channel_map) > 6:
        print(f'    ... 还有 {len(instrument_channel_map)-6} 个')
    
    # 从第三行开始读取数据（跳过前两行表头，使用header=None保持数字索引）
    df_data = pd.read_excel('../backend/data/倒垂线.xlsx', header=None, skiprows=2)
    
    cursor = conn.cursor()
    count = 0
    
    for _, row in df_data.iterrows():
        measure_time = format_datetime(row[0])  # 第0列是观测时间
        if not measure_time:
            continue
        
        # 处理每个仪器通道
        for col_idx, instrument_id in instrument_channel_map:
            if col_idx >= len(row):
                continue
                
            value = clean_value(row[col_idx])
            
            # 只导入有效数据（非零值）
            if value != 0.0:
                cursor.execute('''
                    INSERT INTO measurement (type_id, instrument_id, measure_time, value)
                    VALUES (?, ?, ?, ?)
                ''', (4, instrument_id, measure_time, value))  # type_id=4 是倒垂线
                count += 1
    
    print(f'  导入 {count} 条倒垂线记录')
    
    # 显示统计信息
    cursor.execute('''
        SELECT instrument_id, COUNT(*) as cnt 
        FROM measurement 
        WHERE type_id = 4 
        GROUP BY instrument_id 
        ORDER BY instrument_id
    ''')
    samples = cursor.fetchall()
    print('  仪器统计:')
    for instrument_id, cnt in samples:
        print(f'    {instrument_id}: {cnt} 条记录')
    
    # 检查是否有CH2数据
    cursor.execute('''
        SELECT COUNT(*) as ch2_count 
        FROM measurement 
        WHERE type_id = 4 AND instrument_id LIKE '%-CH2'
    ''')
    ch2_count = cursor.fetchone()[0]
    print(f'  CH2通道数据: {ch2_count} 条记录')
    
    return count

def main():
    """主函数"""
    print('开始导入监测数据...')
    print('=' * 50)
    
    # 连接数据库
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 清空现有的测量数据
    print('清空现有数据...')
    cursor.execute('DELETE FROM measurement')
    
    # 开始导入数据
    total = 0
    total += import_water_level(conn)
    total += import_tension_line(conn)
    total += import_static_level(conn)
    total += import_inverted_pendulum(conn)
    
    # 提交更改
    conn.commit()
    
    # 统计导入的数据
    cursor.execute('SELECT type_id, COUNT(*) FROM measurement GROUP BY type_id')
    stats = cursor.fetchall()
    
    # 获取类型名称映射
    cursor.execute('SELECT id, name FROM monitoring_type')
    type_map = {id: name for id, name in cursor.fetchall()}
    
    print('=' * 50)
    print(f'导入完成！总共导入 {total} 条记录')
    print('\n按类型统计:')
    for type_id, count in stats:
        type_name = type_map.get(type_id, f'未知类型({type_id})')
        print(f'  {type_name}: {count} 条记录')
    
    # 显示一些示例数据
    print('\n示例数据（前3条）:')
    cursor.execute('''
        SELECT m.id, t.name, m.instrument_id, m.measure_time, m.value, m.water_level
        FROM measurement m
        JOIN monitoring_type t ON m.type_id = t.id
        LIMIT 3
    ''')
    for row in cursor.fetchall():
        print(f'  ID: {row[0]}, 类型: {row[1]}, 仪器: {row[2]}, 时间: {row[3]}, 值: {row[4]}, 水位: {row[5]}')
    
    conn.close()
    print('\n数据导入完成！')

if __name__ == '__main__':
    main()
