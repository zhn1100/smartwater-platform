<template>
  <div style="height:100%; display:flex; flex-direction:column; gap:10px;">
    <div style="display:flex; gap:10px; align-items:center; flex-wrap:wrap;">
      <div style="font-weight:700; color:var(--brand-blue-2);">监测资料（全部Sheet读取）</div>
      <el-select v-model="sheet" placeholder="选择Sheet" style="width:180px" @change="load">
        <el-option v-for="s in sheets" :key="s" :label="s" :value="s" />
      </el-select>
      <el-button @click="load">刷新</el-button>
      <el-button type="primary" plain @click="onExport">导出Excel</el-button>
      <div style="font-size:12px; color:#64748b;">提示：默认每页 200 行，可分页浏览；双击单元格可修改。</div>
    </div>

    <div class="card" style="flex:1; overflow:hidden;">
      <el-table
        v-loading="loading"
        :data="tableRows"
        size="small"
        height="100%"
        style="width:100%"
        @cell-dblclick="onCellDblClick"
      >
        <el-table-column
          v-for="(col, idx) in columns"
          :key="idx"
          :label="col"
          :min-width="140"
        >
          <template #default="scope">
            <span>{{ scope.row[idx] }}</span>
          </template>
        </el-table-column>
      </el-table>
    </div>

    <div style="display:flex; justify-content:space-between; align-items:center;">
      <div style="font-size:12px; color:#475569;">Sheet：{{ sheet }} | 总行数：{{ totalRows }} | 总列数：{{ totalCols }}</div>
      <el-pagination
        background
        layout="prev, pager, next, jumper"
        :page-size="pageSize"
        :total="totalRows"
        :current-page="page+1"
        @current-change="(p)=>{page=p-1; load()}"
      />
    </div>

    <el-dialog v-model="editVisible" title="修改单元格" width="520">
      <div style="font-size:12px; color:#64748b; margin-bottom:8px;">
        Sheet: <b>{{ sheet }}</b> | 行: <b>{{ editRow }}</b> | 列: <b>{{ editCol }}</b>（下标从 0 开始）
      </div>
      <el-input v-model="editValue" placeholder="请输入新的内容" />
      <template #footer>
        <el-button @click="editVisible=false">取消</el-button>
        <el-button type="primary" @click="saveCell">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { listSheets, getSheet, updateCell, exportExcel } from '../api/excel'

const sheets = ref([])
const sheet = ref('')

const loading = ref(false)
const columns = ref([])
const tableRows = ref([])
const totalRows = ref(0)
const totalCols = ref(0)

const page = ref(0)
const pageSize = 200

const editVisible = ref(false)
const editRow = ref(0)
const editCol = ref(0)
const editValue = ref('')

async function loadSheets() {
  sheets.value = await listSheets()
  if (!sheet.value && sheets.value.length) sheet.value = sheets.value[0]
}

async function load() {
  if (!sheet.value) return
  loading.value = true
  try {
    const res = await getSheet(sheet.value, page.value, pageSize)
    columns.value = res.columns
    tableRows.value = res.rows
    totalRows.value = res.totalRows
    totalCols.value = res.totalCols
  } finally {
    loading.value = false
  }
}

function onCellDblClick(row, column, cell, event) {
  // element-plus 传来的 row 是数组（我们构造的 tableRows）
  // 这里用列标题在 columns 数组中的位置作为 colIndex（足够满足课设展示/编辑需求）
  const idx = columns.value.indexOf(column.label)
  if (idx < 0) return

  const rowIndexInPage = tableRows.value.indexOf(row)
  if (rowIndexInPage < 0) return

  editRow.value = page.value * pageSize + rowIndexInPage
  editCol.value = idx
  editValue.value = row[idx]
  editVisible.value = true
}

async function saveCell() {
  await updateCell({
    sheetName: sheet.value,
    rowIndex: editRow.value,
    colIndex: editCol.value,
    value: editValue.value
  })
  ElMessage.success('已保存（已写回后端工作簿）')
  editVisible.value = false
  await load()
}

function onExport() {
  exportExcel()
}

onMounted(async () => {
  await loadSheets()
  await load()
})
</script>
