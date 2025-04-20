<!-- <template>
  <div class="map-navigation">
    <div id="map" class="map"></div>

    <div class="controls">
      <el-autocomplete
        v-model="startAddressInput"
        :fetch-suggestions="searchAddress"
        placeholder="输入起点"
        style="width: 280px"
        @select="handleAddressSelect('start', $event)"
        clearable
      />
      <el-autocomplete
        v-model="endAddressInput"
        :fetch-suggestions="searchAddress"
        placeholder="输入终点"
        style="width: 280px"
        @select="handleAddressSelect('end', $event)"
        clearable
      />
      <el-button 
        type="primary" 
        @click="planRoute" 
        :loading="isLoading"
        :disabled="!isRouteValid"
      >
        规划路线
      </el-button>
      <el-button @click="clearAll">清除</el-button>
    </div>

    <div id="route-panel" class="route-panel"></div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from "vue";

// 安全配置（必须放在最前面）
window._AMapSecurityConfig = {
  securityJsCode: '60100f85d5bc1aabddc4d5384a010425'
};

// 核心变量
const map = ref(null);
const startAddressInput = ref("");
const endAddressInput = ref("");
const startAddress = ref({ lng: null, lat: null });
const endAddress = ref({ lng: null, lat: null });
const isLoading = ref(false);
const geocoder = ref(null);
const driving = ref(null);
const markers = ref([]);

// 加载高德地图API
const loadAMapScript = () => {
  return new Promise((resolve, reject) => {
    if (window.AMap) {
      return resolve(window.AMap);
    }
    
    if (document.getElementById("amap-script")) {
      document.getElementById("amap-script").onload = () => resolve(window.AMap);
      return;
    }
    
    const script = document.createElement("script");
    script.id = "amap-script";
    script.src = `https://webapi.amap.com/maps?v=2.0&key=ed8cee311c5cb41a73d898e830fe1a40&plugin=AMap.Geocoder,AMap.Driving,AMap.PlaceSearch,AMap.ToolBar,AMap.Scale`;
    
    script.onload = () => resolve(window.AMap);
    script.onerror = reject;
    
    document.head.appendChild(script);
  });
};

// 初始化地图
const initMap = async () => {
  try {
    await loadAMapScript();
    
    // 创建地图实例
    map.value = new window.AMap.Map("map", {
      zoom: 16,
      center: [104.0520945, 30.6975192],
      scrollWheel: true,
      resizeEnable: true
    });

    // 初始化插件
    geocoder.value = new window.AMap.Geocoder({ city: "全国" });
    driving.value = new window.AMap.Driving({
      map: map.value,
      panel: "route-panel",
      policy: window.AMap.DrivingPolicy.LEAST_TIME
    });

    // 添加地图控件
    map.value.addControl(new window.AMap.Scale());
    map.value.addControl(new window.AMap.ToolBar());
  } catch (error) {
    console.error("地图初始化失败:", error);
    alert("地图加载失败，请检查控制台日志");
  }
};

// 地址搜索功能
const searchAddress = async (query, cb) => {
  if (!query || query.trim().length < 2) return cb([]);

  try {
    const placeSearch = new window.AMap.PlaceSearch({
      city: "全国",
      pageSize: 5
    });

    placeSearch.search(query, (status, result) => {
      if (status === 'complete' && result?.poiList?.pois) {
        const suggestions = result.poiList.pois
          .filter(poi => poi.location)
          .map(poi => ({
            value: `${poi.name} · ${poi.address || poi.district || '未知地址'}`,
            lng: poi.location.lng,
            lat: poi.location.lat
          }));
        cb(suggestions);
      } else {
        cb([{ value: '未找到相关地址', disabled: true }]);
      }
    });
  } catch (error) {
    console.error('搜索失败:', error);
    cb([{ value: '搜索服务不可用', disabled: true }]);
  }
};

// 处理地址选择
const handleAddressSelect = (type, item) => {
  if (!item?.lng || !item?.lat) return;

  const position = [item.lng, item.lat];
  
  if (type === "start") {
    startAddress.value = { lng: item.lng, lat: item.lat };
    addMarker(position, "起点");
  } else {
    endAddress.value = { lng: item.lng, lat: item.lat };
    addMarker(position, "终点");
  }

  // 自动调整地图视角
  const points = [];
  if (startAddress.value.lng) points.push([startAddress.value.lng, startAddress.value.lat]);
  if (endAddress.value.lng) points.push([endAddress.value.lng, endAddress.value.lat]);

  if (points.length > 0) {
    map.value.setFitView(points);
  }
};


// 添加地图标记
const addMarker = (position, title) => {
  const marker = new window.AMap.Marker({
    position,
    title,
    map: map.value,
    draggable: true, // 允许拖拽
    icon: new window.AMap.Icon({
      image: title === "起点"
        ? "https://webapi.amap.com/theme/v1.3/markers/n/mark_b.png"
        : "https://webapi.amap.com/theme/v1.3/markers/n/mark_r.png",
      size: new window.AMap.Size(32, 32),
    }),
  });

  // 监听拖拽事件，实时更新坐标和地址
  marker.on("dragend", (event) => {
    const { lng, lat } = event.lnglat;
    
    if (title === "起点") {
      startAddress.value = { lng, lat };
      getAddressFromCoords(lng, lat, "start");
    } else {
      endAddress.value = { lng, lat };
      getAddressFromCoords(lng, lat, "end");
    }

    // 重新规划路径
    if (isRouteValid.value) {
      planRoute();
    }
  });

  markers.value.push(marker);
};

// 根据坐标获取地址
const getAddressFromCoords = (lng, lat, type) => {
  if (!geocoder.value) return;

  geocoder.value.getAddress([lng, lat], (status, result) => {
    if (status === "complete" && result.regeocode) {
      const formattedAddress = result.regeocode.formattedAddress;
      
      if (type === "start") {
        startAddressInput.value = formattedAddress;
      } else {
        endAddressInput.value = formattedAddress;
      }
    }
  });
};


// 路径规划有效性验证
const isRouteValid = computed(() => {
  return startAddress.value.lng && endAddress.value.lat;
});

// 执行路径规划
const planRoute = async () => {
  if (!isRouteValid.value) return;
  
  isLoading.value = true;
  try {
    driving.value.search(
      [startAddress.value.lng, startAddress.value.lat],
      [endAddress.value.lng, endAddress.value.lat],
      (status, result) => {
        isLoading.value = false;
        if (status !== 'complete') {
          alert(result?.info || '路线规划失败');
        }
      }
    );
  } catch (error) {
    isLoading.value = false;
    console.error('路径规划异常:', error);
    alert('路线规划服务异常');
  }
};

// 清除所有内容
const clearAll = () => {
  // 清除标记
  markers.value.forEach(marker => marker.setMap(null));
  markers.value = [];
  
  // 清除路线
  driving.value.clear();
  
  // 重置表单
  startAddressInput.value = "";
  endAddressInput.value = "";
  startAddress.value = { lng: null, lat: null };
  endAddress.value = { lng: null, lat: null };
};

// 生命周期管理
onMounted(initMap);
onUnmounted(() => {
  if (map.value) {
    map.value.destroy();
    map.value = null;
  }
});
</script> -->



<!-- 


<style scoped>
.map-navigation {
  position: relative;
  height: 600px;
  margin: 20px;
}

.map {
  width: 100%;
  height: 100%;
  border-radius: 8px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
}

.controls {
  position: absolute;
  top: 20px;
  left: 20px;
  background: white;
  padding: 15px;
  border-radius: 8px;
  display: flex;
  gap: 15px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
  z-index: 1000;
}

.route-panel {
  position: absolute;
  top: 20px;
  right: 20px;
  width: 350px;
  max-height: 500px;
  overflow-y: auto;
  background: white;
  padding: 15px;
  border-radius: 8px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.1);
  z-index: 1000;
}
</style> -->