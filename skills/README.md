# Skills - 项目技能库

> 项目辅助开发工具和行政管理脚本集合

---

## 目录结构

```
skills/
├── README.md                          # 本文件 - 总入口
├── requirements.txt                   # Python 依赖包列表
├── dev/                               # 开发技能
│   ├── README.md                      # 开发技能说明
│   ├── ims-architecture.md            # IMS 项目架构规范
│   └── spring-cloud-boot-skills.md    # Spring Boot & Cloud 核心技能
└── report/                            # 报告生成
    ├── README.md                      # 报告生成说明
    ├── requirements.txt               # Python 依赖包列表
    └── scripts/weekly-report/         # 周报生成脚本
        ├── README.md                  # 周报生成说明
        ├── generate_report.py         # 命令行参数模式
        ├── quick_report.py            # 交互模式
        └── requirements.txt           # Python 依赖包列表
```

---

## 快速导航

| 模块 | 目录 | 说明 | 独立文档 |
|------|------|------|----------|
| **开发技能** | [dev/](dev/README.md) | IMS 项目架构规范、Spring Boot/Cloud 核心技能 | [dev/README.md](dev/README.md) |
| **报告生成** | [report/](report/README.md) | 周报生成等报告工具 | [report/README.md](report/README.md) |

---

## 环境准备

### 基础依赖

```bash
pip3 install -r requirements.txt
```

### 可选依赖

```bash
# 数据库直连提取表结构时需要
pip3 install pymysql
```

---

## 分项目使用

### 在后端开发项目中

引用 `dev/` 目录：

```bash
# 加载 Claude Code 技能
/ims-architecture
/spring-cloud-boot-skills
```

### 在行政管理/文档项目中

引用 `report/` 目录：

```bash
# 生成周报
python3 report/scripts/weekly-report/quick_report.py
```

---

## 注意事项

1. Python 版本需要 3.8+
2. 脚本文件使用 UTF-8 编码
3. 输出文件默认使用项目根目录作为相对路径基准
