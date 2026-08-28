---
name: spring-cloud-boot-skills
description: Spring Boot 2.3 & Cloud Hoxton 核心技能 - 自动配置、Feign、Seata 分布式事务
---

# Spring Boot & Spring Cloud 核心技能规范

## 一、Spring Boot 2.3 核心技能

### 1.1 自动配置原理

**核心注解：**
```java
@SpringBootApplication = 
    @SpringBootConfiguration      // 标识为配置类
    @EnableAutoConfiguration      // 启用自动配置
    @ComponentScan                // 组件扫描
```

**自动配置加载流程：**
1. 读取 `META-INF/spring.factories` 中的 `EnableAutoConfiguration` 配置
2. 根据 `@Conditional` 条件判断是否生效
3. 将符合条件的配置类加载到 IOC 容器

**项目中的自动配置：**
```java
// ims-commons-mybatis/src/main/resources/META-INF/spring.factories
org.springframework.boot.autoconfigure.EnableAutoConfiguration=\
  io.ims.commons.mybatis.config.MybatisPlusConfig,\
  io.ims.commons.tools.config.WebMvcConfig,\
  io.ims.commons.tools.redis.RedisConfig
```

### 1.2 Starter 机制

**自定义 Starter 结构：**
```
ims-commons-mybatis/
├── src/main/java/
│   └── io/ims/commons/mybatis/
│       ├── config/MybatisPlusConfig.java    # 配置类
│       ├── dao/BaseDao.java                 # 基础 DAO
│       ├── entity/BaseEntity.java           # 基础实体
│       └── service/CrudService.java         # 基础服务
├── src/main/resources/
│   └── META-INF/spring.factories            # 自动配置入口
└── pom.xml
```

**spring.factories 示例：**
```properties
org.springframework.boot.autoconfigure.EnableAutoConfiguration=\
  io.ims.commons.mybatis.config.MybatisPlusConfig
```

### 1.3 外部化配置

**配置优先级（从高到低）：**
1. 命令行参数
2. `SPRING_APPLICATION_JSON` 中的属性
3. `ServletConfig` 初始化参数
4. `ServletContext` 初始化参数
5. JNDI 属性
6. Java 系统属性（`System.getProperties()`）
7. 操作系统环境变量
8. `RandomValuePropertySource`
9. jar 包外部的 `application-{profile}.yml`
10. jar 包内部的 `application-{profile}.yml`
11. jar 包外部的 `application.yml`
12. jar 包内部的 `application.yml`
13. `@PropertySource` 注解
14. 默认属性

**项目中 Nacos 配置：**
```yaml
# bootstrap.yml - 优先级最高，用于引导配置
spring:
  cloud:
    nacos:
      config:
        server-addr: ${nacos-host:nacos-host}:${nacos-port:8848}
        file-extension: yaml
        extension-configs:
          - data-id: datasource.yaml
            refresh: true
          - data-id: common.yaml
            refresh: true
```

### 1.4 Condition 条件注解

**常用 Condition 注解：**

| 注解 | 说明 | 示例 |
|------|------|------|
| `@ConditionalOnClass` | 类路径存在指定类时生效 | `@ConditionalOnClass(DataSource.class)` |
| `@ConditionalOnMissingBean` | 容器中不存在指定 Bean 时生效 | `@ConditionalOnMissingBean(UserService.class)` |
| `@ConditionalOnProperty` | 配置属性存在且满足值时生效 | `@ConditionalOnProperty(prefix="ims", name="enabled")` |
| `@ConditionalOnWebApplication` | 当前是 Web 应用时生效 | `@ConditionalOnWebApplication` |
| `@Profile` | 激活指定 profile 时生效 | `@Profile("dev")` |

**项目中的 Condition 使用：**
```java
@Configuration
@ConditionalOnClass(MybatisPlusConfig.class)
@EnableConfigurationProperties(MybatisPlusProperties.class)
public class MybatisPlusAutoConfiguration {
    
    @Bean
    @ConditionalOnMissingBean
    public SqlSessionFactory sqlSessionFactory(DataSource dataSource) {
        // 创建 SqlSessionFactory
    }
}
```

### 1.5 监听器机制

**ApplicationListener 使用：**
```java
@Component
public class ApplicationStartListener implements ApplicationListener<ApplicationStartedEvent> {
    @Override
    public void onApplicationEvent(ApplicationStartedEvent event) {
        // 应用启动完成后的初始化逻辑
    }
}
```

**@EventListener 使用：**
```java
@Component
public class ConfigRefreshListener {
    
    @EventListener
    public void handleRefresh(RefreshEvent event) {
        // 配置刷新后的处理逻辑
    }
}
```

---

## 二、Spring Cloud Hoxton 核心技能

### 2.1 服务注册与发现（Nacos）

**服务注册配置：**
```yaml
# bootstrap.yml
spring:
  cloud:
    nacos:
      discovery:
        server-addr: ${nacos-host}:${nacos-port:8848}
        metadata:
          management:
            context-path: ${server.servlet.context-path}/actuator
        namespace: ${nacos-namespace:}  # 命名空间 ID
```

**服务发现使用：**
```java
@Autowired
private DiscoveryClient discoveryClient;

public String getServiceUrl(String serviceName) {
    List<ServiceInstance> instances = discoveryClient.getInstances(serviceName);
    if (instances.isEmpty()) {
        throw new RuntimeException("服务不可用：" + serviceName);
    }
    return instances.get(0).getUri().toString();
}
```

**@EnableDiscoveryClient 说明：**
```java
@SpringBootApplication
@EnableDiscoveryClient  // 启用服务发现（可选，2.2+ 可省略）
public class WmApplication {
    public static void main(String[] args) {
        SpringApplication.run(WmApplication.class, args);
    }
}
```

### 2.2 服务配置中心（Nacos Config）

**配置读取优先级：**
```
bootstrap.yml (本地) 
  → Nacos common.yaml (共享配置) 
  → Nacos datasource.yaml (扩展配置) 
  → Nacos {service-name}.yaml (服务专属配置)
```

**动态刷新机制：**
```java
@RefreshScope  // 配置刷新时重新创建 Bean
@RestController
public class ConfigController {
    
    @Value("${custom.config:default}")
    private String customConfig;
    
    @GetMapping("/config")
    public String getConfig() {
        return customConfig;  // Nacos 配置变更时自动刷新
    }
}
```

**配置导入示例：**
```yaml
spring:
  cloud:
    nacos:
      config:
        server-addr: ${nacos-host}:${nacos-port:8848}
        file-extension: yaml
        group: IMS_CLOUD_GROUP
        # 共享配置
        extension-configs:
          - data-id: datasource.yaml
            group: IMS_CLOUD_GROUP
            refresh: true  # 支持动态刷新
          - data-id: common.yaml
            group: IMS_CLOUD_GROUP
            refresh: true
```

### 2.3 服务网关（Gateway）

**项目网关配置：**
```yaml
spring:
  cloud:
    gateway:
      routes:
        - id: ims-wm-server
          uri: lb://ims-wm-server  # 负载均衡
          predicates:
            - Path=/wm/**
          filters:
            - StripPrefix=1  # 去掉路径前缀
            - name: Hystrix
              args:
                name: fallbackcmd
                fallbackUri: forward:/fallback
```

**自定义过滤器：**
```java
@Component
public class AuthFilter implements GlobalFilter, Ordered {
    
    @Override
    public Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain) {
        String token = exchange.getRequest().getHeaders().getFirst("token");
        if (StringUtils.isBlank(token)) {
            // 返回 401
            return Mono.error(new RuntimeException("未授权"));
        }
        return chain.filter(exchange);
    }
    
    @Override
    public int getOrder() {
        return -100;  // 优先级
    }
}
```

### 2.4 服务熔断与降级（Sentinel/Hystrix）

**Hystrix 配置（Hoxton 默认）：**
```yaml
feign:
  hystrix:
    enabled: true

hystrix:
  command:
    default:
      execution:
        isolation:
          thread:
            timeoutInMilliseconds: 10000
      circuitBreaker:
        requestVolumeThreshold: 10
        sleepWindowInMilliseconds: 10000
        errorThresholdPercentage: 50
```

**FallbackFactory 实现：**
```java
@Slf4j
@Component
public class WmFeignFallbackFactory implements FallbackFactory<WmFeignClient> {
    
    @Override
    public WmFeignClient create(Throwable throwable) {
        log.error("Feign 调用失败：{}", throwable.getMessage(), throwable);
        
        return new WmFeignClient() {
            @Override
            public Result<WmKcDTO> get(Long id) {
                return new Result().error("库存服务暂时不可用");
            }
        };
    }
}
```

### 2.5 声明式服务调用（OpenFeign）

**Feign 配置：**
```yaml
feign:
  client:
    config:
      default:
        connectTimeout: 5000
        readTimeout: 10000
        loggerLevel: FULL  # NONE, BASIC, HEADERS, FULL
  compression:
    request:
      enabled: true
      mime-types: text/html,application/xml,application/json
      min-request-size: 2048
```

**Feign 拦截器：**
```java
@Component
public class FeignInterceptor implements RequestInterceptor {
    
    @Override
    public void apply(RequestTemplate template) {
        // 传递用户信息
        String userId = SecurityUser.getUserId();
        template.header("userId", userId);
        
        // 传递租户信息
        String tenantCode = TenantContext.getTenantCode();
        template.header("tenantCode", tenantCode);
    }
}
```

**Feign 默认配置类：**
```java
@Configuration
public class FeignDefaultConfig {
    
    @Bean
    public RequestInterceptor requestInterceptor() {
        return new FeignInterceptor();
    }
    
    @Bean
    public Decoder decoder() {
        return new MyDecoder();  // 自定义解码器
    }
}
```

### 2.6 分布式事务（Seata）

**Seata 配置：**
```yaml
seata:
  enabled: true
  tx-service-group: ims_tx_group
  service:
    vgroup-mapping:
      ims_tx_group: default
    grouplist:
      default: 127.0.0.1:8091
  config:
    type: nacos
    nacos:
      server-addr: ${nacos-host}:${nacos-port:8848}
      group: SEATA_GROUP
      data-id: seataServer.properties
  registry:
    type: nacos
    nacos:
      application: seata-server
      server-addr: ${nacos-host}:${nacos-port:8848}
```

**全局事务使用：**
```java
@Service
public class OrderServiceImpl implements OrderService {
    
    @Autowired
    private WmFeignClient wmFeignClient;  // 调用库存服务
    
    @GlobalTransactional(timeoutMills = 300000, name = "create-order-tx")
    @Override
    @Transactional
    public void createOrder(OrderDTO order) {
        // 1. 创建订单
        orderMapper.insert(order);
        
        // 2. 扣减库存（远程调用）
        wmFeignClient.decreaseStock(order.getProductId(), order.getQuantity());
        
        // 3. 扣减账户（远程调用）
        accountFeignClient.decreaseAccount(order.getUserId(), order.getAmount());
    }
}
```

**Seata 回滚日志表：**
```sql
CREATE TABLE `undo_log` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `branch_id` bigint(20) NOT NULL,
  `xid` varchar(100) NOT NULL,
  `context` varchar(128) NOT NULL,
  `rollback_info` longblob NOT NULL,
  `log_status` int(11) NOT NULL,
  `log_created` datetime NOT NULL,
  `log_modified` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ux_undo_log` (`xid`,`branch_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
```

---

## 三、微服务监控与管理

### 3.1 Actuator 端点

**Actuator 配置：**
```yaml
management:
  endpoints:
    web:
      exposure:
        include: health,info,metrics,env,loggers
  endpoint:
    health:
      show-details: always
    loggers:
      enabled-by-default: false
```

**常用端点：**

| 端点 | 说明 | 使用场景 |
|------|------|----------|
| `/actuator/health` | 健康检查 | 负载均衡健康探测 |
| `/actuator/info` | 应用信息 | 版本展示 |
| `/actuator/metrics` | 性能指标 | 监控告警 |
| `/actuator/env` | 环境变量 | 配置排查 |
| `/actuator/loggers` | 日志级别 | 动态调整日志 |
| `/actuator/refresh` | 刷新配置 | 配置热更新 |

**动态调整日志级别：**
```bash
curl -X POST http://localhost:9108/actuator/loggers/io.ims \
  -H 'Content-Type: application/json' \
  -d '{"configuredLevel":"DEBUG"}'
```

### 3.2 Spring Boot Admin

**Admin Server 配置：**
```java
@SpringBootApplication
@EnableAdminServer  // 启用 Admin Server
public class AdminApplication {
    public static void main(String[] args) {
        SpringApplication.run(AdminApplication.class, args);
    }
}
```

**Client 注册配置：**
```yaml
spring:
  boot:
    admin:
      client:
        url: http://admin-server:8080
        instance:
          service-host-type: IP
          prefer-ip: true
```

---

## 四、微服务安全

### 4.1 OAuth2 资源服务器配置

```java
@Configuration
@EnableResourceServer
@EnableGlobalMethodSecurity(prePostEnabled = true)
public class ResourceServerConfig extends ResourceServerConfigurerAdapter {
    
    @Autowired
    private TokenStore tokenStore;
    
    @Override
    public void configure(HttpSecurity http) throws Exception {
        http.authorizeRequests()
            .antMatchers("/auth/**", "/public/**").permitAll()
            .anyRequest().authenticated()
            .and()
            .csrf().disable();
    }
    
    @Override
    public void configure(ResourceServerSecurityResources resources) throws Exception {
        resources.tokenStore(tokenStore);
    }
}
```

### 4.2 权限注解使用

```java
@RestController
@RequestMapping("wmclass")
public class WmClassController {
    
    @GetMapping("page")
    @PreAuthorize("hasAuthority('wm:wmclass:page')")  // 权限检查
    @DataFilter  // 数据权限过滤
    public Result<PageData<WmClassDTO>> page(@RequestParam Map<String, Object> params) {
        // ...
    }
    
    @PostMapping
    @PreAuthorize("hasAuthority('wm:wmclass:save')")
    public Result save(@RequestBody WmClassDTO dto) {
        // ...
    }
}
```

**权限表达式：**

| 表达式 | 说明 |
|--------|------|
| `hasAuthority('xxx')` | 拥有指定权限 |
| `hasAnyAuthority('xxx', 'yyy')` | 拥有任一权限 |
| `hasRole('ADMIN')` | 拥有指定角色 |
| `hasAnyRole('ADMIN', 'USER')` | 拥有任一角色 |
| `principal` | 当前用户主体 |
| `authentication` | 认证对象 |

---

## 五、微服务最佳实践

### 5.1 服务拆分原则

1. **单一职责每个服务只负责一个业务领域
2. **高内聚低耦合** - 相关功能聚合在一起，服务间依赖最小化
3. **数据库私有化** - 每个服务拥有独立的数据库
4. **接口标准化** - 统一使用 RESTful API + Result 封装
5. **配置外部化** - 使用 Nacos 统一管理配置

### 5.2 服务间通信规范

| 场景 | 推荐方案 | 说明 |
|------|----------|------|
| 同步调用 | OpenFeign | 简单、声明式 |
| 异步通信 | 消息队列（RabbitMQ/RocketMQ） | 解耦、削峰 |
| 大数据量 | 文件传输/OSS | 避免 HTTP 超时 |
| 实时推送 | WebSocket | 双向通信 |

### 5.3 服务容错策略

1. **超时控制** - Feign 设置合理的 `connectTimeout` 和 `readTimeout`
2. **重试机制** - 对幂等接口配置重试策略
3. **熔断降级** - 配置 Hystrix/Sentinel 熔断规则
4. **限流保护** - 对热点接口进行限流
5. **舱壁隔离** - 使用线程池隔离不同服务

### 5.4 链路追踪

**Sleuth 配置：**
```yaml
spring:
  zipkin:
    base-url: http://zipkin:9411
    sender:
      type: web
  sleuth:
    sampler:
      probability: 1.0  # 采样率（0-1）
```

**日志中追踪 ID：**
```
2024-01-01 10:00:00 [traceId=abc123, spanId=def456] INFO - 业务日志
```

---

## 六、常见问题排查

### 6.1 启动失败

**问题 1：Nacos 连接失败**
```
com.alibaba.nacos.api.exception.NacosException: failed to request Nacos server
```
**解决：** 检查 `bootstrap.yml` 中 Nacos 地址配置，确认网络连通性

**问题 2：Bean 创建失败**
```
org.springframework.beans.factory.UnsatisfiedDependencyException
```
**解决：** 检查依赖的 Bean 是否存在，@Conditional 条件是否满足

### 6.2 Feign 调用失败

**问题 1：404 Not Found**
```
feign.FeignException$NotFound: status 404
```
**解决：** 检查 Feign Client 的 `@RequestMapping` 路径是否与提供方一致

**问题 2：500 Internal Server Error**
```
feign.FeignException$InternalServerError: status 500
```
**解决：** 查看服务提供方日志，检查业务逻辑异常

### 6.3 事务失效

**问题：@Transactional 不生效**
```java
// 错误示例：同类方法调用
public void outer() {
    inner();  // 事务失效
}

@Transactional
public void inner() {
    // ...
}
```
**解决：** 通过注入自身 Bean 调用或使用 AopContext

```java
// 正确示例
@Autowired
@Lazy
private OrderService self;

public void outer() {
    self.inner();  // 事务生效
}
```
