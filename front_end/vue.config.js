module.exports = {
    publicPath: '/',
    devServer: {
        open: false,
        host: '127.0.0.1',
        port: '8081',
        proxy: {
            '/api': {
                target: 'http://127.0.0.1:8000',
                changeOrigin: true,
                pathRewrite:{
                    '^/api': '/'
                }
            }
        }
    }
}
