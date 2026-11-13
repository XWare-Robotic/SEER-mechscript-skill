# SEER-mechscript-skill

给 Codex 和 Claude Code 使用的中文技能，用于编写、修改和排查仙工 SRC2000 机构脚本。

技能涵盖 RoboKit 作业生命周期、`Module.run` 逐帧推进、任务参数与配置参数、SDK 接口核对、RoboShop 导入及离线回放。它引导智能体用各自的证据确认命令发送、设备应答和物理动作完成。

安装只需要 Git 和支持本地技能的客户端。离线示例只需要 Python 3 标准库。使用厂商接口时，另行取得与目标控制器匹配的仙工文档和 SDK。仓库中的代码仅用于离线演示。

## 获取技能

在本机克隆一次。下方安装命令以这个克隆路径为例。

```sh
git clone https://github.com/XWare-Robotic/SEER-mechscript-skill.git "$HOME/SEER-mechscript-skill"
```

## 安装到 Codex

在要使用技能的项目根目录执行以下命令。若已有同名目录，请先检查是否有本地修改。

```sh
mkdir -p .agents/skills
cp -R "$HOME/SEER-mechscript-skill/skills/seer-mechanism-script" .agents/skills/
```

如果希望在本机各项目使用，把整个 `seer-mechanism-script` 目录复制到 `~/.agents/skills/`。使用 `$seer-mechanism-script` 或通过 `/skills` 选择。技能未显示时重启 Codex。见 [Codex 技能文档](https://learn.chatgpt.com/docs/build-skills#where-codex-loads-local-skills)。

## 安装到 Claude Code

在要使用技能的项目根目录执行以下命令。若已有同名目录，请先检查是否有本地修改。

```sh
mkdir -p .claude/skills
cp -R "$HOME/SEER-mechscript-skill/skills/seer-mechanism-script" .claude/skills/
```

如果希望在本机各项目使用，把整个 `seer-mechanism-script` 目录复制到 `~/.claude/skills/`。输入 `/seer-mechanism-script` 调用。见 [Claude Code 技能文档](https://code.claude.com/docs/en/skills)。

更新时，在克隆目录执行 `git pull --ff-only`，再用新的技能目录替换已安装的副本。若副本有本地修改，先比对再合并。

## 使用与验证

可以在调用技能时说明目标 RoboKit 和 Python 版本、待查脚本和期望行为。例如：“检查这段机构脚本的逐帧推进，说明超时后作业如何结束，并用离线回放验证。”

- [技能入口](skills/seer-mechanism-script/SKILL.md) 说明何时使用技能和开发流程。
- [接口查询](skills/seer-mechanism-script/references/接口查询.md) 说明如何核对版本、单位和返回值。
- [导入与重启](skills/seer-mechanism-script/references/导入与重启.md) 说明如何核对实际加载的文件和生效参数。
- [模拟与回放](skills/seer-mechanism-script/references/模拟与回放.md) 提供离线验证流程。

在本仓库根目录运行以下命令。示例使用假时钟和设备替身，覆盖应答与到位、缺失或错配反馈、超时、拒绝和取消。

```sh
python3 skills/seer-mechanism-script/scripts/replay_action.py -v
```

## 贡献与许可证

欢迎提交 [Issue](https://github.com/XWare-Robotic/SEER-mechscript-skill/issues) 或 Pull Request。报告接口差异时，请附上适用的 RoboKit 和 SDK 版本、资料出处、预期行为以及脱敏的最小复现。修改示例时，请运行离线回放。

本仓库的原创技能说明和示例采用 [MIT 许可证](LICENSE)。仙工控制器、SDK 及厂商文档由各自权利人提供，遵循其原有条款。厂商资料见[仙工智能帮助中心](https://seer-robotics.ai/zh/help-center)。
