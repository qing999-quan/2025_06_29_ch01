# 2025_06_29_ch01
致理
這是全設定的
這是第2次修改
租屋處電腦試用
一、makdown語法教學
1.標題：使用「#」符號，數量代表標題層級，從 1 到 6 級。
# 這是 H1 標題
## 這是 H2 標題
### 這是 H3 標題
#### 這是 H4 標題
##### 這是 H5 標題
###### 這是 H6 標題
等號（=）和減號（-）來表示 H1 和 H2：
大標題
=======

次標題
-------
2.文字格式
粗體：用 **文字** 或 __文字__
斜體：用 *文字* 或 _文字_
粗斜體：用 ***文字***
刪除線：用 ~~文字~~
這是 **粗體**，這是 *斜體*，這是 ~~刪除線~~。
3. 清單 (Lists)
無序清單：用 *、- 或 + 表示
* 項目一
- 項目二
+ 項目三
有序清單：用數字加點表示
1. 第一項
2. 第二項
3. 第三項
清單中可以巢狀使用縮排：
1. 第一項
   * 子項目一
   * 子項目二
2. 第二項
4. 連結與圖片
連結：
[Google](https://www.google.com)
圖片（前面加 !）：
![替代文字](https://example.com/image.png)
5. 區塊引用 (Blockquotes)
用 > 表示引用，可多層巢狀：
> 這是一段引用文字。
> > 這是巢狀引用。
6. 代碼區塊
行內代碼：用反引號 ` 包住
這是 `行內代碼` 範例。
多行程式碼區塊：用三個反引號 ``` 包起來，並可指定語言做語法高亮

```python
def hello():
    print("Hello, Markdown!")
```
---

### 7. 分隔線
用三個或以上的 `-`、`*` 或 `_` 建立分隔線：
---

### 8. 表格
用管道符號 `|` 和短橫線 `-` 建立表格：
| 左對齊   | 置中對齊  | 右對齊    |
| :------- | :-------: | --------: |
| 文字1    | 文字2     | 文字3     |
| 文字4    | 文字5     | 文字6     |
---

### 9. 強制換行
在行尾加兩個空白鍵，強制換行：
這是第一行。  
這是第二行。
---
10.核取方塊
 - [ ] uncheck
 - [x] check

#### Docker 安裝
> **注意**: 目前僅支援本機連線，外部連線設定尚未測試成功

```bash
docker run --name my-postgres -e POSTGRES_PASSWORD=yourpassword -p 5432:5432 -d postgres
```

**參數說明**:
- `--name my-postgres`: 容器名稱
- `-e POSTGRES_PASSWORD=yourpassword`: 設定 PostgreSQL 使用者 `postgres` 的密碼
- `-p 5432:5432`: 將容器內的 5432 端口映射到本機 5432 端口
- `-d postgres`: 背景執行並使用 postgres 映像檔
- **預設使用者帳號**: postgres

# Docker安裝python_conda_git開發環境
- 電腦必需有安裝Docker Desktop

---

## 方法1:使用Docker Hub Repository
- 使用以下的repository

`continuumio/miniconda3`

### 步驟1 **下載repository**

```
docker pull continuumio/miniconda3
```

### 步驟2 **建立容器**
- 請不要直接使用Docker Desktop直接啟動(因為容器啟動後會直接關閉)
- 使用以下指令,建立容器,並且要求可互動,和配置一個偽TTY(容器啟動後不會自動關閉)

```bash
docker run -it --name python-miniconda continuumio/miniconda3

#-it 要求可互動,和配置一個偽TTY
#--name python-miniconda 建立容器名稱
#continuumio/miniconda3 映像名稱(一定在最後面)
```

### 步驟3 **使用VSCode Docker容器開發工具**
- Docker
- Dev container
### 步驟4 **下載github專案**
### 步驟5 **安裝VSCode套件**
- python
- jupyter
### 步驟6 **安裝python外部套件**

---

## 方法2

並且安裝nodejs 和 uv,目的是為了mcp

### 步驟1:建立docker file

- pydev為虛擬環境名稱

```dockerfile
FROM continuumio/miniconda3

# 建立 Conda 環境
RUN conda create -n pydev python=3.10 -y && conda clean -a -y

# 安裝 Node.js（含 npm/npx）
RUN conda install -n pydev nodejs -y

# 安裝 uv 到 pydev 環境
RUN conda run -n pydev pip install uv

# 驗證版本
RUN conda run -n pydev uv --version
RUN conda run -n pydev npx --version

# 設定預設目錄
WORKDIR /workspace

# 容器啟動時，自動進入 pydev bash shell
CMD ["conda", "run", "-n", "pydev", "tail", "-f", "/dev/null"]
```

### 步驟2:建立image

```bash
docker build -t my_image_name:v1.0 .
```


### 步驟3:建立容器

```bash
docker run -it --name my_container_name my-conda-env:v1.0
```