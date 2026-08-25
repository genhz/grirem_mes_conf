

    后端：
        http://gitlab.dihuait.com/ims_yyxt/aim.git
    前端：
        ​http://gitlab.dihuait.com/ims_yyxt/aim-front.git
    移动端：
        ​http://gitlab.dihuait.com/ims_yyxt/aim-mobile.git

JDK: 1.8
Maven: 3.8.4
Node: 14.21.3
Nacos: 1.2.1
Seata: 1.3.0

npm install
npm run serve

代码开发工具使用
	创建表
		创建表时复制通用字段
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
