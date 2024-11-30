## **README.md**

### **项目名称：ml-32m-poster-get**

该项目的目标是从 [The Movie Database (TMDb)](https://www.themoviedb.org) 中下载电影的海报图片，同时提供工具统计哪些电影海报缺失。

---

### **项目结构**

```plaintext
.
│  missing_figure_statistic.py    # 脚本 1：统计缺失电影海报
│  scraper.py                     # 脚本 2：下载电影海报并动态更新未完成文件
│
├─.idea                           # PyCharm 配置文件
│  ├─inspectionProfiles
│  │      profiles_settings.xml
│  ├── .gitignore
│  ├── misc.xml
│  ├── ml-32m.iml
│  ├── modules.xml
│  └── workspace.xml
│
└─data                            # 数据文件夹
        checksums.txt             # 数据完整性校验信息
        links.csv                 # 包含 movieId 和 tmdbId 映射关系
        movies.csv                # 包含电影元数据 (movieId、标题等)
        ratings.csv               # 用户评分数据
        README.txt                # 官方数据集说明文件
        tags.csv                  # 用户标签数据
```

---

### **安装要求**

1. **环境**：
   - Python 3.12
   - 推荐使用虚拟环境（如 `venv` 或 `conda`）

2. **依赖安装**：
   安装所需依赖库：
   ```bash
   pip install -r requirements.txt
   ```

3. **数据集准备**：
   项目依赖 **MovieLens 32M 数据集** (`ml-32m`)，请从官方页面自行下载：
   - 下载地址：[MovieLens 数据集](https://grouplens.org/datasets/movielens/32m/)
   - 解压后，将数据文件放入项目的 `data` 文件夹中。

---

### **使用说明**

#### **1. 统计缺失电影海报**

运行 `missing_figure_statistic.py` 脚本，检查哪些电影尚未下载海报：
```bash
python missing_figure_statistic.py
```

**输出**：
- 缺失的电影 ID 列表会保存到 `missing_movie_ids.csv`。

---

#### **2. 下载电影海报**

运行 `scraper.py` 脚本，使用 MovieLens 数据集下载 TMDb 上的电影海报：
```bash
python scraper.py
```

**功能**：
- 从 `data/movies.csv` 和 `data/links.csv` 中读取电影数据。
- 动态下载海报，存储在 `movie_posters` 文件夹中。
- 自动记录下载进度，未完成的电影保存在 `data/movies_copy.csv`。

**注意**：
- 如果 `movies_copy.csv` 文件不存在，脚本会自动从 `movies.csv` 复制创建。
- 已下载的图片不会重复下载。

---

### **数据说明**

项目依赖的 MovieLens 数据集主要包含以下文件：

#### **`movies.csv`**
- 包含电影的基本信息：
  - `movieId`：MovieLens 电影 ID
  - `title`：电影标题
  - `genres`：电影类型

示例内容：
```csv
movieId,title,genres
1,Toy Story (1995),Adventure|Animation|Children|Comedy|Fantasy
2,Jumanji (1995),Adventure|Children|Fantasy
```

#### **`links.csv`**
- 映射 MovieLens 的 `movieId` 和 TMDb 的 `tmdbId`：
  - `movieId`：MovieLens 电影 ID
  - `imdbId`：IMDB ID
  - `tmdbId`：TMDb ID

示例内容：
```csv
movieId,imdbId,tmdbId
1,0114709,862
2,0113497,8844
```

#### **`tags.csv`**
- 用户对电影的标签数据：
  - `userId`：用户 ID
  - `movieId`：电影 ID
  - `tag`：用户标签
  - `timestamp`：时间戳

示例内容：
```csv
userId,movieId,tag,timestamp
15,339,complicated,1446066093
20,1952,dystopia,1445943645
```

#### **`ratings.csv`**
- 用户评分数据：
  - `userId`：用户 ID
  - `movieId`：电影 ID
  - `rating`：评分（0.5 到 5）
  - `timestamp`：评分时间戳

示例内容：
```csv
userId,movieId,rating,timestamp
1,1,4.0,964982703
1,3,4.0,964981247
```

---

### **注意事项**

1. **大文件处理**：
   - `ratings.csv` 和 `tags.csv` 文件较大（超过 100 MB），建议使用 `Git LFS` 或将其排除在版本控制之外（添加到 `.gitignore` 文件）。

2. **错误处理**：
   - 下载过程中可能遇到网络问题或解析错误，所有错误会记录在日志文件 `image_download.log` 中。

3. **输出文件**：
   - 图片保存路径：`movie_posters/`
   - 缺失电影 ID：`missing_movie_ids.csv`
   - 剩余未处理的电影：`movies_copy.csv`

---

### **日志记录**

所有操作都会记录到日志文件 `image_download.log` 中，包括：
- 开始和结束的时间戳。
- 成功下载的电影海报。
- 跳过已存在的图片。
- 发生错误的详细信息。

示例日志内容：
```plaintext
2024-11-30 11:17:12,945 - INFO - 开始处理电影海报下载任务...
2024-11-30 11:17:12,946 - INFO - 开始处理电影 ID：1
2024-11-30 11:18:26,513 - INFO - 成功下载电影 1 的图片：movie_posters/1.jpg
2024-11-30 11:20:00,001 - ERROR - 处理电影 3 时发生错误：网络连接失败。
```

---

### **贡献**

如果您对本项目有任何改进建议或发现问题，欢迎在 [GitHub 项目页面](https://github.com/leonail1/ml-32m-poster-get) 提交 Issue 或 Pull Request。