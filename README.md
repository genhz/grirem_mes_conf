
迪华原代码仓库位置
    后端：
        http://gitlab.dihuait.com/ims_yyxt/aim.git
    前端：
        ​http://gitlab.dihuait.com/ims_yyxt/aim-front.git
    移动端：
        ​http://gitlab.dihuait.com/ims_yyxt/aim-mobile.git

开发环境
	JDK: 1.8
	Maven: 3.8.4
	Node: 14.21.3
	Nacos: 1.2.1
	Seata: 1.3.0
	Redis：3.0.504

前端/PDA配置
	使用nvm安装node 14.21.3
	npm install
	npm run serve

后端配置
	JDK: 1.8
	Maven: 3.8.4(帆软jar包无法直接下载，通过更换代码仓库的文件直接配置)
	Nacos: 1.2.1(由于版本过低，需要更换数据库JDBCjar包，更新为MySQL8.0的连接驱动)
		配置文件为“nacos/conf/application.properties”
	Seata: 1.3.0
		配置文件为“seata/conf/file.conf”


开发
	代码开发工具使用
		创建表
			创建表时复制通用字段(见数据库设计)
			外键使用foreign_id，不需要其他配置
			在页面代码生成工具、生成前后端代码、创建业务对象、创建菜单
			生成前后端代码
				功能名设置为功能名称(汉字)，模块名为功能模块名（例如库存管理为wm，这里就写wm），后端访问路径同理
				后端路径示例：/Users/genhz/Documents/code/aim/ims-module/ims-wm
				前端路径示例：/Users/genhz/Documents/code/aim-front
				设置子表，子表不需要额外生成代码
			创建菜单
				路径为前端代码页面的路径，不需要写代码文件名。

	后端跨模块接口调用
		spring cloud feign模块
