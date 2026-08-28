# 开发技能 (dev/)

> IMS 项目架构规范与 Spring Boot/Cloud 核心技能 - Claude Code 技能文档

---

## 技能列表

| 技能 | 调用命令 | 说明 |
|------|----------|------|
| ims-architecture | `/ims-architecture` | IMS 项目架构规范 - CRUD 开发、Client/Server 隔离 |
| spring-cloud-boot-skills | `/spring-cloud-boot-skills` | Spring Boot & Cloud 核心技能 |

---

## 使用方式

```
/ims-architecture          加载 IMS 项目架构规范
/spring-cloud-boot-skills  加载 Spring 框架核心技能
```

技能加载后，AI 会按照该技能定义的规范进行代码生成和审查。

---

## 技能说明

### ims-architecture 核心内容

1. **绝对红线**
   - Java 8 语法限制
   - javax.* 包名限制（禁止 jakarta.*）
   - Swagger 2 注解限制（禁止 OpenAPI 3）

2. **架构屏障**
   - Client/Server 物理隔离
   - Result<T> 统一响应
   - Feign 降级配置

3. **标准 CRUD 流程 (9 步 SOP)**
   - 数据库表 → Entity → Dao → XML → DTO → Excel → Service → ServiceImpl → Controller

4. **代码生成自检清单**
   - 版本检查、包名检查、注解检查、继承检查等

### spring-cloud-boot-skills 核心内容

1. **Spring Boot 2.3**
   - 自动配置原理
   - 启动流程
   - 配置加载机制

2. **Spring Cloud Hoxton**
   - Nacos 服务注册/配置
   - Feign 远程调用
   - Seata 分布式事务

3. **常见问题排查**
   - 服务启动失败
   - Feign 调用超时
   - 事务回滚失效

---

## 文件结构

```
dev/
├── README.md                          # 本文件
├── ims-architecture.md                # IMS 项目架构规范
└── spring-cloud-boot-skills.md        # Spring Boot & Cloud 核心技能
```

---

## 同步说明

本目录与 `.claude/skills/dev/` 保持同步，内容一致。
