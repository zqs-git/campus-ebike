<template>
  <div class="map-navigation">
    <!-- 地图容器 -->
    <div id="map" class="map"></div>

    <!-- 修改后的绘制控件 -->
    <div class="drawing-controls" v-if="isAdmin">
      <!-- 区域类型选择 -->
      <el-dropdown @command="handleAreaType">
        <el-button type="primary" :disabled="!isDrawingReady">
          绘制区域
          <i class="el-icon-arrow-down el-icon--right"></i>
        </el-button>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="parking">停车区</el-dropdown-item>
            <el-dropdown-item command="no-parking">禁停区</el-dropdown-item>
            <el-dropdown-item command="green">绿化区</el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>

      <!-- 地点类型选择 -->
      <el-dropdown @command="handlePointType">
        <el-button type="success" :disabled="!isDrawingReady">
          添加地点
          <i class="el-icon-arrow-down el-icon--right"></i>
        </el-button>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="charging">充电桩</el-dropdown-item>
            <el-dropdown-item command="entrance">入口</el-dropdown-item>
            <el-dropdown-item command="dining">食堂</el-dropdown-item>
            <el-dropdown-item command="building">教学楼</el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>

      <!-- 保留原有清除按钮 -->
      <el-button @click="clearDrawnAreas" type="warning">
        清除所有
      </el-button>
    </div>

    <!-- 路线规划控件区域 -->
    <div class="controls">
      <h3>路线规划</h3>
      <!-- 起点输入自动补全 -->
      <el-autocomplete
        v-model="startAddressInput"
        :fetch-suggestions="debouncedSearchAddress"
        placeholder="输入起点"
        style="width: 280px"
        @select="handleAddressSelect('start', $event)"
        @keyup.enter="handleAddressSelect('start', startAddressInput)"
        clearable
      />
      <!-- 终点输入自动补全 -->
      <el-autocomplete
        v-model="endAddressInput"
        :fetch-suggestions="debouncedSearchAddress"
        placeholder="输入终点"
        style="width: 280px"
        @select="handleAddressSelect('end', $event)"
        @keyup.enter="handleAddressSelect('end', endAddressInput)"
        clearable
      />
      <!-- 路线策略选择 -->
      <el-select v-model="routePolicy" placeholder="选择路线策略" style="width: 180px">
        <el-option label="最快路线" value="LEAST_TIME" />
        <el-option label="最短距离" value="LEAST_DISTANCE" />
        <el-option label="避开拥堵" value="AVOID_CONGESTION" />
      </el-select>
      <!-- 排序方式选择：距离或相关性 -->
      <el-select v-model="sortMethod" placeholder="选择排序方式" style="width: 180px">
        <el-option label="按距离排序" value="distance" />
        <el-option label="按相关性排序" value="relevance" />
      </el-select>
      <!-- 触发路线规划 -->
      <el-button type="primary" @click="planRoute" :loading="isLoading" :disabled="!isRouteValid">
        规划路线
      </el-button>

      <!-- 清除所有标记及绘制区域 -->
      <el-button @click="clearAll">清除</el-button>
      <!-- 实时获取并定位用户位置 -->
      <el-button @click="locateUser">实时定位</el-button>
    </div>

    <!-- 驾车导航结果面板 -->
    <div id="route-panel" class="route-panel"></div>

    <!-- 查看 / 编辑 / 删除 对话框 -->
    <el-dialog
      :title="isAdmin ? '编辑信息' : '查看信息'"
      v-model="isDialogVisible"
      width="420px"
      @close="resetDialog"
    >
      <el-form :model="dialogForm" label-width="80px">
        <el-form-item label="名称">
          <el-input v-model="dialogForm.name" :disabled="!isAdmin" />
        </el-form-item>
        <el-form-item label="类型">
          <el-select v-model="dialogForm.type" :disabled="!isAdmin">
            <el-option
              v-for="(cfg, key) in typeConfig"
              :key="key"
              :label="cfg.label"
              :value="key"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="坐标">
          <span>{{ dialogForm.latitude.toFixed(6) }}, {{ dialogForm.longitude.toFixed(6) }}</span>
        </el-form-item>
        <el-form-item label="详细描述">
          <el-input
            type="textarea"
            v-model="dialogForm.description"
            :disabled="!isAdmin"
            rows="3"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button v-if="isAdmin" type="danger" @click="onDelete">删除</el-button>
        <el-button v-if="isAdmin" type="primary" @click="onSave">保存</el-button>
        <!-- — 新增：一键导航 -->
        <el-button 
          v-if="!!targetLocation.lat" 
          type="success" 
          @click="startNavigation"
          :loading="isLoading"
        >
          导航到此处
        </el-button>
        <el-button @click="isDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive,onMounted,  computed, watch } from 'vue'
import { debounce } from 'lodash'
import { ElMessageBox, ElMessage } from 'element-plus'
import { useAreaStore } from '@/store/areas' 
import { useAuthStore } from '@/store/auth'

// 高德安全配置
window._AMapSecurityConfig = {
  securityJsCode: '60100f85d5bc1aabddc4d5384a010425'
}

// 用户角色相关

const authStore = useAuthStore();
const userRole = computed(() => authStore.user?.role ?? 'student')
const isAdmin = computed(() => userRole.value === "admin");
// const isStaff = computed(() => userRole.value === "staff");
// const isVisitor = computed(() => userRole.value === "visitor");
// const isStudent = computed(() => userRole.value === "student");
// const isStudentOrStaff = computed(() => userRole.value === "student" || userRole.value === "staff");

// 地图相关状态和引用
const map = ref(null)
const drawing = ref(null)
const isDrawingReady = ref(false)
const drawnAreas = ref([]) // 后端加载的所有区域
const areaStore = useAreaStore()
const mapItems = []; // { id, type, shape?, marker? }
const markers = []; // 全局存放所有标注对象
// 地址、导航状态
const startAddressInput = ref('')
const endAddressInput = ref('')
const startAddress = ref({ lng: null, lat: null })
const endAddress = ref({ lng: null, lat: null })
const routePolicy = ref('LEAST_TIME')
const sortMethod = ref('relevance')
const isLoading = ref(false)
const driving = ref(null)
const userMarker = ref(null)
// let userLocationInterval = null

const geolocationService = ref(null)


// 对话框相关
const isDialogVisible = ref(false)
const dialogForm = reactive({
  id: null,
  name: '',
  type: '',
  latitude: 0,
  longitude: 0,
  pathStr: '',
  description: ''
})



// 类型映射
const typeConfig = {
  // 区域类型
  parking: { color: '#00FF0080', label: '停车区' },
  'no-parking': { color: '#FF000080', label: '禁停区' },
  green: { color: '#00FF8080', label: '绿化区' },
  
  // 地点类型
  charging: { color: '#67C23A', icon: 'lightning', label: '充电桩' },
  entrance: { color: '#409EFF', icon: 'gateway', label: '入口' },
  dining: { color: '#E6A23C', icon: 'food', label: '食堂' },
  building: { color: '#909399', icon: 'school', label: '教学楼' }
}

const getFontSizeByZoom = (zoom) => {
  if (zoom >= 15) return 14;
  if (zoom >= 12) return 12;
  if (zoom >= 10) return 10;
  return 8;
};

const currentDrawingType = ref('parking')


// 修改后的绘制处理
const handleAreaType = async (type) => {
  currentDrawingType.value = type;
  startDrawing();
};

// 新增地点处理
let pointClickHandler = null;

const handlePointType = async (type) => {
  try {
    const { value: name } = await ElMessageBox.prompt(
      '请输入地点名称',
      `添加${typeConfig[type].label}`,
      { inputPattern: /\S+/, inputErrorMessage: '名称不能为空' }
    );

    // 先解绑上一次的，确保干净
    if (pointClickHandler) {
      map.value.off('click', pointClickHandler);
    }

    // 定义一个具名函数
    pointClickHandler = async (e) => {
      // 先解绑自己
      map.value.off('click', pointClickHandler);

      const lnglat = e.lnglat;
      const areaData = {
        name,
        type,
        latitude: lnglat.getLat(),
        longitude: lnglat.getLng(),
        path: [[lnglat.getLng(), lnglat.getLat()]],
        description: '', // 可选描述
      };

      try {
        // 直接 push 到前端 store 的 list
        const saved = await areaStore.saveAreaToServer(areaData)
        console.log('addAreaToMap 收到的 item:', saved)
        // 然后再把它画出来
        addAreaToMap(saved)

        ElMessage.success(`${typeConfig[type].label}已添加`);
      } catch (error) {
        ElMessage.error('保存失败: ' + error.message);
      }
    };

    // 绑定具名 handler
    map.value.on('click', pointClickHandler);
    ElMessage.info('请在地图上点击选择位置');
  } catch {
    ElMessage.warning('取消添加');
  }
};






function addAreaToMap(item) {
  const config = getTypeConfig(item.type);

  if (['parking','no-parking','green'].includes(item.type)) {
    // 画多边形
    const polygon = new window.AMap.Polygon({
      map: map.value,
      path: item.path,
      fillColor: config.color,
      strokeColor: adjustColor(config.color, -30),
      strokeWeight: 2,
    });
    // 文字标注
    const center = polygon.getBounds().getCenter();
    const textMarker = new window.AMap.Text({
      map: map.value,
      position: center,
      text: item.name,
      style: { /* ... */ },
    });

    // 记录
    mapItems.push({ id: item.id, type: item.type, shape: polygon, marker: textMarker });

    // 绑定点击事件
    polygon.on('click', () => handleAreaClick(item.id));
  }
  else {
    // 画点
    const marker = new window.AMap.Marker({
      position: [item.longitude, item.latitude],
      content: createPointContent(item),
      map: map.value,
    });
    mapItems.push({ id: item.id, type: item.type, marker });
    marker.on('click', () => handleAreaClick(item.id));
  }
}



// 添加：存储当前点击的目标位置
const targetLocation = ref({ lat: null, lng: null })

// 点击地图元素弹出对话框
function handleAreaClick(id) {
  const area = areaStore.list.find(a => a.id === id);
  if (!area) return;

  // 坐标验证
  if (
    typeof area.latitude !== 'number' ||
    typeof area.longitude !== 'number' ||
    isNaN(area.latitude) ||
    isNaN(area.longitude)
  ) {
    return ElMessage.error('该地点坐标数据异常');
  }

  // 保留6位小数处理
  targetLocation.value = {
    lat: Number(area.latitude.toFixed(6)),
    lng: Number(area.longitude.toFixed(6))
  };

  // 填充对话框
  dialogForm.id = area.id;
  dialogForm.name = area.name;
  dialogForm.type = area.type;
  dialogForm.latitude = area.latitude;
  dialogForm.longitude = area.longitude;
  dialogForm.pathStr = JSON.stringify(area.path);
  dialogForm.description = area.description || '';

  // 显示对话框
  isDialogVisible.value = true;
}


// — 新增：一键导航方法
// 一键导航
const startNavigation = async () => {
  // 新增坐标有效性验证
  const isValidCoordinate = (coord) => 
    typeof coord === 'number' && !isNaN(coord) && coord !== 0;

  // Check if both latitude and longitude for targetLocation are valid
  if (!targetLocation.value || !isValidCoordinate(targetLocation.value.lat) || !isValidCoordinate(targetLocation.value.lng)) {
    return ElMessage.warning('请先在地图上点击选择有效目标位置');
  }

  try {
    const userLocation = await getUserLocation();
    console.log('用户位置:', userLocation);

    // 坐标范围验证（示例坐标范围）
    if (
      Math.abs(userLocation.lng) > 180 || 
      Math.abs(userLocation.lat) > 90 ||
      Math.abs(targetLocation.value.lng) > 180 ||
      Math.abs(targetLocation.value.lat) > 90
    ) {
      throw new Error('无效的坐标范围');
    }

    // 转换为高德要求的数组格式
    const start = [userLocation.lng, userLocation.lat];
    const end = [targetLocation.value.lng, targetLocation.value.lat];

    console.log("Start Address:", start);
    console.log("End Address:", end);

    isLoading.value = true;
    driving.value.search(start, end, (status, result) => {
      isLoading.value = false;
      
      if (status === 'complete') {
        if (result.routes && result.routes.length > 0) {
          ElMessage.success(`找到${result.routes.length}条路线`);
        } else {
          ElMessage.warning('成功获取结果但未找到可行路线');
        }
      } else {
        const errorInfo = {
          'ROUTE_FAIL': '路径计算失败',
          'INVALID_USER_KEY': '密钥无效',
          'INSUFFICIENT_PRIVILEGES': '权限不足',
          'SERVICE_RESPONSE_ERROR': '服务响应异常'
        }[result.info] || result.info;
        
        ElMessage.error(`导航失败: ${errorInfo}`);
        console.error('详细错误信息:', {
          status,
          info: result.info,
          details: result
        });
      }
    });

  } catch (error) {
    isLoading.value = false;
    console.error('导航过程中发生错误:', error);
    ElMessage.error(`导航失败: ${error.message}`);
  }
};



// Update the map when save happens
async function onSave() {
  try {
    const updatedData = {
      name: dialogForm.name,
      type: dialogForm.type,
      latitude: dialogForm.latitude,
      longitude: dialogForm.longitude,
      path: JSON.parse(dialogForm.pathStr),
      description: dialogForm.description,
    };

    await areaStore.updateAreaInServer(dialogForm.id, updatedData);

    // Update the map with the new details
    updateMapItem(dialogForm.id, updatedData);

    ElMessage.success('更新成功');
    isDialogVisible.value = false;
  } catch (error) {
    ElMessage.error('更新失败');
  }
}




// 删除
async function onDelete() {
  try {
    await ElMessageBox.confirm('确认删除？', '删除确认', { type: 'warning' })
    await areaStore.deleteAreaFromServer(dialogForm.id)
    removeMapItem(dialogForm.id)
    ElMessage.success('删除成功')
    isDialogVisible.value = false
  } catch {
    // 取消或错误
  }
}

// 重置对话框
function resetDialog() {
  dialogForm.id = null
  dialogForm.name = ''
  dialogForm.type = ''
  dialogForm.latitude = 0
  dialogForm.longitude = 0
  dialogForm.pathStr = ''
}

function updateMapItem(id, updatedData) {
  const item = mapItems.find(m => m.id === id);
  if (!item) return;

  // Update the marker or polygon
  const config = getTypeConfig(updatedData.type);

  if (item.shape) {
    // If it's a polygon, update its path, color, and label
    item.shape.setPath(updatedData.path);
    item.shape.setOptions({
      fillColor: config.color,
      strokeColor: adjustColor(config.color, -30),
    });

    // Update text label for polygon
    const center = item.shape.getBounds().getCenter();
    item.marker.setText(updatedData.name);
    item.marker.setPosition(center);
  } else if (item.marker) {
    // If it's a point, update the marker
    item.marker.setIcon(config.icon);
    item.marker.setContent(createPointContent(updatedData));
    item.marker.setPosition([updatedData.longitude, updatedData.latitude]);
  }

  // Update the item data in mapItems
  item.type = updatedData.type;
  item.name = updatedData.name;
}

// 删除地图覆盖物
function removeMapItem(id) {
  const idx = mapItems.findIndex(m => m.id === id);
  if (idx === -1) return;
  const { shape, marker } = mapItems[idx];
  if (shape) shape.setMap(null);
  if (marker) marker.setMap(null);
  mapItems.splice(idx, 1);
}





// 创建点标记内容
const createPointContent = (item) => {
  const config = getTypeConfig(item.type);
  return `
    <div class="custom-marker">
      <div style="
        background: ${config.color};
        padding: 6px 12px;
        border-radius: 4px;
        color: white;
        display: flex;
        align-items: center;
        gap: 6px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.2);
      ">
        <i class="el-icon-${config.icon}"></i>
        <span>${item.name}</span>
      </div>
    </div>
  `;
}


// 颜色调整函数
const adjustColor = (hex, amount) => {
  return '#' + hex.replace(/^#/, '')
    .replace(/../g, color => 
      ('0' + Math.min(255, Math.max(0, 
        parseInt(color, 16) + amount
      )).toString(16)).slice(-2)
    )
}



/** 动态加载高德 JSAPI */
// 修改脚本加载部分的插件列表
const loadAMapScript = () => new Promise((resolve, reject) => {
  if (window.AMap) return resolve(window.AMap)
  const script = document.createElement('script')
  script.src = 'https://webapi.amap.com/maps?v=2.0&key=ed8cee311c5cb41a73d898e830fe1a40&plugin=AMap.MouseTool,AMap.Driving,AMap.PlaceSearch,AMap.ToolBar,AMap.Scale,AMap.Geolocation' // 增加Geolocation插件
  script.onload = () => resolve(window.AMap)
  script.onerror = reject
  document.head.appendChild(script)
})

// 增强类型安全访问
const getTypeConfig = (type) => {
  return typeConfig[type] || { 
    color: '#CCCCCC', 
    label: '未知区域',
    icon: 'question'
  }
}



/** 初始化地图、绘制工具和加载后端区域 */
/** 初始化地图、绘制工具和加载后端区域 */
const initMap = async () => {
  try {
    await loadAMapScript();
    
    // 初始化地图
    map.value = new window.AMap.Map('map', {
      zoom: 17,
      center: [104.0520945, 30.6975192],
      scrollWheel: true,
      resizeEnable: true,
      restrictBounds: new window.AMap.Bounds([104.048, 30.686], [104.058, 30.694])
    });

    // 初始化定位服务
    window.AMap.plugin(['AMap.Geolocation'], () => {
      geolocationService.value = new window.AMap.Geolocation({
        enableHighAccuracy: true, // 高精度定位
        timeout: 10000, // 超时时间10秒
        showButton: false // 隐藏默认定位按钮
      })
    })

    // 初始化绘制工具
    window.AMap.plugin(['AMap.MouseTool'], () => {
      if (drawing.value) {
        drawing.value.off('draw'); // 确保每次只绑定一个事件
      }
      drawing.value = new window.AMap.MouseTool(map.value);
      isDrawingReady.value = true;

      // 绑定绘制事件
      drawing.value.on('draw', async (ev) => {
        const shape = ev.obj;
        drawing.value.close(true);

        try {
          const { value: name } = await ElMessageBox.prompt(
            '请输入区域名称',
            `命名${getTypeConfig(currentDrawingType.value).label}`,
            {
              confirmButtonText: '确定',
              cancelButtonText: '取消',
              inputPattern: /\S+/,
              inputErrorMessage: '名称不能为空'
            }
          );

          // 生成符合后端的数据结构
          const areaData = {
            name,
            type: currentDrawingType.value,
            path: shape.getPath().map((p) => [p.lng, p.lat]),
            latitude: shape.getBounds().getCenter().getLat(),
            longitude: shape.getBounds().getCenter().getLng(),
            center: shape.getBounds().getCenter(), 
                       
          };

          // 保存到后端
          await areaStore.saveAreaToServer(areaData);

          addAreaToMap(areaData);
          ElMessage.success('区域已保存');
        } catch (error) {
          console.error('保存失败:', error);
          shape.setMap(null);
          ElMessage.error(`保存失败: ${error.message}`);
        }
      });
    });

    // 初始化导航服务
    window.AMap.plugin(['AMap.Driving'], () => {
      try {
        driving.value = new window.AMap.Driving({ 
          map: map.value,
          panel: 'route-panel',
          policy: window.AMap.DrivingPolicy[routePolicy.value]
        });
        console.log('导航服务初始化成功');
      } catch (error) {
        console.error('导航服务初始化失败:', error);
        ElMessage.error('导航功能初始化失败，请刷新页面');
      }
    });

    // 添加控件
    map.value.addControl(new window.AMap.Scale());
    map.value.addControl(new window.AMap.ToolBar());

    // 加载管理员已划定区域
    await areaStore.loadAreasFromServer();

    // 绑定缩放变化事件，动态调整区域名字字体大小
    map.value.on('zoomchange', () => {
    const fontSize = getFontSizeByZoom(map.value.getZoom());
    markers.forEach(({ marker }) => {
      // 只处理 AMap.Text（也就是多边形上的 label）
      if (typeof marker.getText === 'function') {
        const txt = marker.getText();
        marker.setContent(`
          <div style="
            font-size: ${fontSize}px;
            background: rgba(255,255,255,0.9);
            border: 1px solid #ddd;
            padding: 4px 8px;
            border-radius: 4px;
            white-space: nowrap;
          ">
            ${txt}
          </div>
        `);
      }
      // 对于自定义点标记（AMap.Marker + HTML content），不做任何改动
    });
  });


  } catch (error) {
    ElMessage.error('地图初始化失败: ' + error.message);
    console.error('地图初始化失败:', error);
  }
};


/** 开始绘制多边形 */
const startDrawing = () => {
  // 在这里仅触发绘制功能，不需要再绑定绘制事件
  console.log("启动绘制工具");
  drawing.value.polygon(); // 开始绘制多边形
};


/** 清除所有绘制区域（仅前端） */
const clearDrawnAreas = () => {
  drawnAreas.value.forEach((item) => {
    console.log('删除区域:', item);  // 输出正在删除的区域
    item.shape.setMap(null);  // 清除地图上的区域
  });
  drawnAreas.value = [];  // 清空已绘制区域数组
};


/** 获取用户位置（使用高德定位服务）*/
const getUserLocation = () => new Promise((resolve, reject) => {
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
      pos => resolve({ lat: pos.coords.latitude, lng: pos.coords.longitude }),
      err => {
        console.warn('HTML5 定位失败:', err.message);
        reject(err);
      },
      {
        enableHighAccuracy: true,    // 尽量使用高精度（GPS/Wi‑Fi）
        timeout: 20000,              // 超时设长一点，比如 20 秒
        maximumAge: 0
      }
    );
  } else {
    reject(new Error('浏览器不支持 HTML5 定位'));
  }
});

const getUserLocationFallback = () => new Promise((resolve, reject) => {
  if (!geolocationService.value) {
    return reject(new Error('AMap 定位服务未初始化'));
  }
  geolocationService.value.getCurrentPosition((status, result) => {
    if (status === 'complete' && result.position) {
      resolve({ lat: result.position.lat, lng: result.position.lng });
    } else {
      reject(new Error(result.info || 'AMap 定位失败'));
    }
  });
});



// /** 更新并显示用户位置 */
// const updateUserLocation = async () => {
//   try {
//     const loc = await getUserLocation();
//     if (userMarker.value) {
//       userMarker.value.setPosition(new window.AMap.LngLat(loc.lng, loc.lat));
//     } else {
//       userMarker.value = new window.AMap.Marker({ map: map.value, position: new window.AMap.LngLat(loc.lng, loc.lat), title: '我的位置' });
//     }
//     map.value.setCenter([loc.lng, loc.lat]);
//   } catch (err) {
//     console.error(err);
//   }
// };

/** 周期更新定位 */
// const startUserLocationUpdates = () => {
//   clearInterval(userLocationInterval);
//   userLocationInterval = setInterval(updateUserLocation, 5000);
// };

const locateUser = async () => {
  try {
    // 先试 HTML5 定位
    const loc = await getUserLocation();
    updateMapAndMarker(loc);
  } catch {
    // 再试 AMap 插件定位
    try {
      const loc2 = await getUserLocationFallback();
      updateMapAndMarker(loc2);
    } catch (err) {
      ElMessage.error('定位失败：' + err.message);
    }
  }
};

function updateMapAndMarker({ lat, lng }) {
  if (userMarker.value) userMarker.value.setMap(null);
  userMarker.value = new window.AMap.Marker({
    map: map.value,
    position: [lng, lat],
    title: '我的位置'
  });
  map.value.setCenter([lng, lat]);
}


/** 计算两点距离 */
const calculateDistance = (p1, p2) => {
  const R = 6378137;
  const toRad = d => (d * Math.PI) / 180;
  const dLat = toRad(p2.lat - p1.lat);
  const dLng = toRad(p2.lng - p1.lng);
  const a = Math.sin(dLat/2)**2 + Math.cos(toRad(p1.lat)) * Math.cos(toRad(p2.lat)) * Math.sin(dLng/2)**2;
  return 2*R*Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
};

/** 地址搜索并排序 */
const searchAddress = async (query, cb) => {
  if (!query.trim()) return cb([]);
  const ps = new window.AMap.PlaceSearch({ city: '全国', pageSize: 5 });
  ps.search(query, async (status, result) => {
    if (status === 'complete' && result.poiList) {
      const userLoc = await getUserLocation();
      let list = result.poiList.pois.map(poi => ({
        value: `${poi.name} · ${poi.address || poi.district}`,
        lng: poi.location.lng,
        lat: poi.location.lat,
        distance: calculateDistance(userLoc, poi.location),
        relevance: poi.name.length,
      }));
      list.sort((a,b) => sortMethod.value==='distance' ? a.distance-b.distance : b.relevance-a.relevance);
      cb(list);
    } else cb([{ value:'未找到相关地址', disabled:true }]);
  });
};
const debouncedSearchAddress = debounce(searchAddress, 500);

/** 选中地址后处理 */
const handleAddressSelect = (type, item) => {
  if (!item.lng) return;
  const pos = [item.lng, item.lat];
  new window.AMap.Marker({ position: pos, map: map.value, title: type==='start'? '起点':'终点', draggable:true});
  if (type==='start') { startAddress.value={lng:item.lng,lat:item.lat}; localStorage.setItem('startCoords',JSON.stringify(startAddress.value)); }
  else { endAddress.value={lng:item.lng,lat:item.lat}; localStorage.setItem('endCoords',JSON.stringify(endAddress.value)); }
  localStorage.setItem(type==='start'?'startAddress':'endAddress', item.value);
  map.value.setFitView([startAddress.value,endAddress.value].filter(p=>p.lng));
};

const isRouteValid = computed(() => !!startAddress.value.lng && !!endAddress.value.lng);
watch(routePolicy, np => { if(driving.value&&isRouteValid.value){ driving.value.setPolicy(window.AMap.DrivingPolicy[np]); planRoute(); }});

/** 发起路线规划 */
const planRoute = () => {
  if(!isRouteValid.value) return;
  isLoading.value=true;
  driving.value.search([startAddress.value.lng,startAddress.value.lat],[endAddress.value.lng,endAddress.value.lat],(status,result)=>{
    isLoading.value=false;
    if(status!=='complete') ElMessage.error(result.info||'规划失败');
  });
};

/** 清除所有数据及覆盖物 */
const clearAll = () => {
  map.value.clearMap();
  startAddressInput.value=''; endAddressInput.value='';
  startAddress.value={lng:null,lat:null}; endAddress.value={lng:null,lat:null};
  ['startAddress','endAddress','startCoords','endCoords'].forEach(k=>localStorage.removeItem(k));
  clearDrawnAreas();
};


const renderStoredAreas = () => {
  areaStore.list.forEach(area => {
    if (Array.isArray(area.path) && area.path.length > 0) {
      console.log('区域路径:', area.path);  // 检查路径数据
      addAreaToMap(area);
    } else {
      console.warn('无效的路径数据:', area);
    }
  });
};



onMounted(async () => {
  await initMap()
  await areaStore.loadAreasFromServer()
  renderStoredAreas()
})




// onUnmounted(() => clearInterval(userLocationInterval));
</script>

<style scoped>
.map-navigation { display: flex; flex-direction: column; align-items: center; background: #f4f6f9; padding: 20px; border-radius: 10px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }
.controls { display: flex; flex-direction: column; gap: 15px; width: 100%; max-width: 440px; margin-bottom: 20px; background: #fff; padding: 20px; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
.drawing-controls { margin-top: 20px; display: flex; gap: 10px; padding: 10px; background: #fff; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
.map { width: 100%; height: 450px; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }
.route-panel { width: 100%; max-width: 360px; margin-top: 20px; background: #fff; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); padding: 15px; }
.el-autocomplete, .el-select { margin-bottom: 15px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
.el-autocomplete .el-input__inner, .el-select .el-input__inner { padding: 10px 15px; font-size: 14px; border-radius: 8px; background: #f7f9fc; border: 1px solid #dce2e7; }
.el-autocomplete .el-input__inner:focus, .el-select .el-input__inner:focus { border-color: #409EFF; box-shadow: 0 0 5px rgba(64,158,255,0.5); }
.el-button { padding: 10px 20px; background: #409EFF; color: #fff; border: none; border-radius: 5px; font-size: 14px; cursor: pointer; transition: background 0.3s; }
.el-button:disabled { background: #dce2e7; cursor: not-allowed; }
.el-button:hover { background: #66b1ff; }
.el-button + .el-button { margin-left: 10px; }
@media (max-width: 600px) {
  .map-navigation { padding: 10px; }
  .controls { width: 100%; margin-bottom: 10px; }
  .map { height: 300px; }
  .route-panel { max-width: 100%; }
}
.custom-marker {
  transform: translate(-50%, -100%);
  font-size: 14px;
  white-space: nowrap;
}

.custom-marker i {
  font-size: 16px;
}


</style>
