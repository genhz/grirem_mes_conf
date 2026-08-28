# 迪华原项目开发指南

## 目录

1. [代码仓库](#代码仓库)
2. [开发环境](#开发环境)
3. [服务启动顺序](#服务启动顺序)
4. [环境配置](#环境配置)
5. [项目结构](#项目结构)
6. [开发规范](#开发规范)

---

## 代码仓库

| 项目 | 地址 |
|------|------|
| 后端 | http://gitlab.dihuait.com/ims_yyxt/aim.git |
| 前端 | http://gitlab.dihuait.com/ims_yyxt/aim-front.git |
| 移动端 | http://gitlab.dihuait.com/ims_yyxt/aim-mobile.git |

---

## 开发环境

| 组件 | 版本 |
|------|------|
| JDK | 1.8 |
| Maven | 3.8.4 |
| Node | 14.21.3 |
| Nacos | 1.2.1 |
| Seata | 1.3.0 |
| Redis | 3.0.504 |
| MySQL | 8.0+ |

---

## 服务启动顺序

**必须按以下顺序启动服务：**

```
1. Nacos (配置中心/服务发现)
2. Seata (分布式事务)
3. Redis (缓存)
4. 后端各模块
5. 前端
```

> Nacos 和 Seata 在此目录下有完整项目，直接运行即可。配置文件已在相应位置配置完成。

---

## 环境配置

### 前端/PDA 配置

```bash
# 使用 nvm 安装 node
nvm install 14.21.3
nvm use 14.21.3

# 安装依赖
npm install

# 启动开发服务器
npm run serve
```

### 后端配置

**JDK**: 1.8

**Maven**: 3.8.4
- 帆软 jar 包无法直接下载，通过更换代码仓库的文件直接配置

**Nacos**: 1.2.1
- 配置文件：`nacos/conf/application.properties`
- 由于版本过低，需要更换数据库 JDBC jar 包，更新为 MySQL 8.0 的连接驱动
- Redis 连接信息配置在 Nacos 配置中心内

**Seata**: 1.3.0
- 配置文件：`seata/conf/file.conf`

**数据库**
- 前期使用本地 MySQL 数据库
- 后期使用局域网内数据库
- 连接信息配置在 Nacos 配置中心

---

## 项目结构

### 后端模块结构

```
ims-cloud-tenant (父工程)
├── ims-commons          # 公共模块
│   ├── ims-commons-dependencies       # 依赖管理
│   ├── ims-commons-tools              # 工具类
│   ├── ims-commons-mybatis            # MyBatis 扩展
│   ├── ims-commons-security           # 安全认证
│   ├── ims-commons-log                # 日志处理
│   ├── ims-commons-swagger            # Swagger 配置
│   ├── ims-commons-lock               # 分布式锁
│   ├── ims-commons-xxl-job            # 任务调度
│   └── ims-commons-dynamic-datasource # 动态数据源
├── ims-gateway          # 网关模块
├── ims-monitor          # 监控模块
├── ims-auth             # 认证模块
├── ims-admin            # 系统管理模块
└── ims-module           # 业务模块
    ├── ims-activiti     # 工作流模块
    ├── ims-api          # API 模块
    ├── ims-seata        # Seata 事务模块
    ├── ims-devtools     # 开发工具模块
    ├── ims-message      # 消息模块
    ├── ims-job          # 任务模块
    ├── ims-xxl-job      # XXL-Job 模块
    ├── ims-md           # 物料模块
    ├── ims-om           # 订单模块
    ├── ims-mr           # 报表模块
    ├── ims-sc           # 采购模块
    ├── ims-pp           # 计划模块
    ├── ims-ap           # 应付模块
    ├── ims-es           # 工程模块
    ├── ims-qm           # 质量模块
    ├── ims-wm           # 仓库模块
    ├── ims-em           # 设备模块
    ├── ims-ur           # 用户模块
    └── ims-fr           # 财务模块
```

### 业务模块结构 (以 ims-wm 为例)

每个业务模块采用 **Client/Server 分离** 架构：

```
ims-wm/
├── ims-wm-client    # 客户端模块 (DTO、Feign 接口、枚举)
└── ims-wm-server    # 服务端模块 (Controller、Service、Dao、Entity)
```

详细结构请参考 [ARCHITECTURE.md](ARCHITECTURE.md)

---

## 开发规范

### 创建新业务

```
1. 数据库表设计 → 2. Entity 实体类 → 3. Dao 接口 → 4. XML 映射文件
       ↓
5. DTO 数据传输对象 → 6. Excel 类 → 7. Service 接口 → 8. ServiceImpl 实现
       ↓
9. Controller 控制器 → 10. Feign Client（可选）→ 11. 测试验证
```

### 代码生成

使用代码生成工具创建前后端代码：
- **功能名**: 功能名称 (汉字)
- **模块名**: 功能模块名 (例如库存管理为 wm)
- **后端路径**: `/ims-module/ims-{模块名}`
- **前端路径**: 前端项目根目录
- **子表**: 设置子表关联，子表不需要额外生成代码

### 创建菜单

- 路径为前端代码页面的路径，不需要写代码文件名

### 通用字段

创建表时复制通用字段：
- `id`, `create_date`, `creator`, `tenant_code`, `del_flag`
- `updater`, `update_date`, `import_uid`, `import_pid`, `foreign_id`

### 外键

外键统一使用 `foreign_id` 字段，不需要其他配置

---

## 非 CRUD 开发规范

### 1. Feign 跨模块调用

**核心原则：被调用方定义 Feign Client，调用方引入 client 依赖后直接注入使用。**

| 场景 | Feign Client 写在哪 | FallbackFactory 写在哪 | 调用方怎么做 |
|------|---------------------|------------------------|-------------|
| WM 调用 QM | `ims-qm-client` 中定义 | `ims-qm-client` 中定义 | WM server 的 pom.xml 引入 `ims-qm-client`，注入 `@Autowired QmXxxFeignClient` |
| QM 调用 WM | `ims-wm-client` 中定义 | `ims-wm-client` 中定义 | QM server 的 pom.xml 引入 `ims-wm-client`，注入 `@Autowired WmXxxFeignClient` |

**接口定义 (被调用方的 Client 模块)**
- 位置：`ims-xxx-client/src/main/java/io/ims/feign/`
- 注解：`@FeignClient(name = "ims-xxx-server", contextId = "xxxFeignClient", fallbackFactory = XxxFeignFallbackFactory.class)`
- 路径格式：`/模块/资源/操作`，如 `/wm/wmkc/getList`
- 返回值统一使用 `Result<T>`

**降级工厂 (被调用方的 Client 模块)**
- 位置：`ims-xxx-client/src/main/java/io/ims/feign/fallback/`
- 实现 `FallbackFactory<T>` 接口，用 `@Component` 注册
- 记录错误日志，返回友好错误提示

**消费方调用 (调用方的 Server 模块)**
- 在调用方 server 模块的 `pom.xml` 中引入提供方 client 模块依赖
- 使用 `@Autowired` 注入 Feign Client
- 始终检查 `result.getCode() != 0` 判断调用是否成功

**启动类配置**
```java
@EnableFeignClients(basePackages = {"io.ims.*"}, defaultConfiguration = FeignDefaultConfig.class)
```

### 2. 事务管理

- 使用 `@Transactional(rollbackFor = Exception.class)`
- 涉及多表操作 (主表 + 子表) 必须加事务
- 批量操作必须在事务内执行

### 3. 参数校验

```java
// Controller 层
ValidatorUtils.validateEntity(dto, AddGroup.class, DefaultGroup.class);
```

校验分组：
- `AddGroup.class` - 新增时校验
- `UpdateGroup.class` - 修改时校验
- `DefaultGroup.class` - 默认校验

### 4. 异常处理

```java
// 业务异常
throw new RenException("错误信息");
throw new RenException(ErrorCode.PARAMS_GET_ERROR, params);

// 数组判空
AssertUtils.isArrayEmpty(ids, "id");
```

### 5. 权限控制

```java
// Controller 方法
@PreAuthorize("hasAuthority('模块：资源：操作')")
// 示例
@PreAuthorize("hasAuthority('wm:wmclass:save')")
```

### 6. 操作日志

```java
// 写操作添加日志
@LogOperation("保存")
@LogOperation("修改")
@LogOperation("删除")
```

### 7. 数据权限

```java
// Controller 方法
@DataFilter

// Service 的 getWrapper() 中处理租户和删除标记
Object tenantCode = TenantContext.getTenantCode(SecurityUser.getUser());
Object delFlag = DeleteEnum.NO.value();
```

### 8. Excel 导入导出

**Excel 类定义**
```java
@Data
@ContentRowHeight(20)
@HeadRowHeight(20)
@ColumnWidth(25)
public class XxxExcel {
    @ExcelProperty(value = "列名", index = 0)
    private String field;
}
```

**导入**
```java
EasyExcel.read(file.getInputStream(), ExcelClass.class, 
    new ExcelDataListener<>(service)).sheet().doRead();
```

**导出**
```java
ExcelUtils.exportExcelToTarget(response, "标题", "sheet 名", list, ExcelClass.class);
```

### 9. 主从表 (一对多) 处理

- 子表通过 `foreign_id` 关联主表
- `get()` 时查询子表数据并 set 到 DTO 的 List 字段
- `save()/update()` 时遍历子表 List，设置 `foreignId` 后逐条保存
- `update()` 先删除旧子表数据再插入新数据

### 10. 逻辑删除

```java
// 使用逻辑删除
logicDelete(ids, Entity.class);

// 可选：同时删除子表数据
subService.deleteByForeignIds(ids);
```

### 11. Swagger 文档

```java
// Controller 类
@Api(tags = "功能名")
public class XxxController {}

// 方法
@ApiOperation("接口描述")
public Result<XxxDTO> get(@PathVariable("id") Long id) {}

// DTO 字段
@ApiModelProperty("字段说明")
private String field;
```

---

## 常用工具类

| 工具类 | 包路径 | 说明 |
|--------|--------|------|
| `Result<T>` | `io.ims.commons.tools.utils` | 统一返回结果 |
| `ConvertUtils` | `io.ims.commons.tools.utils` | 对象转换 |
| `JavaBeanUtils` | `io.ims.commons.tools.utils` | JavaBean 工具 |
| `ValidatorUtils` | `io.ims.commons.tools.validator` | 参数校验 |
| `DateUtils` | `io.ims.commons.tools.utils` | 日期工具 |
| `StringUtils` | `org.apache.commons.lang3` | 字符串工具 |
| `CollectionUtils` | `com.baomidou.mybatisplus.core.toolkit` | 集合工具 |

---

## 验证服务启动

| 服务 | 验证方式 |
|------|----------|
| Nacos | 访问 http://localhost:8848/nacos |
| 后端模块 | 查看日志，确认无 ERROR，注册到 Nacos 成功 |
| 前端 | 访问 http://localhost:8080，页面正常加载 |

---

## 相关文档

- [架构说明与开发指南](ARCHITECTURE.md) - 详细的后端项目结构和开发规范
