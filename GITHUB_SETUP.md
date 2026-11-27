# GitHub 上传指南

## 步骤1: 在GitHub上创建新仓库

1. 登录 GitHub
2. 点击右上角的 "+" 按钮，选择 "New repository"
3. 填写仓库信息：
   - Repository name: `competitive-intelligence` (或你喜欢的名字)
   - Description: "竞争情报分析平台 - GTM策略诊断和知识库构建"
   - 选择 Public 或 Private
   - **不要**勾选 "Initialize this repository with a README"
4. 点击 "Create repository"

## 步骤2: 连接本地仓库到GitHub

复制GitHub提供的命令，通常是：

```bash
git remote add origin https://github.com/YOUR_USERNAME/competitive-intelligence.git
git branch -M main
git push -u origin main
```

或者使用SSH：

```bash
git remote add origin git@github.com:YOUR_USERNAME/competitive-intelligence.git
git branch -M main
git push -u origin main
```

## 步骤3: 推送代码

如果还没有创建初始提交，先执行：

```bash
git add .
git commit -m "Initial commit: Competitive Intelligence Analysis Platform"
```

然后推送：

```bash
git push -u origin main
```

## 注意事项

1. **大文件处理**: 如果仓库中有大文件（>100MB），GitHub可能会拒绝。考虑使用Git LFS或排除大文件。

2. **敏感信息**: 确保 `.gitignore` 已正确配置，不要上传敏感数据。

3. **数据文件**: 根据你的需求，可能需要调整 `.gitignore` 来决定是否上传数据文件。

## 当前仓库状态

已创建初始提交，包含：
- ✅ 完整的项目结构
- ✅ 分析脚本
- ✅ 知识库文档
- ✅ README.md
- ✅ .gitignore

现在只需要连接到GitHub并推送即可！
