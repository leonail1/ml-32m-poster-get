import os
import csv
import requests
from lxml import html
import logging
import shutil
import time

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("image_download.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

BASE_URL = "https://www.themoviedb.org/movie/"
OUTPUT_FOLDER = "movie_posters"
MOVIE_CSV_PATH = "data/movies.csv"
MOVIE_COPY_PATH = "data/movies_copy.csv"
LINK_CSV_PATH = "data/links.csv"

# 创建存储图片的文件夹
if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)
    logging.info(f"创建文件夹：{OUTPUT_FOLDER}")

# 检查并创建 movie_copy.csv
if not os.path.exists(MOVIE_COPY_PATH):
    shutil.copy(MOVIE_CSV_PATH, MOVIE_COPY_PATH)
    logging.info(f"movie_copy.csv 不存在，已从 {MOVIE_CSV_PATH} 创建副本：{MOVIE_COPY_PATH}")
else:
    logging.info(f"movie_copy.csv 已存在，直接使用。")

# 统计信息
total_movies = 0
downloaded_movies = 0
skipped_movies = 0
errors = 0

def get_tmdb_id(movie_id, link_csv_path):
    try:
        with open(link_csv_path, "r", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row["movieId"] == movie_id:
                    return row["tmdbId"]
    except Exception as e:
        logging.error(f"读取 link.csv 文件时出错：{e}")
    return None

def download_poster(movie_id, tmdb_id):
    global downloaded_movies, skipped_movies, errors
    image_path = os.path.join(OUTPUT_FOLDER, f"{movie_id}.jpg")
    if os.path.exists(image_path):
        logging.info(f"电影 {movie_id} 的图片已存在，跳过下载。")
        skipped_movies += 1
        return True

    movie_url = f"{BASE_URL}{tmdb_id}"
    try:
        response = requests.get(movie_url)
        if response.status_code != 200:
            logging.error(f"访问 URL {movie_url} 失败，状态码：{response.status_code}")
            errors += 1
            return False

        tree = html.fromstring(response.content)
        poster_url = tree.xpath('//*[@id="original_header"]/div[1]/div/div[1]/div/img/@src')[0]
        img_response = requests.get(poster_url)
        if img_response.status_code == 200:
            with open(image_path, "wb") as img_file:
                img_file.write(img_response.content)
            logging.info(f"成功下载电影 {movie_id} 的图片：{image_path}")
            downloaded_movies += 1
            return True
        else:
            logging.error(f"下载图片失败，状态码：{img_response.status_code}")
            errors += 1
            return False
    except Exception as e:
        logging.error(f"处理电影 {movie_id} 时发生错误：{e}")
        errors += 1
        return False

def remove_movie_from_copy(movie_id):
    try:
        with open(MOVIE_COPY_PATH, "r", encoding="utf-8") as infile:
            rows = list(csv.reader(infile))
        with open(MOVIE_COPY_PATH, "w", encoding="utf-8", newline="") as outfile:
            writer = csv.writer(outfile)
            for row in rows:
                if row[0] != movie_id:
                    writer.writerow(row)
        logging.info(f"已从 {MOVIE_COPY_PATH} 中删除电影 ID：{movie_id}")
    except Exception as e:
        logging.error(f"更新 {MOVIE_COPY_PATH} 时发生错误：{e}")

def process_movies(movie_csv_path, link_csv_path):
    global total_movies, errors
    while True:
        try:
            if not os.path.exists(MOVIE_COPY_PATH) or os.stat(MOVIE_COPY_PATH).st_size == 0:
                logging.info("所有电影已处理完成！")
                break

            with open(MOVIE_COPY_PATH, "r", encoding="utf-8") as csvfile:
                reader = csv.reader(csvfile)
                next(reader, None)  # 跳过标题行
                for row in reader:
                    movie_id = row[0]
                    total_movies += 1
                    logging.info(f"开始处理电影 ID：{movie_id}")

                    tmdb_id = get_tmdb_id(movie_id, link_csv_path)
                    if tmdb_id:
                        success = download_poster(movie_id, tmdb_id)
                        if success:
                            remove_movie_from_copy(movie_id)
                    else:
                        logging.warning(f"在 link.csv 中找不到电影 ID {movie_id} 的 tmdbID，跳过。")
                        errors += 1
        except Exception as e:
            logging.error(f"发生致命错误：{e}")
            time.sleep(5)
            continue

if __name__ == "__main__":
    logging.info("开始处理电影海报下载任务...")
    process_movies(MOVIE_CSV_PATH, LINK_CSV_PATH)
    logging.info("任务完成！")

    logging.info(f"总电影数：{total_movies}")
    logging.info(f"成功下载：{downloaded_movies}")
    logging.info(f"跳过（已存在）：{skipped_movies}")
    logging.info(f"出错电影数：{errors}")
