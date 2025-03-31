<template>
  <div class="map-navigation">
    <!-- 地图容器 -->
    <div id="map" class="map"></div>

    <!-- 控制面板 -->
    <div class="controls">
      <el-input
        v-model="startAddress"
        placeholder="请输入起点地址"
        style="width: 200px"
      />
      <el-input
        v-model="endAddress"
        placeholder="请输入终点地址"
        style="width: 200px"
      />
      <el-button type="primary" @click="planRoute">规划路线</el-button>
    </div>

    <!-- 路径规划结果 -->
    <div id="route-panel" class="route-panel"></div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";

const map = ref(null);
const startAddress = ref("");
const endAddress = ref("");
const AMapRef = ref(null); // 存储 AMap 对象

// **动态加载高德地图 API**
const loadAMapScript = () => {
  return new Promise((resolve, reject) => {
    if (window.AMap) {
      AMapRef.value = window.AMap;
      return resolve(window.AMap);
    }
    const script = document.createElement("script");
    script.type = "text/javascript";
    script.src =
      "https://webapi.amap.com/maps?v   =2.0&key=YOUR_AMAP_API_KEY&plugin=AMap.Driving,AMap.Geocoder,AMap.Scale,AMap.ControlBar";

    script.onload = () => {
      AMapRef.value = window.AMap;
      resolve(window.AMap);
    };
    script.onerror = (error) => reject(error);
    document.head.appendChild(script);
  });
};

// **初始化地图**
const initMap = async () => {
  try {
    const AMap = await loadAMapScript();
    map.value = new AMap.Map("map", {
      center: [104.225532, 30.726747], // 替换为实际位置
      zoom: 15,
      resizeEnable: true,
    });

    // 添加控件
    map.value.addControl(new AMap.ControlBar());
    map.value.addControl(new AMap.Scale());
  } catch (error) {
    console.error("高德地图加载失败:", error);
  }
};

// **规划路线**
const planRoute = async () => {
  if (!startAddress.value || !endAddress.value) {
    alert("请输入起点和终点");
    return;
  }

  try {
    const AMap = await loadAMapScript(); // 确保 AMap 加载完成
    AMap.plugin("AMap.Driving", () => {
      const driving = new AMap.Driving({
        map: map.value,
        panel: "route-panel",
      });

      driving.search(startAddress.value, endAddress.value, (status, result) => {
        if (status === "complete") {
          console.log("路线规划成功", result);
        } else {
          console.error("路线规划失败:", result);
          alert("路线规划失败，请检查地址是否正确");
        }
      });
    });
  } catch (error) {
    console.error("路线规划出错:", error);
  }
};

onMounted(() => {
  initMap();
});
</script>

<style scoped>
.map-navigation {
  position: relative;
  width: 100%;
  height: 600px;
}

.map {
  width: 100%;
  height: 100%;
}

.controls {
  position: absolute;
  top: 10px;
  left: 10px;
  background: rgba(255, 255, 255, 0.9);
  padding: 10px;
  border-radius: 4px;
  z-index: 1000;
  display: flex;
  gap: 10px;
  align-items: center;
}

.route-panel {
  position: absolute;
  right: 10px;
  top: 10px;
  width: 300px;
  max-height: 400px;
  overflow-y: auto;
  background: rgba(255, 255, 255, 0.9);
  padding: 10px;
  border-radius: 4px;
  z-index: 1000;
}
</style>
