/**
 * dam3.glb模型分块到测点仪器的映射配置
 * 这个映射将模型分块的名字映射到数据库中的仪器ID
 * 
 * 注意：实际的分块名字需要从GLB模型中提取
 * 这里提供的是示例映射，需要根据实际情况调整
 */

export const dam3ModelMapping = {
  // 根据实际模型分块名字映射到仪器ID
  // 这些是示例映射，需要根据实际模型分块名字调整
  
  // 倒垂线监测点映射 (IP系列)
  'IP1监测点': 'IP1',
  'IP1_CH1监测点': 'IP1-CH1',
  'IP1_CH2监测点': 'IP1-CH2',
  'IP2监测点': 'IP2',
  'IP2_CH1监测点': 'IP2-CH1',
  'IP2_CH2监测点': 'IP2-CH2',
  'IP3监测点': 'IP3',
  'IP3_CH1监测点': 'IP3-CH1',
  'IP3_CH2监测点': 'IP3-CH2',
  'IP4监测点': 'IP4',
  'IP4_CH1监测点': 'IP4-CH1',
  'IP4_CH2监测点': 'IP4-CH2',
  'IP5监测点': 'IP5',
  'IP5_CH1监测点': 'IP5-CH1',
  'IP5_CH2监测点': 'IP5-CH2',
  'IP6监测点': 'IP6',
  'IP6_CH1监测点': 'IP6-CH1',
  'IP6_CH2监测点': 'IP6-CH2',
  'IP7_CH1监测点': 'IP7-CH1',
  'IP7_CH2监测点': 'IP7-CH2',
  'IP8_CH1监测点': 'IP8-CH1',
  'IP8_CH2监测点': 'IP8-CH2',
  'IP9_CH1监测点': 'IP9-CH1',
  'IP9_CH2监测点': 'IP9-CH2',
  
  // 引张线监测点映射 (EX系列)
  'EX1-2监测点': 'EX1-2',
  'EX1-3监测点': 'EX1-3',
  'EX1-4监测点': 'EX1-4',
  'EX1-5监测点': 'EX1-5',
  'EX1-6监测点': 'EX1-6',
  'EX1-7监测点': 'EX1-7',
  'EX1-8监测点': 'EX1-8',
  'EX1-9监测点': 'EX1-9',
  'EX1-10监测点': 'EX1-10',
  'EX1-11监测点': 'EX1-11',
  
  'EX2-2监测点': 'EX2-2',
  'EX2-3监测点': 'EX2-3',
  'EX2-4监测点': 'EX2-4',
  'EX2-5监测点': 'EX2-5',
  'EX2-6监测点': 'EX2-6',
  'EX2-7监测点': 'EX2-7',
  
  'EX3-2监测点': 'EX3-2',
  'EX3-3监测点': 'EX3-3',
  'EX3-4监测点': 'EX3-4',
  'EX3-4′监测点': 'EX3-4′',
  
  // 静力水准监测点映射 (TC系列)
  'TC1-1监测点': 'TC1-1',
  'TC1-2监测点': 'TC1-2',
  'TC1-3监测点': 'TC1-3',
  'TC1-4监测点': 'TC1-4',
  'TC1-5监测点': 'TC1-5',
  'TC1-6监测点': 'TC1-6',
  'TC1-6′监测点': 'TC1-6′',
  'TC1-7监测点': 'TC1-7',
  'TC1-8监测点': 'TC1-8',
  'TC1-9监测点': 'TC1-9',
  'TC1-10监测点': 'TC1-10',
  'TC1-11监测点': 'TC1-11',
  'TC1-12监测点': 'TC1-12',
  
  'TC3-1监测点': 'TC3-1',
  'TC3-2监测点': 'TC3-2',
  'TC3-3监测点': 'TC3-3',
  'TC3-4监测点': 'TC3-4',
  'TC3-5监测点': 'TC3-5',
  
  // 水位监测点
  '上游水位监测点': '上游',
  '下游水位监测点': '下游',
  
  // 实际模型分块名字映射（根据控制台输出）
  '组合窗 - 三层单列(固定 上悬) 单扇窗 [330274]': 'IP1-CH1',
  '挡水坝段4-4 挡水坝段4-4 [214417]': 'EX1-2',
  '基本墙 常规 - 200mm [328370]': 'TC1-1',
  'DL DL6 [316956]': 'IP2-CH1',
  'P Pxdb5-7 [310149]': 'EX2-2',
  
  // 默认映射（用于测试）
  'Test_Block_1': 'IP1-CH1',
  'Test_Block_2': 'EX1-2',
  'Test_Block_3': 'TC1-1'
};

/**
 * 根据模型分块名字获取对应的仪器ID
 * @param {string} blockName - 模型分块的名字
 * @returns {string|null} 对应的仪器ID，如果没有找到则返回null
 */
export function getInstrumentIdFromBlockName(blockName) {
  // 直接匹配
  if (dam3ModelMapping[blockName]) {
    return dam3ModelMapping[blockName];
  }
  
  // 尝试模糊匹配（不区分大小写，忽略空格和下划线）
  const normalizedBlockName = blockName.toLowerCase().replace(/[_\s]/g, '');
  
  for (const [key, value] of Object.entries(dam3ModelMapping)) {
    const normalizedKey = key.toLowerCase().replace(/[_\s]/g, '');
    if (normalizedKey.includes(normalizedBlockName) || normalizedBlockName.includes(normalizedKey)) {
      return value;
    }
  }
  
  // 尝试匹配仪器ID模式
  const instrumentPatterns = [
    /IP\d+/i,
    /EX\d+-\d+/i,
    /TC\d+-\d+/i,
    /上游/i,
    /下游/i
  ];
  
  for (const pattern of instrumentPatterns) {
    const match = blockName.match(pattern);
    if (match) {
      // 尝试找到最接近的匹配
      const foundId = Object.values(dam3ModelMapping).find(id => 
        id.toLowerCase().includes(match[0].toLowerCase())
      );
      if (foundId) {
        return foundId;
      }
    }
  }
  
  return null;
}

/**
 * 获取所有可用的仪器ID列表
 * @returns {string[]} 仪器ID数组
 */
export function getAllInstrumentIds() {
  return Array.from(new Set(Object.values(dam3ModelMapping)));
}

/**
 * 根据仪器ID获取对应的模型分块名字
 * @param {string} instrumentId - 仪器ID
 * @returns {string[]} 对应的模型分块名字数组（可能有多个分块对应同一个仪器）
 */
export function getBlockNamesFromInstrumentId(instrumentId) {
  return Object.entries(dam3ModelMapping)
    .filter(([_, id]) => id === instrumentId)
    .map(([blockName]) => blockName);
}

export default {
  dam3ModelMapping,
  getInstrumentIdFromBlockName,
  getAllInstrumentIds,
  getBlockNamesFromInstrumentId
};
