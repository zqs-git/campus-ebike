const path = require('path');

module.exports = {
  transpileDependencies: true,  // 保留这个配置

  devServer: {
    hot: false, // 禁用热重载
  },

  configureWebpack: {
    resolve: {
      // 配置 Webpack 查找模块的路径
      modules: [
        path.resolve(__dirname, 'path/to/frontend/node_modules'),  // 确保路径指向你的前端子目录中的 node_modules
        'node_modules'  // 默认的查找路径
      ]
    }
  }
}
