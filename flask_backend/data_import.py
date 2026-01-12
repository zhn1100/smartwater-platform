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
    
    # 读取所有数据
    df_all = pd.read_excel('../backend/data/倒垂线.xlsx', header=None)
    
    # 分析数据结构
    print('  分析倒垂线数据结构...')
    
    # 第一行是仪器信息，第二行开始是数据
    # 获取仪器ID
    instrument_ids = []
    for i in range(1, len(df_all.columns)):
        instrument_id = df_all.iloc[0, i]
        if pd.isna(instrument_id):
            instrument_id = f'IP_{i}'
        instrument_ids.append(str(instrument_id))
    
    # 从第二行开始读取数据
    df = pd.read_excel('../backend/data/倒垂线.xlsx', skiprows=1)
    
    # 重命名列
    new_columns = ['measure_time'] + instrument_ids[:len(df.columns)-1]
    df.columns = new_columns[:len(df.columns)]
    
    cursor = conn.cursor()
    count = 0
    
    for _, row in df.iterrows():
        measure_time = format_datetime(row['measure_time'])
        if not measure_time:
            continue
        
        for i, instrument_id in enumerate(instrument_ids):
            if i >= len(df.columns) - 1:
                break
            col_name = instrument_ids[i]
            value = clean_value(row[col_name]) if col_name in row else 0.0
            
            cursor.execute('''
                INSERT INTO measurement (type_id, instrument_id, measure_time, value)
                VALUES (?, ?, ?, ?)
            ''', (4, instrument_id, measure_time, value))  # type_id=4 是倒垂线
            count += 1
    
    print(f'  导入 {count} 条倒垂线记录')
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
