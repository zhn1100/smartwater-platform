<template>
  <div style="height:100%; display:flex; gap:12px;">
    <div class="card" style="flex: 6; min-width: 520px; position:relative; overflow:hidden;">
      <div ref="viewerEl" style="height:100%;"></div>
      <div style="position:absolute; left:12px; top:12px; background:rgba(255,255,255,0.92); padding:8px 10px; border-radius:10px; font-size:12px; color:#334155;">
        <div><b>模型：</b>dam.glb（来自 模型.zip 的 D1.zip）</div>
        <div><b>交互：</b>点击测点 → 右侧切换数据</div>
      </div>
    </div>

    <div class="card" style="flex: 4; padding:12px; overflow:auto;">
      <div style="display:flex; align-items:center; justify-content:space-between; gap:8px;">
        <div style="font-weight:700; color:var(--brand-blue-2);">测点数据管理</div>
        <el-select v-model="selectedPointId" placeholder="选择测点" style="width:160px" @change="refreshMeasurements">
          <el-option v-for="p in points" :key="p.id" :label="p.name" :value="p.id" />
        </el-select>
      </div>

      <div style="margin-top:10px; display:flex; gap:8px;">
        <el-button type="primary" @click="openAdd">新增</el-button>
        <el-button @click="refreshMeasurements">刷新</el-button>
      </div>

      <el-table :data="measurements" size="small" style="margin-top:10px" height="260">
        <el-table-column prop="measureDate" label="日期" width="120" />
        <el-table-column prop="valueMm" label="位移(mm)" />
        <el-table-column label="操作" width="140">
          <template #default="scope">
            <el-button link type="primary" @click="openEdit(scope.row)">编辑</el-button>
            <el-popconfirm title="确定删除？" @confirm="onDelete(scope.row)">
              <template #reference>
                <el-button link type="danger">删除</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>

      <div style="margin-top:12px; font-weight:700; color:#0f172a;">折线图</div>
      <div ref="chartEl" style="height:260px;"></div>

      <el-dialog v-model="dlgVisible" :title="dlgMode==='add' ? '新增测值' : '编辑测值'" width="420">
        <el-form :model="form" label-width="90px">
          <el-form-item label="日期">
            <el-date-picker v-model="form.measureDate" type="date" value-format="YYYY-MM-DD" style="width:100%" />
          </el-form-item>
          <el-form-item label="位移(mm)">
            <el-input-number v-model="form.valueMm" :step="0.01" :precision="3" style="width:100%" />
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="dlgVisible=false">取消</el-button>
          <el-button type="primary" @click="onSave">保存</el-button>
        </template>
      </el-dialog>

    </div>
  </div>
</template>

<script setup>
import { onMounted, onBeforeUnmount, ref, reactive, watch } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import * as Cesium from 'cesium'

import { listPoints, listMeasurements, addMeasurement, updateMeasurement, deleteMeasurement } from '../api/monitoring'

const viewerEl = ref(null)
const chartEl = ref(null)

const points = ref([])
const selectedPointId = ref(null)
const measurements = ref([])

let viewer = null
let chart = null
let pointEntities = new Map()
let damEntity = null

const dlgVisible = ref(false)
const dlgMode = ref('add')
const editingId = ref(null)

const form = reactive({
  measureDate: '',
  valueMm: 0
})

function formatDateISO(d) {
  return d
}

async function refreshPoints() {
  points.value = await listPoints()
  if (!selectedPointId.value && points.value.length) {
    selectedPointId.value = points.value[0].id
  }
}

async function refreshMeasurements() {
  if (!selectedPointId.value) return
  measurements.value = await listMeasurements(selectedPointId.value)
  renderChart()
}

function openAdd() {
  dlgMode.value = 'add'
  editingId.value = null
  form.measureDate = '2025-01-15'
  form.valueMm = 0.21
  dlgVisible.value = true
}

function openEdit(row) {
  dlgMode.value = 'edit'
  editingId.value = row.id
  form.measureDate = row.measureDate
  form.valueMm = row.valueMm
  dlgVisible.value = true
}

async function onSave() {
  if (!selectedPointId.value) return
  if (!form.measureDate) {
    ElMessage.warning('请选择日期')
    return
  }
  const payload = {
    measureDate: formatDateISO(form.measureDate),
    valueMm: Number(form.valueMm)
  }
  if (dlgMode.value === 'add') {
    await addMeasurement(selectedPointId.value, payload)
    ElMessage.success('已新增')
  } else {
    await updateMeasurement(editingId.value, payload)
    ElMessage.success('已更新')
  }
  dlgVisible.value = false
  await refreshMeasurements()
}

async function onDelete(row) {
  await deleteMeasurement(row.id)
  ElMessage.success('已删除')
  await refreshMeasurements()
}

function renderChart() {
  if (!chart) return
  const xs = measurements.value.map(m => m.measureDate)
  const ys = measurements.value.map(m => m.valueMm)
  chart.setOption({
    tooltip: { trigger: 'axis' },
    grid: { left: 40, right: 12, top: 24, bottom: 36 },
    xAxis: { type: 'category', data: xs },
    yAxis: { type: 'value', name: 'mm' },
    series: [{ type: 'line', data: ys, smooth: true }]
  })
}

function initCesiumViewer() {
  viewer = new Cesium.Viewer(viewerEl.value, {
    animation: false,
    timeline: false,
    baseLayerPicker: false,
    geocoder: false,
    homeButton: false,
    sceneModePicker: false,
    navigationHelpButton: false,
    fullscreenButton: false,
    terrainProvider: new Cesium.EllipsoidTerrainProvider(),
    imageryProvider: new Cesium.UrlTemplateImageryProvider({
      url: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png'
    })
  })

  viewer.scene.globe.depthTestAgainstTerrain = true

  // 画一个简易“河面”多边形（蓝色半透明）
  const river = viewer.entities.add({
    polygon: {
      hierarchy: Cesium.Cartesian3.fromDegreesArray([
        118.7456, 32.0603,
        118.7464, 32.0603,
        118.7466, 32.0596,
        118.7454, 32.0596
      ]),
      material: Cesium.Color.CYAN.withAlpha(0.35)
    }
  })

  // 允许近距离观察模型 & 远距离查看地图
  viewer.scene.globe.depthTestAgainstTerrain = false
  viewer.scene.screenSpaceCameraController.minimumZoomDistance = 10
  viewer.scene.screenSpaceCameraController.maximumZoomDistance = 50_000_000

  // 大坝模型锚点（与后端 seed 的 lon/lat/height 一致）
  const lon = 118.7460
  const lat = 32.0600
  const height = 30.0
  const basePos = Cesium.Cartesian3.fromDegrees(lon, lat, height)

  damEntity = viewer.entities.add({
    name: '大坝模型',
    position: basePos,
    model: {
      uri: '/models/dam.glb',
      scale: 5.0,
      minimumPixelSize: 128
    }
  })

  viewer.camera.flyTo({
    destination: Cesium.Cartesian3.fromDegrees(lon, lat, 350.0),
    orientation: {
      heading: Cesium.Math.toRadians(0),
      pitch: Cesium.Math.toRadians(-35),
      roll: 0
    }
  })

  // 点击实体：如果是测点，则切换选中
  const handler = new Cesium.ScreenSpaceEventHandler(viewer.scene.canvas)
  handler.setInputAction((movement) => {
    const picked = viewer.scene.pick(movement.position)
    if (!picked || !picked.id) return
    const ent = picked.id

    // 点击测点：选中 + 飞到该位置
    if (ent && ent.properties && ent.properties.pointId) {
      const pid = ent.properties.pointId.getValue()
      selectedPointId.value = pid
      flyToPoint(pid)
      return
    }

    // 点击大坝：飞到大坝附近
    if (ent && ent.name === '大坝模型') {
      viewer.flyTo(ent, { duration: 1.2 })
    }
  }, Cesium.ScreenSpaceEventType.LEFT_CLICK)

  viewer.__pickHandler = handler
}

function flyToPoint(pointId) {
  if (!viewer) return
  const ent = pointEntities.get(pointId)
  if (!ent) return
  viewer.flyTo(ent, {
    duration: 1.2,
    offset: new Cesium.HeadingPitchRange(0, -0.5, 120)
  })
}

function updateCesiumPoints() {
  if (!viewer) return
  // 清理旧点
  for (const ent of pointEntities.values()) {
    viewer.entities.remove(ent)
  }
  pointEntities.clear()

  for (const p of points.value) {
    if (p.lon == null || p.lat == null || p.height == null) continue
    const base = Cesium.Cartesian3.fromDegrees(p.lon, p.lat, p.height)
    const enu = Cesium.Transforms.eastNorthUpToFixedFrame(base)
    const offset = new Cesium.Cartesian3(p.offsetEast || 0, p.offsetNorth || 0, p.offsetUp || 0)
    const pos = Cesium.Matrix4.multiplyByPoint(enu, offset, new Cesium.Cartesian3())

    const ent = viewer.entities.add({
      name: p.name,
      position: pos,
      point: {
        pixelSize: 12,
        color: Cesium.Color.YELLOW,
        outlineColor: Cesium.Color.BLACK,
        outlineWidth: 2
      },
      label: {
        text: p.name,
        font: '14px sans-serif',
        pixelOffset: new Cesium.Cartesian2(0, -18),
        fillColor: Cesium.Color.WHITE,
        outlineColor: Cesium.Color.BLACK,
        outlineWidth: 3,
        style: Cesium.LabelStyle.FILL_AND_OUTLINE
      },
      properties: {
        pointId: p.id
      }
    })
    pointEntities.set(p.id, ent)
  }
}

watch(selectedPointId, async () => {
  await refreshMeasurements()
  flyToPoint(selectedPointId.value)
})

onMounted(async () => {
  initCesiumViewer()
  chart = echarts.init(chartEl.value)

  await refreshPoints()
  updateCesiumPoints()
  await refreshMeasurements()
})

onBeforeUnmount(() => {
  if (chart) chart.dispose()
  if (viewer && viewer.__pickHandler) viewer.__pickHandler.destroy()
  if (viewer) viewer.destroy()
})
</script>
