import os
import csv
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import shutil
import time

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("movie_name_scraper.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

BASE_URL = "https://www.themoviedb.org/movie/"
MOVIE_CSV_PATH = "movies.csv"
LINK_CSV_PATH = "links.csv"
OUTPUT_FILE = "movie_id_to_name.csv"
REMAINING_FILE = "for_movies_name.csv"

# 初始化文件
if not os.path.exists(REMAINING_FILE):
    shutil.copy(MOVIE_CSV_PATH, REMAINING_FILE)
    logging.info(f"创建处理中的文件：{REMAINING_FILE}（从 {MOVIE_CSV_PATH} 复制）")

if not os.path.exists(OUTPUT_FILE):
    with open(OUTPUT_FILE, "w", encoding="utf-8", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["movieId", "movieName"])
        logging.info(f"创建输出文件：{OUTPUT_FILE}")


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


def get_movie_name_with_edge(movie_id, tmdb_id, driver, wait_time=10):
    movie_url = f"{BASE_URL}{tmdb_id}"
    try:
        driver.get(movie_url)
        wait = WebDriverWait(driver, wait_time)
        movie_name_element = wait.until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="original_header"]/div[2]/section/div[1]/h2/a'))
        )
        return movie_name_element.text.strip()
    except TimeoutException:
        logging.error(f"等待超时，未找到电影名称元素：{movie_url}")
        return None
    except WebDriverException as e:
        logging.error(f"使用 Edge 浏览器处理电影 {movie_id} 时发生错误：{e}")
        return None


def save_to_output(movie_id, movie_name):
    try:
        with open(OUTPUT_FILE, "a", encoding="utf-8", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([movie_id, movie_name])
            logging.info(f"成功保存电影 {movie_id}: {movie_name}")
    except Exception as e:
        logging.error(f"保存电影 {movie_id} 时发生错误：{e}")


def remove_processed_movie(movie_id):
    try:
        with open(REMAINING_FILE, "r", encoding="utf-8") as infile:
            rows = list(csv.reader(infile))

        with open(REMAINING_FILE, "w", encoding="utf-8", newline="") as outfile:
            writer = csv.writer(outfile)
            for row in rows:
                if row[0] != movie_id:
                    writer.writerow(row)
        logging.info(f"已从 {REMAINING_FILE} 中删除电影 ID：{movie_id}")
    except Exception as e:
        logging.error(f"更新 {REMAINING_FILE} 时发生错误：{e}")


def process_movies_with_edge(movie_csv_path, link_csv_path):
    options = Options()
    service = Service()
    driver = webdriver.Edge(service=service, options=options)

    while True:
        try:
            if not os.path.exists(REMAINING_FILE) or os.stat(REMAINING_FILE).st_size == 0:
                logging.info("所有电影已处理完成！")
                break

            with open(REMAINING_FILE, "r", encoding="utf-8") as csvfile:
                reader = csv.reader(csvfile)
                next(reader, None)  # 跳过标题行
                for row in reader:
                    movie_id = row[0]
                    try:
                        logging.info(f"开始处理电影 ID：{movie_id}")
                        tmdb_id = get_tmdb_id(movie_id, link_csv_path)
                        if not tmdb_id:
                            logging.warning(f"在 link.csv 中找不到电影 ID {movie_id} 的 tmdbID，跳过。")
                            continue
                        movie_name = get_movie_name_with_edge(movie_id, tmdb_id, driver)
                        if movie_name:
                            save_to_output(movie_id, movie_name)
                            remove_processed_movie(movie_id)
                        else:
                            logging.warning(f"电影 ID {movie_id} 未成功获取名称，跳过。")
                    except Exception as e:
                        logging.error(f"处理电影 ID {movie_id} 时发生错误：{e}")
                        continue
        except Exception as e:
            logging.error(f"发生致命错误：{e}")
            time.sleep(5)  # 延时以避免短时间重复错误
            continue
        finally:
            driver.quit()


if __name__ == "__main__":
    logging.info("开始处理电影名称获取任务...")
    process_movies_with_edge(MOVIE_CSV_PATH, LINK_CSV_PATH)
    logging.info("任务完成！")
