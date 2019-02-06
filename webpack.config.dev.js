var path = require('path');
var HtmlWebpackPlugin = require('html-webpack-plugin');

module.exports = {
    mode: 'development',


    output: {
        publicPath: '/'
    },
    resolve: {
        extensions: ['.js', '.vue']
    },
    module: {
        rules: [
            {
                test: /\.vue?$/,
                exclude: /(node_modules)/,
                use: [{
                    loader: 'vue-loader',

                    options: {
                        loaders: {
                            'scss': 'vue-style-loader!css-loader!sass-loader',
                            'sass': 'vue-style-loader!css-loader!sass-loader?indentedSyntax'
                        }
                    }
                }],
            },
            {
                test: /\.js?$/,
                exclude: /(node_modules)/,
                use: 'babel-loader'
            },
            {
                test: /\.css$/,
                use: ['style-loader', 'css-loader']
            },
            {
                test: /\.styl$/,
                loader: ['style-loader', 'css-loader', 'stylus-loader']
            },
            {
                test: /\.scss$/,
                use: [
                    {
                        loader: 'css-loader'
                    },
                    {
                        loader: 'sass-loader'
                    }
                ]
            },
            {
                test: /\.(png|jp(e*)g|svg)$/,
                use: [{
                    loader: 'url-loader',
                    options: {
                        limit: 8000, // Convert images < 8kb to base64 strings
                        name: 'images/[hash]-[name].[ext]'
                    }
                }]
            }
        ]
    },
    plugins: [new HtmlWebpackPlugin({
        template: './src/index.html'
    })],
    devServer: {
        historyApiFallback: true,
        headers: {
            'Access-Control-Allow-Origin': '*',
        },
        proxy: {
            '/api*': {
                // Forward frontend dev server request for /api to django dev server
                target: 'http://localhost:8000/',
            }
        }
    },
    externals: {
        // global app config object
        config: JSON.stringify({
            apiUrl: 'http://localhost:8000/api'
        })
    }
}
