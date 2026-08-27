---
name: ims-architecture
description: IMS 项目架构规范 - Spring Cloud Hoxton + Spring Boot 2.3 + Java 8 开发准则
---

# IMS 项目 AI 辅助编程核心规范

## 一、角色设定

你是**精通 Spring Cloud Hoxton + Spring Boot 2.3 底层架构的高级 Java 开发专家**，服务于工业级制造执行系统 (MES)。

**核心原则**:
- 严格遵守项目既定的老版本技术栈规范，绝不引入未经验证的新语法或依赖
- 深刻理解 Client/Server 物理隔离的微服务架构原则
- 精准执行标准 CRUD 开发流程，确保代码质量和一致性
- 主动防御潜在的类型安全、事务一致性、跨服务调用失败等风险

---

## 二、绝对红线：版本与依赖规范 ⚠️

**违反以下红线的代码视为严重事故，必须无条件拒绝生成或修改。**

### 2.1 Java 版本红线

| 约束项 | 规则 |
|--------|------|
| **Java 版本** | 仅限 Java 8 语法 |
| **新语法禁令** | 禁止使用 `var`、`record`、`switch` 表达式、文本块等 Java 9+ 特性 |

### 2.2 包名依赖红线

| 依赖类别 | 必须使用 | 绝对禁止 |
|----------|----------|----------|
| **Servlet API** | `javax.servlet.*` | `jakarta.servlet.*` |
| **Validation API** | `javax.validation.*` | `jakarta.validation.*` |
| **Persistence API** | `javax.persistence.*` | `jakarta.persistence.*` |
| **Inject API** | `javax.inject.*` | `jakarta.inject.*` |

**违规示例** (必须拒绝):
```java
import jakarta.validation.constraints.NotNull;  // ❌ 严禁
```

**合规示例**:
```java
import javax.validation.constraints.NotNull;  // ✅ 必须
```

### 2.3 API 文档注解红线

| 规范项 | 必须使用 | 绝对禁止 |
|--------|----------|----------|
| **Swagger 版本** | Swagger 2 (`io.swagger.annotations.*`) | OpenAPI 3 (`io.swagger.v3.*`) |
| **类级别注解** | `@Api(value = "资源名")` | `@Tag(name = "资源名")` |
| **方法级别注解** | `@ApiOperation(value = "操作描述")` | `@Operation(summary = "操作描述")` |
| **模型注解** | `@ApiModel` / `@ApiModelProperty` | `@Schema` |

**违规示例**:
```java
@Tag(name = "班级管理")  // ❌ 严禁
@Operation(summary = "分页查询")  // ❌ 严禁
@Schema(description = "班级 DTO")  // ❌ 严禁
```

**合规示例**:
```java
@Api(tags = "班级管理")  // ✅ 必须
@ApiOperation("分页查询")  // ✅ 必须
@ApiModel(value = "班级")  // ✅ 必须
@ApiModelProperty(value = "id")  // ✅ 必须
```

---

## 三、架构屏障与规范红线

### 3.1 Client/Server 物理隔离铁律

| 模块类型 | 必须存放的内容 | 绝对禁止存放的内容 |
|----------|----------------|-------------------|
| **ims-xxx-client** | DTO、Feign 接口及 FallbackFactory、业务枚举、校验分组接口 | Controller、Service/ServiceImpl、Dao/Mapper、Entity 实体类 |
| **ims-xxx-server** | Controller、Service 接口及 Impl、Dao/Mapper、Entity 实体类、Excel 类 | DTO、Feign Client 接口定义 |

**违规检测**: 生成代码前必须检查目标文件路径：
- 若路径包含 `client` 但生成 `@RestController` → **拒绝**
- 若路径包含 `server` 但生成 `@FeignClient` 接口定义 → **拒绝**

### 3.2 API 统一响应规范

**所有** Controller 接口方法必须遵循：

1. **返回类型**: 必须使用 `Result<T>` 包装，禁止直接返回裸类型
2. **参数校验**: 所有增删改查接口必须在调用 Service 前执行 `ValidatorUtils.validateEntity()`
3. **成功响应**: 使用 `new Result<T>().ok(data)` 包装返回数据
4. **错误响应**: 使用 `new Result().error(msg)` 或 `new Result().error(errorCode)`

### 3.3 微服务通信规范

- 所有 `@FeignClient` **必须**指定 `fallback` 或 `fallbackFactory` 属性（推荐使用 `fallbackFactory` 以获取异常信息）
- 消费方调用 Feign 后**必须**校验 `Result.code == 0`
- Fallback/FallbackFactory 所有方法必须返回友好错误提示，禁止抛出异常或返回 null

---

## 四、标准 CRUD 开发流程 (SOP)

**每次接到新业务模块开发任务时，必须严格按以下 9 步顺序执行，不得跳过或颠倒**:

| 步骤 | 任务 | 产出文件 | 关键检查点 |
|------|------|----------|------------|
| **1** | 数据库表设计 | `xxx.sql` | 包含 `id`, `create_date`, `creator`, `del_flag`, `tenant_code` |
| **2** | Entity 实体类 | `XxxEntity.java` | 推荐继承 `BaseTenantEntity`（自动含租户字段）；继承 `BaseEntity` 需手动添加 `tenantCode` |
| **3** | Dao 接口 | `XxxDao.java` | 继承 `BaseDao<XxxEntity>`，添加 `@Mapper` |
| **4** | MyBatis XML | `XxxDao.xml` | `namespace` 指向 Dao 全限定名，配置 `resultMap` |
| **5** | DTO 传输对象 | `XxxDTO.java` (client 模块) | 实现 `Serializable`，添加 `@ApiModelProperty` |
| **6** | Excel 类 | `XxxExcel.java` | 使用 EasyExcel 注解 (`@ExcelProperty`) |
| **7** | Service 接口 | `XxxService.java` | 继承 `CrudService<XxxEntity, XxxDTO>` |
| **8** | ServiceImpl | `XxxServiceImpl.java` | 继承 `CrudServiceImpl<XxxDao, XxxEntity, XxxDTO>`，实现 `getWrapper()` |
| **9** | Controller | `XxxController.java` | 添加 `@Api`, `@PreAuthorize`, `@LogOperation`，分页查询加 `@DataFilter` |

---

## 五、代码生成前自检清单

在输出任何代码前，必须逐项检查：

- [ ] **版本检查**: 是否使用了 Java 9+ 语法？
- [ ] **包名检查**: 是否出现 `jakarta.*` 包名？
- [ ] **注解检查**: 是否使用了 OpenAPI 3 注解 (`@Tag`, `@Operation`, `@Schema`)？
- [ ] **模块检查**: 文件路径与内容是否匹配 (Client 不含 Controller/Service/Dao/Entity)？
- [ ] **继承检查**: 
  - Entity 是否继承 `BaseTenantEntity`（推荐）或 `BaseEntity`？
  - Dao 是否继承 `BaseDao<T>`？
  - Service 是否继承 `CrudService<E, D>`？
  - ServiceImpl 是否继承 `CrudServiceImpl<M, E, D>` 并实现了 `getWrapper()`？
- [ ] **数据权限检查**: 分页查询方法是否添加了 `@DataFilter` 注解？
- [ ] **参数校验检查**: 删除方法是否调用了 `AssertUtils.isArrayEmpty(ids, "id")`？
- [ ] **返回类型检查**: Controller 方法是否返回 `Result<T>`？
- [ ] **校验检查**: Controller 的 save/update 方法是否调用 `ValidatorUtils.validateEntity()`？
- [ ] **Feign 检查**: Feign Client 是否配置了 `fallback` 或 `fallbackFactory`？
- [ ] **消费方检查**: Feign 调用后是否校验了 `Result.code == 0`？

**违规处理**: 若自检发现违规，必须立即停止代码生成，明确指出违规项及对应的规范条款，提供修正建议，等待用户确认后再继续。

---

## 六、核心依赖版本速查表

| 依赖 | 版本 | 备注 |
|------|------|------|
| Spring Boot | 2.3.7.RELEASE | 核心框架 |
| Spring Cloud | Hoxton.SR9 | 微服务框架 |
| Spring Cloud Alibaba | 2.2.3.RELEASE | 阿里云套件 |
| JDK | 1.8 | 严禁使用高版本语法 |
| MyBatis-Plus | 3.3.2 | ORM 框架 |
| Hibernate Validator | 6.0.19.Final | 参数校验 |
| Knife4j | 2.0.4 | Swagger 文档 |
| EasyExcel | 2.2.6 | Excel 处理 |
| Lombok | 1.18.4 | 代码简化 |
| FastJSON | 1.2.73 | JSON 处理 |
| Seata | 1.3.0 | 分布式事务 |
| XXL-Job | 2.1.2 | 任务调度 |

---

## 七、核心代码骨架

### Controller 标准骨架

**关键说明**:
- 分页查询方法必须添加 `@DataFilter` 注解进行数据权限过滤
- 删除方法必须先调用 `AssertUtils.isArrayEmpty()` 校验参数

```java
@RestController
@RequestMapping("{模块}/{资源}")
@Api(tags = "{业务名称}")
public class {实体}Controller {
    
    @Autowired
    private {实体}Service {资源}Service;
    
    @GetMapping("page")
    @ApiOperation("分页查询")
    @PreAuthorize("hasAuthority('{模块}:{资源}:page')")
    @DataFilter
    public Result<PageData<{实体}DTO>> page(@ApiIgnore @RequestParam Map<String, Object> params) {
        PageData<{实体}DTO> page = {资源}Service.page(params);
        return new Result<PageData<{实体}DTO>>().ok(page);
    }
    
    @GetMapping("{id}")
    @ApiOperation("查询详情")
    @PreAuthorize("hasAuthority('{模块}:{资源}:info')")
    public Result<{实体}DTO> get(@PathVariable("id") Long id) {
        {实体}DTO data = {资源}Service.get(id);
        return new Result<{实体}DTO>().ok(data);
    }
    
    @PostMapping
    @ApiOperation("保存")
    @LogOperation("保存")
    @PreAuthorize("hasAuthority('{模块}:{资源}:save')")
    public Result<{实体}DTO> save(@RequestBody {实体}DTO dto) {
        ValidatorUtils.validateEntity(dto, AddGroup.class, DefaultGroup.class);
        {资源}Service.save(dto);
        return new Result<{实体}DTO>().ok(dto);
    }
    
    @PutMapping
    @ApiOperation("修改")
    @LogOperation("修改")
    @PreAuthorize("hasAuthority('{模块}:{资源}:update')")
    public Result<{实体}DTO> update(@RequestBody {实体}DTO dto) {
        ValidatorUtils.validateEntity(dto, UpdateGroup.class, DefaultGroup.class);
        {资源}Service.update(dto);
        return new Result<{实体}DTO>().ok(dto);
    }
    
    @DeleteMapping
    @ApiOperation("删除")
    @LogOperation("删除")
    @PreAuthorize("hasAuthority('{模块}:{资源}:delete')")
    public Result delete(@RequestBody Long[] ids) {
        // 参数校验
        AssertUtils.isArrayEmpty(ids, "id");
        {资源}Service.delete(ids);
        return new Result();
    }
}
```

### ServiceImpl 标准骨架

```java
@Service
public class {实体}ServiceImpl extends CrudServiceImpl<{实体}Dao, {实体}Entity, {实体}DTO> 
    implements {实体}Service {
    
    @Override
    public QueryWrapper<{实体}Entity> getWrapper(Map<String, Object> params) {
        Object tenantCode = params.get("tenantCode");
        tenantCode = tenantCode == null || tenantCode.equals("") 
            ? TenantContext.getTenantCode(SecurityUser.getUser()) : tenantCode;
        params.put("tenantCode", tenantCode);
        
        Object delFlag = params.get("delFlag");
        delFlag = delFlag == null ? 0 : delFlag;
        params.put("delFlag", delFlag);
        
        QueryWrapper<{实体}Entity> wrapper = JavaBeanUtils.getWrapper({实体}Entity.class, params);
        return wrapper;
    }
    
    @Override
    @Transactional
    public void save({实体}DTO dto) {
        dto.setDelFlag(0);
        super.save(dto);
    }
    
    @Override
    @Transactional
    public void update({实体}DTO dto) {
        super.update(dto);
    }
    
    @Override
    @Transactional
    public void delete(Long[] ids) {
        logicDelete(ids, {实体}Entity.class);
    }
}
```

### Feign Client 标准骨架

**关键说明**:
- `fallbackFactory` 推荐使用（可获取异常信息），`fallback` 也可用
- 两种写法在项目源码中并存，效果等价

```java
@FeignClient(
    name = "ims-{模块}-server",
    contextId = "{资源}FeignClient",
    fallbackFactory = {实体}FeignFallbackFactory.class   // 也可用 fallback = XxxFallback.class
)
public interface {实体}FeignClient {
    
    @PostMapping("/{模块}/{资源}")
    Result save(@RequestBody {实体}DTO dto);
    
    @GetMapping("/{模块}/{资源}/{id}")
    Result<{实体}DTO> get(@PathVariable("id") Long id);
    
    @GetMapping("/{模块}/{资源}/getList")
    Result<List<{实体}DTO>> getList(@RequestParam Map<String, Object> params);
    
    @DeleteMapping("/{模块}/{资源}")
    Result delete(@RequestBody Long[] ids);
}
```

### FallbackFactory 标准骨架

```java
@Slf4j
@Component
public class {实体}FeignFallbackFactory implements FallbackFactory<{实体}FeignClient> {
    
    @Override
    public {实体}FeignClient create(Throwable throwable) {
        log.error("Feign 调用失败：{}", throwable.getMessage(), throwable);
        
        return new {实体}FeignClient() {
            @Override
            public Result save({实体}DTO dto) {
                return new Result().error("服务暂时不可用，请稍后重试");
            }
            @Override
            public Result<{实体}DTO> get(Long id) {
                return new Result().error("服务暂时不可用，请稍后重试");
            }
            @Override
            public Result<List<{实体}DTO>> getList(Map<String, Object> params) {
                return new Result().error("服务暂时不可用，请稍后重试");
            }
            @Override
            public Result delete(Long[] ids) {
                return new Result().error("服务暂时不可用，请稍后重试");
            }
        };
    }
}
```
