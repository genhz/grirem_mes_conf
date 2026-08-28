# 项目结构与开发指南

## 1. 核心技术栈及版本说明

### 1.1 核心框架

| 框架/组件 | 版本号 | 说明 |
|----------|--------|------|
| **Spring Boot** | 2.3.7.RELEASE | 应用基础框架 |
| **Spring Cloud** | Hoxton.SR9 | 微服务框架 |
| **Spring Cloud Alibaba** | 2.2.3.RELEASE | 阿里云微服务套件 |
| **MyBatis-Plus** | 3.3.2 | ORM 持久层框架 |
| **JDK** | 1.8 | Java 版本 |

### 1.2 关键依赖

| 依赖 | 版本号 | 说明 |
|------|--------|------|
| **MySQL Driver** | 8.0.21 | 数据库驱动 |
| **Druid** | 1.1.13 | 数据库连接池 |
| **Hutool** | 5.1.2 | Java 工具库 |
| **Lombok** | 1.18.4 | 代码简化 |
| **FastJSON** | 1.2.73 | JSON 处理 |
| **EasyExcel** | 2.2.6 | Excel 导入导出 |
| **Knife4j** | 2.0.4 | Swagger 文档增强 |
| **Hibernate Validator** | 6.0.19.Final | 参数校验 |
| **XXL-Job** | 2.1.2 | 分布式任务调度 |
| **Seata** | 1.3.0 | 分布式事务 |

### 1.3 项目模块结构

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
└── ims-module           # 业务模块（本指南重点）
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

---

## 2. `ims-module` 业务模块开发规范

### 2.1 模块结构

每个业务模块（如 `ims-wm`）采用 **Client/Server 分离** 的架构：

```
ims-wm/
├── ims-wm-client    # 客户端模块（DTO、Feign 接口、枚举）
└── ims-wm-server    # 服务端模块（Controller、Service、Dao、Entity）
```

### 2.2 包命名规范

| 包路径 | 说明 | 命名示例 |
|--------|------|----------|
| `io.ims.modules.{模块}/controller` | 控制器层 | `WmClassController` |
| `io.ims.modules.{模块}/service` | 服务接口 | `WmClassService` |
| `io.ims.modules.{模块}/service/impl` | 服务实现 | `WmClassServiceImpl` |
| `io.ims.modules.{模块}/dao` | 数据访问层 | `WmClassDao` |
| `io.ims.modules.{模块}/entity` | 实体类 | `WmClassEntity` |
| `io.ims.modules.{模块}/dto` | 数据传输对象 | `WmClassDTO` |
| `io.ims.modules.{模块}/excel` | Excel 导入导出类 | `WmClassExcel` |
| `io.ims.feign` | Feign 客户端接口 | `WmFeignClient` |
| `io.ims.feign.fallback` | Feign 降级工厂 | `WmFeignFallbackFactory` |
| `io.ims.enums` | 枚举类 | `CkdlxEnum` |

### 2.3 代码分层逻辑

```
┌─────────────────────────────────────────┐
│          Controller 层                   │
│  - 接收请求，参数校验                      │
│  - 调用 Service 处理业务                  │
│  - 返回 Result 统一响应                   │
├─────────────────────────────────────────┤
│          Service 层 (接口)               │
│  - 定义业务方法                          │
│  - 继承 CrudService 基础接口             │
├─────────────────────────────────────────┤
│          ServiceImpl 层 (实现)           │
│  - 实现业务逻辑                          │
│  - 继承 CrudServiceImpl 基础实现         │
│  - 事务控制 @Transactional              │
├─────────────────────────────────────────┤
│          Dao 层 (Mapper)                 │
│  - 继承 BaseDao 基础接口                 │
│  - 定义自定义 SQL 方法                    │
├─────────────────────────────────────────┤
│          Entity 层                       │
│  - 继承 BaseEntity 或 BaseTenantEntity   │
│  - 映射数据库表 @TableName               │
└─────────────────────────────────────────┘
```

### 2.4 统一返回结果封装

所有接口返回统一使用 `Result<T>` 包装：

```java
// 成功返回
return new Result<PageData<WmClassDTO>>().ok(page);

// 错误返回
return new Result().error("错误信息");
return new Result().error(ErrorCode.ACCOUNT_PASSWORD_ERROR);
```

**Result 常用方法：**
- `ok(T data)` - 返回成功及数据
- `error()` - 返回默认错误
- `error(int code)` - 返回指定错误码
- `error(String msg)` - 返回指定错误信息

### 2.5 异常处理机制

#### 2.5.1 异常类

```java
// 业务异常
throw new RenException("错误信息");
throw new RenException(ErrorCode.ACCOUNT_PASSWORD_ERROR);
throw new RenException(ErrorCode.PARAMS_GET_ERROR, params);
```

#### 2.5.2 错误码定义

错误码由 5 位数字组成，前 2 位为模块编码，后 3 位为业务编码：

```java
public interface ErrorCode {
    int INTERNAL_SERVER_ERROR = 500;
    int UNAUTHORIZED = 401;
    int FORBIDDEN = 403;
    
    int NOT_NULL = 10001;           // 参数为空
    int DB_RECORD_EXISTS = 10002;   // 记录已存在
    int PARAMS_GET_ERROR = 10003;   // 参数获取错误
    // ... 更多错误码
}
```

#### 2.5.3 参数校验

使用 `ValidatorUtils` 进行参数校验：

```java
// 在 Controller 中
ValidatorUtils.validateEntity(dto, AddGroup.class, DefaultGroup.class);
```

校验分组：
- `AddGroup.class` - 新增时校验
- `UpdateGroup.class` - 修改时校验
- `DefaultGroup.class` - 默认校验

---

## 3. 子模块项目结构拆解

### 3.1 完整目录结构示例（以 ims-wm 为例）

```
ims-wm/
├── pom.xml                          # 模块父 POM
├── ims-wm-client/
│   ├── pom.xml
│   └── src/main/java/io/ims/
│       ├── enums/                   # 枚举定义
│       │   ├── CkdlxEnum.java       # 出库类型枚举
│       │   ├── CrkEnums.java        # 出入库枚举
│       │   └── FhdTypeEnum.java     # 发货单类型枚举
│       ├── feign/                   # Feign 客户端
│       │   ├── WmFeignClient.java
│       │   ├── WmCkFeignClient.java
│       │   └── fallback/            # 降级工厂
│       │       ├── WmFeignFallbackFactory.java
│       │       └── WmCkFeignFallbackFactory.java
│       ├── modules/wm/dto/          # DTO 对象
│       │   ├── WmClassDTO.java
│       │   ├── WmKcDTO.java
│       │   └── WmFhdDTO.java
│       └── valid/                   # 校验分组
│           └── PrepareGroup.java
│
└── ims-wm-server/
    ├── pom.xml
    ├── db/                          # 数据库脚本
    ├── src/main/
    │   ├── java/io/ims/
    │   │   ├── WmApplication.java   # 应用入口
    │   │   ├── config/              # 配置类
    │   │   │   ├── ModuleConfigImpl.java
    │   │   │   └── ResourceServerConfig.java
    │   │   └── modules/wm/
    │   │       ├── controller/      # 控制器
    │   │       │   ├── WmClassController.java
    │   │       │   ├── WmKcController.java
    │   │       │   └── WmFhdController.java
    │   │       ├── service/         # 服务接口
    │   │       │   ├── WmClassService.java
    │   │       │   └── WmKcService.java
    │   │       ├── service/impl/    # 服务实现
    │   │       │   ├── WmClassServiceImpl.java
    │   │       │   └── WmKcServiceImpl.java
    │   │       ├── dao/             # 数据访问层
    │   │       │   ├── WmClassDao.java
    │   │       │   └── WmKcDao.java
    │   │       ├── entity/          # 实体类
    │   │       │   ├── WmClassEntity.java
    │   │       │   └── WmKcEntity.java
    │   │       └── excel/           # Excel 类
    │   │           ├── WmClassExcel.java
    │   │           └── WmKcExcel.java
    │   └── resources/
    │       ├── application.yml      # 应用配置
    │       ├── bootstrap.yml        # 启动配置
    │       ├── logback-spring.xml   # 日志配置
    │       ├── i18n/                # 国际化资源
    │       │   ├── messages.properties
    │       │   └── validation.properties
    │       └── mapper/wm/           # MyBatis XML
    │           ├── WmClassDao.xml
    │           └── WmKcDao.xml
    └── target/
```

### 3.2 各层级职责说明

| 层级 | 职责 | 继承/实现 |
|------|------|-----------|
| **Controller** | 接收 HTTP 请求、参数校验、调用 Service、返回响应 | `@RestController` |
| **Service** | 定义业务接口方法 | 继承 `CrudService<T, D>` |
| **ServiceImpl** | 实现业务逻辑、事务控制 | 继承 `CrudServiceImpl<M, T, D>` |
| **Dao** | 定义数据库操作方法 | 继承 `BaseDao<T>` |
| **Entity** | 数据库表映射实体 | 继承 `BaseTenantEntity` 或 `BaseEntity` |
| **DTO** | 数据传输对象，用于层间数据传递 | 实现 `Serializable` |
| **Excel** | Excel 导入导出字段映射 | 使用 EasyExcel 注解 |

---

## 4. Server 与 Client 模块职责说明

### 4.1 Client 模块（ims-xxx-client）

**定位：** 对外提供接口契约和数据传输对象

**职责：**
1. **DTO 定义** - 定义所有对外暴露的数据传输对象
2. **Feign 接口声明** - 定义本模块对外提供的 Feign 接口
3. **枚举定义** - 定义业务枚举类
4. **降级工厂** - 定义 Feign 调用失败时的降级逻辑

**依赖关系：**
- 仅依赖 `ims-commons-*` 基础模块
- **不依赖** 本模块的 Server 或其他业务模块的 Server

**典型代码结构：**
```java
// DTO 示例
@Data
@ApiModel(value = "班级")
public class WmClassDTO implements Serializable {
    @ApiModelProperty(value = "id")
    private Long id;
    @ApiModelProperty(value = "班级名")
    private String className;
}

// Feign Client 示例
@FeignClient(name = "ims-wm-server", contextId = "wmFeignClient", 
             fallbackFactory = WmFeignFallbackFactory.class)
public interface WmFeignClient {
    @PostMapping("/wm/wmfhd/fhdSave")
    Result fhdSave(@RequestBody WmFhdDTO dto);
    
    @GetMapping("/wm/wmkc/{id}")
    Result<WmKcDTO> get(@PathVariable("id") Long id);
}

// 降级工厂示例
@Slf4j
@Component
public class WmFeignFallbackFactory implements FallbackFactory<WmFeignClient> {
    @Override
    public WmFeignClient create(Throwable throwable) {
        log.error("{}", throwable);
        return new WmFeignClient() {
            @Override
            public Result fhdSave(WmFhdDTO dto) {
                return new Result().error();
            }
            // ... 其他方法降级实现
        };
    }
}
```

### 4.2 Server 模块（ims-xxx-server）

**定位：** 业务逻辑实现和接口暴露

**职责：**
1. **业务实现** - 实现具体的业务逻辑
2. **接口暴露** - 通过 Controller 提供 HTTP 接口
3. **Feign 实现** - 实现 Client 模块定义的 Feign 接口
4. **数据持久化** - 通过 Dao/Entity 操作数据库

**依赖关系：**
- 依赖本模块的 Client (`ims-xxx-client`)
- 依赖其他模块的 Client（用于跨模块调用）
- 依赖 `ims-commons-*` 基础模块

**典型依赖配置：**
```xml
<dependencies>
    <!-- 本模块 Client -->
    <dependency>
        <groupId>io.ims</groupId>
        <artifactId>ims-wm-client</artifactId>
        <version>${ims.cloud.version}</version>
    </dependency>
    
    <!-- 其他模块 Client（跨模块调用） -->
    <dependency>
        <groupId>io.ims</groupId>
        <artifactId>ims-pp-client</artifactId>
        <version>${ims.cloud.version}</version>
    </dependency>
    
    <!-- 公共组件 -->
    <dependency>
        <groupId>io.ims</groupId>
        <artifactId>ims-commons-mybatis</artifactId>
    </dependency>
    <dependency>
        <groupId>io.ims</groupId>
        <artifactId>ims-commons-log</artifactId>
    </dependency>
    
    <!-- Spring Cloud -->
    <dependency>
        <groupId>com.alibaba.cloud</groupId>
        <artifactId>spring-cloud-starter-alibaba-nacos-discovery</artifactId>
    </dependency>
    <dependency>
        <groupId>com.alibaba.cloud</groupId>
        <artifactId>spring-cloud-starter-alibaba-nacos-config</artifactId>
    </dependency>
</dependencies>
```

### 4.3 调用关系图

```
┌─────────────────────┐         ┌─────────────────────┐
│   消费方 Server      │         │   提供方 Server      │
│  (ims-pp-server)   │         │  (ims-wm-server)   │
│                     │         │                     │
│  @Autowired         │         │  @RestController    │
│  WmFeignClient      │────────▶│  WmClassController  │
│                     │  HTTP   │                     │
└─────────────────────┘         └─────────────────────┘
         ▲                                ▲
         │                                │
         │ 依赖                           │ 实现
         │                                │
┌────────┴────────┐              ┌────────┴────────┐
│  ims-wm-client  │              │  ims-wm-client  │
│  (Feign 接口定义) │              │  (DTO 定义)      │
└─────────────────┘              └─────────────────┘
```

---

## 5. 标准的 CRUD 开发流程

### 5.1 开发步骤概览

```
1. 数据库表设计 → 2. Entity 实体类 → 3. Dao 接口 → 4. XML 映射文件
       ↓
5. DTO 数据传输对象 → 6. Excel 类 → 7. Service 接口 → 8. ServiceImpl 实现
       ↓
9. Controller 控制器 → 10. Feign Client（可选）→ 11. 测试验证
```

### 5.2 第一步：数据库表设计

```sql
CREATE TABLE `wm_class` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT COMMENT 'id',
  `create_date` datetime DEFAULT NULL COMMENT '创建时间',
  `creator` bigint(20) DEFAULT NULL COMMENT '创建者',
  `tenant_code` bigint(20) DEFAULT NULL COMMENT '租户编码',
  `del_flag` int(11) DEFAULT '0' COMMENT '删除标识',
  `updater` bigint(20) DEFAULT NULL COMMENT '修改人',
  `update_date` datetime DEFAULT NULL COMMENT '修改时间',
  `import_uid` varchar(50) DEFAULT NULL COMMENT '导入唯一标识',
  `import_pid` varchar(50) DEFAULT NULL COMMENT '导入父级标识',
  `foreign_id` bigint(20) DEFAULT NULL COMMENT '外键 ID',
  `class_name` varchar(100) DEFAULT NULL COMMENT '班级名',
  `kemu` varchar(50) DEFAULT NULL COMMENT '科目',
  PRIMARY KEY (`id`),
  KEY `tenant_code` (`tenant_code`),
  KEY `del_flag` (`del_flag`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='班级';
```

### 5.3 第二步：Entity 实体类

**位置：** `ims-xxx-server/src/main/java/io/ims/modules/{模块}/entity/`

```java
package io.ims.modules.wm.entity;

import lombok.Data;
import lombok.EqualsAndHashCode;
import com.baomidou.mybatisplus.annotation.*;
import java.util.Date;
import io.ims.commons.mybatis.entity.BaseEntity;

/**
 * 班级
 * @author genhz genhz@foxmail.com
 * @since 1.0 2026-08-25
 */
@Data
@EqualsAndHashCode(callSuper=false)
@TableName("wm_class")
public class WmClassEntity extends BaseEntity {
    private static final long serialVersionUID = 1L;

    /**
     * 租户编码
     */
    @TableField(fill = FieldFill.INSERT)
    private Long tenantCode;
    
    /**
     * 删除标识
     */
    private Integer delFlag;
    
    /**
     * 修改人
     */
    @TableField(fill = FieldFill.INSERT_UPDATE)
    private Long updater;
    
    /**
     * 修改时间
     */
    @TableField(fill = FieldFill.INSERT_UPDATE)
    private Date updateDate;
    
    /**
     * 导入唯一标识
     */
    private String importUid;
    
    /**
     * 导入父级标识
     */
    private String importPid;
    
    private Long foreignId;
    
    /**
     * 班级名
     */
    private String className;
    
    /**
     * 科目
     */
    private String kemu;
}
```

**关键点：**
- 继承 `BaseEntity`（不含租户）或 `BaseTenantEntity`（含租户）
- 使用 `@TableName` 指定表名
- 使用 `@TableField(fill = FieldFill.INSERT)` 自动填充字段
- 使用 `@TableField(fill = FieldFill.INSERT_UPDATE)` 自动填充更新字段

### 5.4 第三步：Dao 接口

**位置：** `ims-xxx-server/src/main/java/io/ims/modules/{模块}/dao/`

```java
package io.ims.modules.wm.dao;

import io.ims.commons.mybatis.dao.BaseDao;
import io.ims.modules.wm.entity.WmClassEntity;
import org.apache.ibatis.annotations.Mapper;

/**
 * 班级
 * @author genhz genhz@foxmail.com
 * @since 1.0 2026-08-25
 */
@Mapper
public interface WmClassDao extends BaseDao<WmClassEntity> {

    /**
     * 根据外键 id，删除表数据
     */
    void deleteByForeignIds(Long[] foreignIds);

    /**
     * 恢复数据
     */
    void recovery(String ids);
}
```

**关键点：**
- 继承 `BaseDao<T>`（实际是 `BaseMapper<T>` 的别名）
- 使用 `@Mapper` 注解
- 自定义方法在 XML 中实现

### 5.5 第四步：MyBatis XML 映射文件

**位置：** `ims-xxx-server/src/main/resources/mapper/{模块}/`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE mapper PUBLIC "-//mybatis.org//DTD Mapper 3.0//EN" 
    "http://mybatis.org/dtd/mybatis-3-mapper.dtd">

<mapper namespace="io.ims.modules.wm.dao.WmClassDao">

    <resultMap type="io.ims.modules.wm.entity.WmClassEntity" id="wmClassMap">
        <result property="id" column="id"/>
        <result property="createDate" column="create_date"/>
        <result property="creator" column="creator"/>
        <result property="tenantCode" column="tenant_code"/>
        <result property="delFlag" column="del_flag"/>
        <result property="updater" column="updater"/>
        <result property="updateDate" column="update_date"/>
        <result property="importUid" column="import_uid"/>
        <result property="importPid" column="import_pid"/>
        <result property="foreignId" column="foreign_id"/>
        <result property="className" column="class_name"/>
        <result property="kemu" column="kemu"/>
    </resultMap>

    <!-- 自定义删除方法 -->
    <delete id="deleteByForeignIds">
        delete from wm_class where foreign_id in
        <foreach item="foreignId" collection="array" open="(" separator="," close=")">
            #{foreignId}
        </foreach>
    </delete>

    <!-- 自定义恢复方法 -->
    <update id="recovery">
        update wm_class set del_flag = 0 where id in (${ids})
    </update>
</mapper>
```

**关键点：**
- `namespace` 指向 Dao 接口全限定名
- `resultMap` 定义字段映射关系（驼峰转下划线）
- 自定义 SQL 在 `<mapper>` 标签内定义

### 5.6 第五步：DTO 数据传输对象

**位置：** `ims-xxx-client/src/main/java/io/ims/modules/{模块}/dto/`

```java
package io.ims.modules.wm.dto;

import com.fasterxml.jackson.annotation.JsonFormat;
import io.swagger.annotations.ApiModel;
import io.swagger.annotations.ApiModelProperty;
import lombok.Data;

import java.io.Serializable;
import java.util.Date;
import java.util.List;

/**
 * 班级
 * @author genhz genhz@foxmail.com
 * @since 1.0 2026-08-25
 */
@Data
@ApiModel(value = "班级")
public class WmClassDTO implements Serializable {
    private static final long serialVersionUID = 1L;

    @ApiModelProperty(value = "id")
    private Long id;
    
    @ApiModelProperty(value = "创建时间")
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss", timezone = "GMT+8")
    private Date createDate;
    
    @ApiModelProperty(value = "创建者")
    private Long creator;
    
    @ApiModelProperty(value = "租户编码")
    private Long tenantCode;
    
    @ApiModelProperty(value = "删除标识")
    private Integer delFlag;
    
    @ApiModelProperty(value = "修改人")
    private Long updater;
    
    @ApiModelProperty(value = "修改时间")
    @JsonFormat(pattern = "yyyy-MM-dd HH:mm:ss", timezone = "GMT+8")
    private Date updateDate;
    
    @ApiModelProperty(value = "导入唯一标识")
    private String importUid;
    
    @ApiModelProperty(value = "导入父级标识")
    private String importPid;
    
    private Long foreignId;
    
    @ApiModelProperty(value = "班级名")
    private String className;
    
    @ApiModelProperty(value = "科目")
    private String kemu;
    
    @ApiModelProperty(value = "学生列表")
    private List<WmClassStuDTO> wmClassStuList;
}
```

**关键点：**
- 实现 `Serializable` 接口
- 使用 `@ApiModelProperty` 添加 Swagger 文档说明
- 日期字段使用 `@JsonFormat` 格式化
- 可包含子对象列表（一对多关系）

### 5.7 第六步：Excel 导入导出类

**位置：** `ims-xxx-server/src/main/java/io/ims/modules/{模块}/excel/`

```java
package io.ims.modules.wm.excel;

import com.alibaba.excel.annotation.format.DateTimeFormat;
import com.alibaba.excel.annotation.ExcelProperty;
import com.alibaba.excel.annotation.write.style.ColumnWidth;
import com.alibaba.excel.annotation.write.style.ContentRowHeight;
import com.alibaba.excel.annotation.write.style.HeadRowHeight;
import lombok.Data;

import java.util.Date;

/**
 * 班级
 * @author genhz genhz@foxmail.com
 * @since 1.0 2026-08-25
 */
@Data
@ContentRowHeight(20)
@HeadRowHeight(20)
@ColumnWidth(25)
public class WmClassExcel {
    
    @ExcelProperty(value = "班级名", index = 0)
    private String className;
    
    @ExcelProperty(value = "科目", index = 1)
    private String kemu;
}
```

**关键点：**
- 使用 EasyExcel 注解
- `@ExcelProperty` 指定列名和索引
- `@ColumnWidth` 设置列宽
- `@ContentRowHeight` 和 `@HeadRowHeight` 设置行高

### 5.8 第七步：Service 接口

**位置：** `ims-xxx-server/src/main/java/io/ims/modules/{模块}/service/`

```java
package io.ims.modules.wm.service;

import io.ims.commons.mybatis.service.CrudService;
import io.ims.modules.wm.dto.WmClassDTO;
import io.ims.modules.wm.entity.WmClassEntity;
import java.util.*;

/**
 * 班级
 * @author genhz genhz@foxmail.com
 * @since 1.0 2026-08-25
 */
public interface WmClassService extends CrudService<WmClassEntity, WmClassDTO> {

    /**
     * 根据外键 ID 删除
     */
    void deleteByForeignIds(Long[] foreignIds);

    /**
     * 根据外键查询列表
     */
    List<WmClassDTO> getList(Long foreignId);

    /**
     * 恢复数据
     */
    void recovery(Long[] ids);

    /**
     * Excel 导入
     */
    void importExcel(HashMap map);
}
```

**关键点：**
- 继承 `CrudService<Entity, DTO>`
- 泛型 1：Entity 实体类
- 泛型 2：DTO 数据传输对象
- 定义自定义业务方法

### 5.9 第八步：ServiceImpl 实现类

**位置：** `ims-xxx-server/src/main/java/io/ims/modules/{模块}/service/impl/`

```java
package io.ims.modules.wm.service.impl;

import com.baomidou.mybatisplus.core.conditions.query.QueryWrapper;
import io.ims.commons.mybatis.service.impl.CrudServiceImpl;
import io.ims.commons.security.context.TenantContext;
import io.ims.commons.security.user.SecurityUser;
import io.ims.commons.tools.utils.ConvertUtils;
import io.ims.commons.tools.utils.JavaBeanUtils;
import io.ims.modules.wm.dao.WmClassDao;
import io.ims.modules.wm.dto.WmClassDTO;
import io.ims.modules.wm.entity.WmClassEntity;
import io.ims.modules.wm.service.WmClassService;
import io.ims.modules.wm.dto.WmClassStuDTO;
import io.ims.modules.wm.service.WmClassStuService;
import org.springframework.beans.factory.annotation.Autowired;
import org.apache.commons.lang3.StringUtils;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.*;
import com.baomidou.mybatisplus.core.toolkit.CollectionUtils;
import io.ims.commons.tools.enums.DeleteEnum;

/**
 * 班级
 * @author genhz genhz@foxmail.com
 * @since 1.0 2026-08-25
 */
@Service
public class WmClassServiceImpl extends CrudServiceImpl<WmClassDao, WmClassEntity, WmClassDTO> 
    implements WmClassService {
    
    @Autowired
    private WmClassStuService wmClassStuService;

    /**
     * 构建查询条件
     */
    @Override
    public QueryWrapper<WmClassEntity> getWrapper(Map<String, Object> params) {
        // 处理租户
        Object tenantCode = params.get("tenantCode");
        tenantCode = tenantCode == null || tenantCode.equals("") 
            ? TenantContext.getTenantCode(SecurityUser.getUser()) : tenantCode;
        params.put("tenantCode", tenantCode);
        
        // 处理删除标记
        Object delFlag = params.get("delFlag");
        delFlag = delFlag == null ? DeleteEnum.NO.value() : delFlag;
        params.put("delFlag", delFlag);
        
        QueryWrapper<WmClassEntity> wrapper = JavaBeanUtils.getWrapper(WmClassEntity.class, params);
        return wrapper;
    }

    /**
     * 查询详情（包含子表数据）
     */
    @Override
    public WmClassDTO get(Long id) {
        WmClassDTO dto = super.get(id);
        
        // 获取学生子表数据
        List<WmClassStuDTO> wmClassStuList = wmClassStuService.getList(id);
        dto.setWmClassStuList(wmClassStuList);
        
        return dto;
    }

    /**
     * 保存（包含子表数据）
     */
    @Override
    @Transactional
    public void save(WmClassDTO dto) {
        dto.setDelFlag(DeleteEnum.NO.value());
        super.save(dto);
        
        // 保存学生子表数据
        if (CollectionUtils.isNotEmpty(dto.getWmClassStuList())) {
            for (WmClassStuDTO subDto : dto.getWmClassStuList()) {
                subDto.setForeignId(dto.getId());
                subDto.setId(null);
                wmClassStuService.save(subDto);
            }
        }
    }

    /**
     * 更新（包含子表数据）
     */
    @Override
    @Transactional
    public void update(WmClassDTO dto) {
        super.update(dto);
        
        // 更新学生子表数据
        wmClassStuService.deleteByForeignIds(new Long[]{dto.getId()});
        if (CollectionUtils.isNotEmpty(dto.getWmClassStuList())) {
            for (WmClassStuDTO subDto : dto.getWmClassStuList()) {
                subDto.setForeignId(dto.getId());
                subDto.setId(null);
                wmClassStuService.save(subDto);
            }
        }
    }

    /**
     * 删除（逻辑删除）
     */
    @Override
    @Transactional
    public void delete(Long[] ids) {
        // 使用逻辑删除
        logicDelete(ids, WmClassEntity.class);
        
        // 可选：同时删除子表数据
        // wmClassStuService.deleteByForeignIds(ids);
    }

    /**
     * 恢复数据
     */
    @Override
    @Transactional(rollbackFor = Exception.class)
    public void recovery(Long[] ids) {
        String idsStr = "";
        for (long id : ids) {
            idsStr += "," + id;
        }
        baseDao.recovery(idsStr.substring(1));
    }

    /**
     * 根据外键删除
     */
    @Override
    public void deleteByForeignIds(Long[] foreignIds) {
        baseDao.deleteByForeignIds(foreignIds);
    }

    /**
     * 根据外键查询列表
     */
    @Override
    public List<WmClassDTO> getList(Long foreignId) {
        QueryWrapper<WmClassEntity> query = new QueryWrapper<>();
        query.eq("foreign_id", foreignId);
        List<WmClassEntity> list = baseDao.selectList(query);
        
        return ConvertUtils.sourceToTarget(list, WmClassDTO.class);
    }

    /**
     * Excel 导入
     */
    @Override
    @Transactional(rollbackFor = Exception.class)
    public void importExcel(HashMap map) {
        Collection<WmClassEntity> entityList = (Collection<WmClassEntity>) map.get("list");
        int isCover = (int) map.get("isCover");
        
        // 实现导入逻辑（新增或覆盖）
        // ...
        
        if (!updateList.isEmpty())
            updateBatchById(updateList);
        if (!insertList.isEmpty())
            insertBatch(insertList);
    }
}
```

**关键点：**
- 继承 `CrudServiceImpl<Dao, Entity, DTO>`
- 实现 `getWrapper()` 方法构建查询条件
- 使用 `@Transactional` 管理事务
- 使用 `baseDao` 访问 Dao 层
- 使用 `ConvertUtils.sourceToTarget()` 进行对象转换

### 5.10 第九步：Controller 控制器

**位置：** `ims-xxx-server/src/main/java/io/ims/modules/{模块}/controller/`

```java
package io.ims.modules.wm.controller;

import com.alibaba.excel.EasyExcel;
import io.ims.commons.log.annotation.LogOperation;
import io.ims.commons.tools.constant.Constant;
import io.ims.commons.tools.page.PageData;
import io.ims.commons.tools.utils.Result;
import io.ims.commons.tools.utils.ExcelUtils;
import io.ims.commons.tools.validator.AssertUtils;
import io.ims.commons.tools.validator.ValidatorUtils;
import io.ims.commons.tools.validator.group.AddGroup;
import io.ims.commons.tools.validator.group.DefaultGroup;
import io.ims.commons.tools.validator.group.UpdateGroup;
import io.ims.modules.wm.dto.WmClassDTO;
import io.ims.modules.wm.excel.WmClassExcel;
import io.ims.modules.wm.service.WmClassService;
import io.ims.modules.wm.excel.listener.ExcelDataListener;
import io.swagger.annotations.Api;
import io.swagger.annotations.ApiImplicitParam;
import io.swagger.annotations.ApiImplicitParams;
import io.swagger.annotations.ApiOperation;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;
import springfox.documentation.annotations.ApiIgnore;
import org.springframework.web.multipart.MultipartFile;

import javax.servlet.http.HttpServletResponse;
import java.util.*;
import io.ims.commons.tools.enums.DeleteEnum;
import io.ims.commons.mybatis.annotation.DataFilter;

/**
 * 班级
 * @author genhz genhz@foxmail.com
 * @since 1.0 2026-08-25
 */
@RestController
@RequestMapping("wmclass")
@Api(tags = "班级")
public class WmClassController {
    
    @Autowired
    private WmClassService wmClassService;
    
    /**
     * 分页查询
     */
    @GetMapping("page")
    @ApiOperation("分页")
    @ApiImplicitParams({
        @ApiImplicitParam(name = Constant.PAGE, value = "当前页码，从 1 开始", paramType = "query", required = true, dataType = "int"),
        @ApiImplicitParam(name = Constant.LIMIT, value = "每页显示记录数", paramType = "query", required = true, dataType = "int"),
        @ApiImplicitParam(name = Constant.ORDER_FIELD, value = "排序字段", paramType = "query", dataType = "String"),
        @ApiImplicitParam(name = Constant.ORDER, value = "排序方式，可选值 (asc、desc)", paramType = "query", dataType = "String")
    })
    @PreAuthorize("hasAuthority('wm:wmclass:page')")
    @DataFilter
    public Result<PageData<WmClassDTO>> page(@ApiIgnore @RequestParam Map<String, Object> params) {
        PageData<WmClassDTO> page = wmClassService.page(params);
        return new Result<PageData<WmClassDTO>>().ok(page);
    }

    /**
     * 查询详情
     */
    @GetMapping("{id}")
    @ApiOperation("信息")
    @PreAuthorize("hasAuthority('wm:wmclass:info')")
    public Result<WmClassDTO> get(@PathVariable("id") Long id) {
        WmClassDTO data = wmClassService.get(id);
        return new Result<WmClassDTO>().ok(data);
    }

    /**
     * 保存
     */
    @PostMapping
    @ApiOperation("保存")
    @LogOperation("保存")
    @PreAuthorize("hasAuthority('wm:wmclass:save')")
    public Result<WmClassDTO> save(@RequestBody WmClassDTO dto) {
        dto.setDelFlag(DeleteEnum.NO.value());
        // 效验数据
        ValidatorUtils.validateEntity(dto, AddGroup.class, DefaultGroup.class);
        
        wmClassService.save(dto);
        
        return new Result<WmClassDTO>().ok(dto);
    }

    /**
     * 修改
     */
    @PutMapping
    @ApiOperation("修改")
    @LogOperation("修改")
    @PreAuthorize("hasAuthority('wm:wmclass:update')")
    public Result<WmClassDTO> update(@RequestBody WmClassDTO dto) {
        // 效验数据
        ValidatorUtils.validateEntity(dto, UpdateGroup.class, DefaultGroup.class);
        
        wmClassService.update(dto);
        
        return new Result<WmClassDTO>().ok(dto);
    }

    /**
     * 删除
     */
    @DeleteMapping
    @ApiOperation("删除")
    @LogOperation("删除")
    @PreAuthorize("hasAuthority('wm:wmclass:delete')")
    public Result delete(@RequestBody Long[] ids) {
        // 效验数据
        AssertUtils.isArrayEmpty(ids, "id");
        
        wmClassService.delete(ids);
        
        return new Result();
    }

    /**
     * 导入
     */
    @PostMapping("import")
    @ApiOperation("导入")
    @PreAuthorize("hasAuthority('wm:wmclass:import')")
    @ApiImplicitParam(name = "file", value = "文件", paramType = "query", dataType = "file")
    public Result importExcel(@RequestParam("file") MultipartFile file) {
        try {
            // 解析并保存到数据库
            EasyExcel.read(file.getInputStream(), WmClassExcel.class, 
                new ExcelDataListener<>(wmClassService)).sheet().doRead();
        } catch (Exception e) {
            return new Result().error(e.getMessage());
        }
        return new Result();
    }

    /**
     * 导出
     */
    @GetMapping("export")
    @ApiOperation("导出")
    @LogOperation("导出")
    @PreAuthorize("hasAuthority('wm:wmclass:export')")
    public void export(@ApiIgnore @RequestParam Map<String, Object> params, HttpServletResponse response) throws Exception {
        List<WmClassDTO> list = wmClassService.list(params);
        ExcelUtils.exportExcelToTarget(response, "班级", "班级", list, WmClassExcel.class);
    }

    /**
     * 导出模板
     */
    @GetMapping("exportM")
    @ApiOperation("导出模板")
    @LogOperation("导出模板")
    @PreAuthorize("hasAuthority('wm:wmclass:export')")
    public void exportM(@ApiIgnore @RequestParam Map<String, Object> params, HttpServletResponse response) throws Exception {
        List list = new ArrayList();
        ExcelUtils.exportExcelToTarget(response, "班级-Excel 模板", "班级", list, WmClassExcel.class);
    }

    /**
     * 获取列表（无条件）
     */
    @GetMapping("getList")
    @ApiOperation("获取列表")
    @ApiImplicitParams({
        @ApiImplicitParam(name = "className", value = "班级名", paramType = "query", dataType = "String"),
        @ApiImplicitParam(name = "kemu", value = "科目", paramType = "query", dataType = "String"),
        @ApiImplicitParam(name = "id", value = "id", paramType = "query", dataType = "Long")
    })
    public Result<List<WmClassDTO>> getList(@ApiIgnore @RequestParam Map<String, Object> params) throws Exception {
        List<WmClassDTO> list = wmClassService.list(params);
        return new Result<List<WmClassDTO>>().ok(list);
    }
}
```

**关键点：**
- 使用 `@RestController` 和 `@RequestMapping` 定义路由
- 使用 `@Api` 和 `@ApiOperation` 添加 Swagger 文档
- 使用 `@PreAuthorize` 进行权限控制
- 使用 `@LogOperation` 记录操作日志
- 使用 `@DataFilter` 进行数据权限过滤
- 使用 `ValidatorUtils` 进行参数校验
- 统一返回 `Result<T>`

### 5.11 CRUD 方法继承关系一览

| 方法 | 来源 | 说明 |
|------|------|------|
| `page(params)` | `CrudServiceImpl` | 分页查询 |
| `list(params)` | `CrudServiceImpl` | 列表查询 |
| `get(id)` | `CrudServiceImpl` | 查询详情 |
| `lock(id)` | `CrudServiceImpl` | 悲观锁查询 |
| `save(dto)` | `CrudServiceImpl` | 保存 |
| `update(dto)` | `CrudServiceImpl` | 更新 |
| `delete(ids)` | `CrudServiceImpl` | 删除 |
| `insert(entity)` | `BaseServiceImpl` | 插入实体 |
| `insertBatch(entityList)` | `BaseServiceImpl` | 批量插入 |
| `updateById(entity)` | `BaseServiceImpl` | 根据 ID 更新 |
| `updateBatchById(entityList)` | `BaseServiceImpl` | 批量更新 |
| `selectById(id)` | `BaseServiceImpl` | 根据 ID 查询 |
| `deleteById(id)` | `BaseServiceImpl` | 根据 ID 删除 |
| `logicDelete(ids, entity)` | `BaseServiceImpl` | 逻辑删除 |

---

## 6. 跨模块 Feign Client 调用规范

### 6.1 核心原则

**Feign Client 归属规则：被调用方定义 Feign Client，调用方引入 client 依赖后直接注入使用。**

| 场景 | Feign Client 写在哪 | FallbackFactory 写在哪 | 调用方怎么做 |
|------|---------------------|------------------------|-------------|
| WM 调用 QM | `ims-qm-client` 中定义 | `ims-qm-client` 中定义 | WM server 的 pom.xml 引入 `ims-qm-client`，注入 `@Autowired QmXxxFeignClient` |
| QM 调用 WM | `ims-wm-client` 中定义 | `ims-wm-client` 中定义 | QM server 的 pom.xml 引入 `ims-wm-client`，注入 `@Autowired WmXxxFeignClient` |
| PP 调用 WM | `ims-wm-client` 中定义 | `ims-wm-client` 中定义 | PP server 的 pom.xml 引入 `ims-wm-client`，注入 `@Autowired WmXxxFeignClient` |

### 6.2 Feign 接口定义（被调用方的 Client 模块）

**位置：** `ims-xxx-client/src/main/java/io/ims/feign/`（xxx 为**被调用方**模块名）

```java
package io.ims.feign;

import io.ims.commons.tools.utils.Result;
import io.ims.feign.fallback.WmFeignFallbackFactory;
import io.ims.modules.wm.dto.*;
import org.springframework.cloud.openfeign.FeignClient;
import org.springframework.web.bind.annotation.*;
import springfox.documentation.annotations.ApiIgnore;

import java.math.BigDecimal;
import java.util.List;
import java.util.Map;

/**
 * 仓库模块 Feign 客户端 - 由 WM 模块定义，供其他模块调用
 */
@FeignClient(name = "ims-wm-server", contextId = "wmFeignClient", 
             fallbackFactory = WmFeignFallbackFactory.class)
public interface WmFeignClient {
    
    /**
     * 新增发货单
     */
    @PostMapping("/wm/wmfhd/fhdSave")
    Result fhdSave(@RequestBody WmFhdDTO dto);

    /**
     * 新增出入库单
     */
    @PostMapping("/wm/wmcrk")
    Result save(WmCrkDTO dto);

    /**
     * 查询库存详情
     */
    @GetMapping("/wm/wmkc/{id}")
    Result<WmKcDTO> get(@PathVariable("id") Long id);

    /**
     * 更新库存
     */
    @PutMapping("/wm/wmkc")
    Result update(@RequestBody WmKcDTO dto);

    /**
     * 查询库存列表
     */
    @GetMapping("/wm/wmkc/getList")
    Result<List<WmKcDTO>> getKcList(@ApiIgnore @RequestParam Map<String, Object> params);

    /**
     * 物料分拆
     */
    @PostMapping("/wm/wmkc/materialSplit")
    Result materialSplit(@RequestBody Map<String, Object> params);
}
```

**关键点：**
- 使用 `@FeignClient` 注解，指定服务名和降级工厂
- 接口方法使用 Spring MVC 注解（`@PostMapping`, `@GetMapping` 等）
- 参数使用 `@RequestBody` 或 `@RequestParam` 明确标注
- 返回值统一使用 `Result<T>` 包装
- **Feign Client 由被调用方（服务提供方）定义在它的 client 模块中**

### 6.3 Feign 降级工厂（被调用方的 Client 模块）

**位置：** `ims-xxx-client/src/main/java/io/ims/feign/fallback/`（xxx 为**被调用方**模块名）

```java
package io.ims.feign.fallback;

import feign.hystrix.FallbackFactory;
import io.ims.commons.tools.utils.Result;
import io.ims.feign.WmFeignClient;
import io.ims.modules.wm.dto.*;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;

import java.math.BigDecimal;
import java.util.List;
import java.util.Map;

/**
 * Feign 降级工厂
 */
@Slf4j
@Component
public class WmFeignFallbackFactory implements FallbackFactory<WmFeignClient> {
    
    @Override
    public WmFeignClient create(Throwable throwable) {
        log.error("Feign 调用失败：{}", throwable.getMessage(), throwable);
        
        return new WmFeignClient() {
            @Override
            public Result fhdSave(WmFhdDTO dto) {
                return new Result().error("服务暂时不可用，请稍后重试");
            }

            @Override
            public Result save(WmCrkDTO dto) {
                return new Result().error("服务暂时不可用，请稍后重试");
            }

            @Override
            public Result<WmKcDTO> get(Long id) {
                return new Result().error("服务暂时不可用，请稍后重试");
            }

            @Override
            public Result update(WmKcDTO dto) {
                return new Result().error("服务暂时不可用，请稍后重试");
            }

            @Override
            public Result<List<WmKcDTO>> getKcList(Map<String, Object> params) {
                return new Result().error("服务暂时不可用，请稍后重试");
            }

            @Override
            public Result materialSplit(Map<String, Object> params) {
                return new Result().error("服务暂时不可用，请稍后重试");
            }
        };
    }
}
```

**关键点：**
- 实现 `FallbackFactory<T>` 接口
- 使用 `@Slf4j` 记录错误日志
- 使用 `@Component` 注册为 Spring Bean
- 降级方法返回默认值或友好错误提示

### 6.4 消费方调用示例（调用方的 Server 模块）

**场景：** 在生产模块 (`ims-pp-server`) 中调用仓库模块的 Feign 接口

**前提：** 在 `ims-pp-server/pom.xml` 中引入 `ims-wm-client` 依赖（见 6.5 节）

```java
package io.ims.modules.pp.service.impl;

import io.ims.commons.tools.utils.Result;
import io.ims.feign.WmFeignClient;
import io.ims.modules.pp.dto.ProductionOrderDTO;
import io.ims.modules.pp.service.ProductionOrderService;
import io.ims.modules.wm.dto.WmKcDTO;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * 生产订单服务实现
 */
@Service
public class ProductionOrderServiceImpl implements ProductionOrderService {
    
    @Autowired
    private WmFeignClient wmFeignClient;  // 注入 Feign 客户端
    
    /**
     * 查询库存
     */
    @Override
    public WmKcDTO getKcInfo(Long kcId) {
        Result<WmKcDTO> result = wmFeignClient.get(kcId);
        
        // 检查调用结果
        if (result == null || result.getCode() != 0) {
            throw new RuntimeException("查询库存失败：" + (result != null ? result.getMsg() : "未知错误"));
        }
        
        return result.getData();
    }
    
    /**
     * 查询库存列表
     */
    @Override
    public List<WmKcDTO> getKcList(String fwltm) {
        Map<String, Object> params = new HashMap<>();
        params.put("fwltm", fwltm);
        
        Result<List<WmKcDTO>> result = wmFeignClient.getKcList(params);
        
        if (result == null || result.getCode() != 0) {
            throw new RuntimeException("查询库存列表失败：" + (result != null ? result.getMsg() : "未知错误"));
        }
        
        return result.getData();
    }
    
    /**
     * 物料分拆
     */
    @Override
    public void materialSplit(Long kcId, BigDecimal splitQty) {
        Map<String, Object> params = new HashMap<>();
        params.put("kcId", kcId);
        params.put("splitQty", splitQty);
        
        Result result = wmFeignClient.materialSplit(params);
        
        if (result == null || result.getCode() != 0) {
            throw new RuntimeException("物料分拆失败：" + (result != null ? result.getMsg() : "未知错误"));
        }
    }
}
```

**关键点：**
- 使用 `@Autowired` 注入 Feign 客户端
- 检查 `Result.code == 0` 判断调用是否成功
- 处理降级返回的错误信息
- 抛出业务异常时包含详细错误信息

### 6.5 依赖配置（调用方 Server 模块）

在调用方 Server 模块的 `pom.xml` 中添加依赖（引入**被调用方**的 client 模块）：

```xml
<dependencies>
    <!-- 引入提供方 Client 模块 -->
    <dependency>
        <groupId>io.ims</groupId>
        <artifactId>ims-wm-client</artifactId>
        <version>${ims.cloud.version}</version>
        <exclusions>
            <exclusion>
                <groupId>io.github.openfeign</groupId>
                <artifactId>feign-httpclient</artifactId>
            </exclusion>
        </exclusions>
    </dependency>
    
    <!-- Feign HTTP Client（版本统一管理） -->
    <dependency>
        <groupId>io.github.openfeign</groupId>
        <artifactId>feign-httpclient</artifactId>
        <version>10.10.1</version>
    </dependency>
    
    <!-- 其他依赖... -->
</dependencies>
```

### 6.6 启动类配置

确保**调用方**启动类已启用 Feign：

```java
@SpringBootApplication
@EnableDiscoveryClient
@EnableFeignClients(basePackages = {"io.ims.*"}, defaultConfiguration = FeignDefaultConfig.class)
public class PpApplication {
    public static void main(String[] args) {
        SpringApplication.run(PpApplication.class, args);
    }
}
```

**关键点：**
- `@EnableFeignClients` 启用 Feign 客户端扫描
- `basePackages` 指定扫描包路径
- `defaultConfiguration` 指定默认配置类

### 6.7 调用流程图

```
┌─────────────────────────────────────────────────────────────────┐
│                        消费方 (ims-pp-server)                    │
│                                                                  │
│  ┌──────────────────┐                                           │
│  │ ProductionOrder  │                                           │
│  │ Controller       │                                           │
│  └────────┬─────────┘                                           │
│           │                                                      │
│           ▼                                                      │
│  ┌──────────────────┐                                           │
│  │ ProductionOrder  │                                           │
│  │ ServiceImpl      │                                           │
│  └────────┬─────────┘                                           │
│           │                                                      │
│           │ @Autowired                                           │
│           ▼                                                      │
│  ┌──────────────────┐                                           │
│  │ WmFeignClient    │ (Feign 接口，定义在 ims-wm-client)          │
│  └────────┬─────────┘                                           │
└───────────┼──────────────────────────────────────────────────────┘
            │
            │ HTTP (通过 Nacos 发现服务)
            │ Content-Type: application/json
            ▼
┌─────────────────────────────────────────────────────────────────┐
│                        提供方 (ims-wm-server)                    │
│                                                                  │
│  ┌──────────────────┐                                           │
│  │ WmKcController   │                                           │
│  └────────┬─────────┘                                           │
│           │                                                      │
│           ▼                                                      │
│  ┌──────────────────┐                                           │
│  │ WmKcService      │                                           │
│  └────────┬─────────┘                                           │
│           │                                                      │
│           ▼                                                      │
│  ┌──────────────────┐                                           │
│  │ WmKcDao          │                                           │
│  └────────┬─────────┘                                           │
│           │                                                      │
│           ▼                                                      │
│  ┌──────────────────┐                                           │
│  │ wm_kc (数据库表)  │                                           │
│  └──────────────────┘                                           │
└─────────────────────────────────────────────────────────────────┘
```

### 6.8 最佳实践

1. **接口命名规范**
   - Feign 接口路径使用 `/模块/资源/操作` 格式
   - 例如：`/wm/wmkc/getList`, `/wm/wmfhd/fhdSave`

2. **参数传递规范**
   - 单个对象参数使用 `@RequestBody`
   - 多个简单参数使用 `@RequestParam`
   - 复杂查询条件使用 `Map<String, Object>`

3. **错误处理规范**
   - 始终检查 `Result.code`
   - 降级工厂返回友好错误提示
   - 记录详细错误日志

4. **版本兼容**
   - 新增接口时保持向后兼容
   - 不随意修改已有接口参数
   - 必要时使用版本号区分

5. **性能优化**
   - 避免频繁调用 Feign 接口
   - 批量查询使用批量接口
   - 考虑添加本地缓存

---

## 附录

### A. 常用工具类

| 工具类 | 包路径 | 说明 |
|--------|--------|------|
| `Result<T>` | `io.ims.commons.tools.utils` | 统一返回结果 |
| `ConvertUtils` | `io.ims.commons.tools.utils` | 对象转换 |
| `JavaBeanUtils` | `io.ims.commons.tools.utils` | JavaBean 工具 |
| `ValidatorUtils` | `io.ims.commons.tools.validator` | 参数校验 |
| `DateUtils` | `io.ims.commons.tools.utils` | 日期工具 |
| `StringUtils` | `org.apache.commons.lang3` | 字符串工具 |
| `CollectionUtils` | `com.baomidou.mybatisplus.core.toolkit` | 集合工具 |

### B. 常用注解

| 注解 | 说明 | 示例 |
|------|------|------|
| `@DataFilter` | 数据权限过滤 | `@DataFilter` |
| `@LogOperation` | 操作日志 | `@LogOperation("保存")` |
| `@PreAuthorize` | 权限控制 | `@PreAuthorize("hasAuthority('wm:wmclass:save')")` |
| `@Transactional` | 事务管理 | `@Transactional(rollbackFor = Exception.class)` |
| `@TableField(fill = FieldFill.INSERT)` | 自动填充 | 创建时间、创建人 |
| `@TableField(fill = FieldFill.INSERT_UPDATE)` | 自动填充 | 更新时间、更新人 |

### C. 开发检查清单

- [ ] 数据库表设计完成，包含必要字段（id, create_date, creator, del_flag 等）
- [ ] Entity 继承 `BaseEntity` 或 `BaseTenantEntity`
- [ ] Dao 继承 `BaseDao` 并添加 `@Mapper`
- [ ] XML 映射文件配置正确，namespace 正确
- [ ] DTO 实现 `Serializable`，添加 `@ApiModelProperty`
- [ ] Service 继承 `CrudService`
- [ ] ServiceImpl 继承 `CrudServiceImpl` 并实现 `getWrapper()`
- [ ] Controller 添加权限注解和 Swagger 注解
- [ ] Excel 类配置正确（如需导入导出）
- [ ] Feign Client 和 FallbackFactory 配置（如需跨模块调用）
- [ ] 单元测试通过
