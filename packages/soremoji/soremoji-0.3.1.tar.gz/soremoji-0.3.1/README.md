# Soremoji

自维护的 gitmoji-cli，做了部分更改

## 安装

```bash
poetry add soremoji --dev
```

## 在 pre-commit 中使用

```yaml
# .pre-commit-config.yaml
default_install_hook_types: [pre-commit, prepare-commit-msg]
repos:
  - repo: https://github.com/pycqa/isort
    rev: 5.10.1
    hooks:
      - id: isort
        stages: [commit]

  - repo: https://github.com/psf/black
    rev: 22.6.0
    hooks:
      - id: black
        stages: [commit]

  - repo: https://github.com/netsora/soremoji
    rev: 0.3.1
    hooks:
      - id: soremoji
        stages: [pre-commit-msg]
```

## 使用

### 快速提交

使用如下命令，选择一个 emoji 并填写提交信息：

```bash
soremoji commit
```

### 交互式使用

```bash
soremoji
```

## 支持的emoji

<details>
<summary>展开查看</summary>

| 表情 |           名称            |                    介绍                    |
| :--: | :-----------------------: | :----------------------------------------: |
|  🎨  |            art            |                引起重大变化                |
| ⚡️  |            zap            |                  提高性能                  |
|  🔥  |           fire            |               删除代码或文件               |
|  🐛  |            bug            |                修复一个错误                |
|  ✨  |         sparkles          |                 引入新功能                 |
|  📝  |           memo            |               添加或更新文档               |
|  🚀  |          rocket           |                  部署东西                  |
|  💄  |         lipstick          |         添加或更新 UI 和 样式文件          |
|  🎉  |           tada            |                开始一个项目                |
|  ✅  |     white_check_mark      |            添加、更新或通过测试            |
|  🔖  |         bookmark          |               发布/版本表情                |
|  🚨  |      rotating_light       |          修复 编译器/linter 警告           |
|  🚧  |       construction        |               工作正在进行中               |
|  💚  |        green_heart        |                修复 CI 构建                |
|  ⬇️  |        arrow_down         |                  降级依赖                  |
|  ⬆️  |         arrow_up          |                  升级依赖                  |
|  📌  |          pushpin          |            将依赖固定到特定版本            |
|  👷  |    construction_worker    |           添加或更新 CI 构建系统           |
|  📈  | chart_with_upwards_trend  |          添加或更新分析或跟踪代码          |
|  ♻️  |          recycle          |                  重构代码                  |
|  ➕  |      heavy_plus_sign      |                 添加依赖项                 |
|  ➖  |     heavy_minus_sign      |                 删除依赖项                 |
|  🔧  |          wrench           |             添加或更新配置文件             |
|  🔨  |          hammer           |             添加或更新开发脚本             |
|  🌐  |   globe_with_meridians    |               国际化和本地化               |
|  ✏️  |          pencil2          |                修正拼写错误                |
| ⏪️  |          rewind           |                  还原更改                  |
|  🔀  | twisted_rightwards_arrows |                  合并分支                  |
| 📦️  |          package          |          添加或更新编译的文件或包          |
| 👽️  |           alien           |        由于外部 API 更改而更新代码         |
|  🚚  |           truck           | 移动或重命名资源（例如：文件、路径、路由） |
|  📄  |      page_facing_up       |              添加或更新许可证              |
|  💥  |           boom            |                引起重大变化                |
|  🍱  |           bento           |               添加或更新资产               |
| ♿️  |        wheelchair         |                提高可访问性                |
|  💡  |           bulb            |          添加或更新源代码中的注释          |
|  🍻  |           beers           |                 醉着写代码                 |
|  🔊  |        loud_sound         |               添加或更新日志               |
|  🔇  |           mute            |                  删除日志                  |
|  🚸  |     children_crossing     |            改善用户体验/可用性             |
|  🏗️  |   building_construction   |                进行架构更改                |
|  🙈  |        see_no_evil        |        添加或更新 `.gitignore` 文件        |
|  🏷️  |           label           |               添加或更新类型               |
|  🚩  |  triangular_flag_on_post  |          添加、更新或删除功能标志          |
|  🥅  |         goal_net          |                  捕捉错误                  |
|  🗑️  |        wastebasket        |             弃用需要清理的代码             |
|  ⚰️  |          coffin           |                 杀死死代码                 |
|  🧑‍💻  |       technologist        |               改善开发者体验               |

</details>
