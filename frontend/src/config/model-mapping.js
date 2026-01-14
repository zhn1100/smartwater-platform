/**
 * dam3.glb模型分块到测点仪器的映射配置
 * 这个映射将模型分块的名字映射到数据库中的仪器ID
 * 
 * 注意：实际的分块名字需要从GLB模型中提取
 * 这里提供的是示例映射，需要根据实际情况调整
 */

export const dam3ModelMapping = {
  // 根据测点映射.txt文件的实际映射关系
  
  // EX系列映射（根据测点映射.txt）
  // 只有EX EX1 [239587]是特殊的，对应IP1（因为这个点有两个仪器）
  'EX EX1 [239587]': 'IP1',
  // 其他的EX EX2到EX EX10对应EX1-2到EX1-10
  'EX EX2 [239614]': 'EX1-2',
  'EX EX3 [239599]': 'EX1-3',
  'EX EX4 [239611]': 'EX1-4',
  'EX EX5 [239608]': 'EX1-5',
  'EX EX6 [239590]': 'EX1-6',
  'EX EX7 [239593]': 'EX1-7',
  'EX EX8 [239602]': 'EX1-8',
  'EX EX9 [239596]': 'EX1-9',
  'EX EX10 [239584]': 'EX1-10',
  
  // IP系列映射（根据测点映射.txt）
  'IP IP1 [257492]': 'IP1',
  'IP IP2 [253389]': 'IP2',
  'IP IP3 [257472]': 'IP3',
  
  // PL2 IP6(倒锤线) 映射
  'PL2 IP6(倒锤线) [268515]': 'IP6-CH1',
  
  // 反向映射支持（从仪器ID到模型分块）
  // 这些是反向映射，用于从列表点击时找到对应的模型分块
  'IP6': 'PL2 IP6(倒锤线) [268515]',
  'IP6-CH1': 'PL2 IP6(倒锤线) [268515]',
  'IP6-CH2': 'PL2 IP6(倒锤线) [268515]',
  
  // 其他可能的映射（根据之前的配置保留）
  'IP1监测点': 'IP1',
  'IP1_CH1监测点': 'IP1-CH1',
  'IP1_CH2监测点': 'IP1-CH2',
  'IP2监测点': 'IP2',
  'IP2_CH1监测点': 'IP2-CH1',
  'IP2_CH2监测点': 'IP2-CH2',
  'IP3监测点': 'IP3',
  'IP3_CH1监测点': 'IP3-CH1',
  'IP3_CH2监测点': 'IP3-CH2',
  
  // EX系列其他映射
  'EX1-2监测点': 'EX1-2',
  'EX1-3监测点': 'EX1-3',
  'EX1-4监测点': 'EX1-4',
  'EX1-5监测点': 'EX1-5',
  'EX1-6监测点': 'EX1-6',
  'EX1-7监测点': 'EX1-7',
  'EX1-8监测点': 'EX1-8',
  'EX1-9监测点': 'EX1-9',
  'EX1-10监测点': 'EX1-10',
  
  // 水位监测点
  '上游水位监测点': '上游',
  '下游水位监测点': '下游',
  
  // 实际模型分块名字映射（根据控制台输出）
  '组合窗 - 三层单列(固定 上悬) 单扇窗 [330274]': 'IP1-CH1',
  '挡水坝段4-4 挡水坝段4-4 [214417]': 'EX1-2',
  '基本墙 常规 - 200mm [328370]': 'TC1-1',
  'DL DL6 [316956]': 'IP2-CH1',
  'P Pxdb5-7 [310149]': 'EX2-2',
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
  const blockNames = [];
  
  // 直接匹配
  for (const [blockName, id] of Object.entries(dam3ModelMapping)) {
    if (id === instrumentId) {
      blockNames.push(blockName);
    }
  }
  
  // 如果直接匹配没有找到，尝试模糊匹配
  if (blockNames.length === 0) {
    const normalizedInstrumentId = instrumentId.toLowerCase().replace(/[-\s]/g, '');
    
    for (const [blockName, id] of Object.entries(dam3ModelMapping)) {
      const normalizedId = id.toLowerCase().replace(/[-\s]/g, '');
      
      // 检查是否包含前三个字母（如IP6匹配IP6-CH1）
      if (normalizedId.includes(normalizedInstrumentId.substring(0, 3)) || 
          normalizedInstrumentId.includes(normalizedId.substring(0, 3))) {
        blockNames.push(blockName);
      }
    }
  }
  
  // 去重并返回
  return [...new Set(blockNames)];
}

export default {
  dam3ModelMapping,
  getInstrumentIdFromBlockName,
  getAllInstrumentIds,
  getBlockNamesFromInstrumentId
};
