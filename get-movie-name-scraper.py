import os
import csv
import logging
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

# 配置日志，仅输出到控制台
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

BASE_URL = "https://www.themoviedb.org/movie/"
MOVIE_CSV_PATH = "movies-sample.csv"
LINK_CSV_PATH = "links-sample.csv"
OUTPUT_FILE = "movie_id_to_name.csv"
MIN_TIME_PER_REQUEST = 10  # 每次请求的最小时间（秒）

# 初始化输出文件
if not os.path.exists(OUTPUT_FILE):
    with open(OUTPUT_FILE, "w", encoding="utf-8", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["movieId", "movieName"])
        logging.info(f"创建输出文件：{OUTPUT_FILE}")


def get_existing_movie_ids(output_file):
    """
    获取已保存的 movieId 列表
    """
    existing_movie_ids = set()
    try:
        with open(output_file, "r", encoding="utf-8") as csvfile:
            reader = csv.reader(csvfile)
            next(reader)  # 跳过标题行
            for row in reader:
                existing_movie_ids.add(row[0])
    except Exception as e:
        logging.error(f"读取 {OUTPUT_FILE} 时出错：{e}")
    return existing_movie_ids


def get_tmdb_id(movie_id, link_csv_path):
    """
    根据 movieID 在 link.csv 中查找对应的 tmdbID
    """
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
    """
    使用 Edge 浏览器获取电影名称
    """
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
    """
    保存电影 ID 和名称到输出文件
    """
    try:
        with open(OUTPUT_FILE, "a", encoding="utf-8", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([movie_id, movie_name])
            logging.info(f"成功保存电影 {movie_id}: {movie_name}")
    except Exception as e:
        logging.error(f"保存电影 {movie_id} 时发生错误：{e}")


def process_movies_with_edge(movie_csv_path, link_csv_path, output_file):
    """
    遍历 movies-sample.csv 的第一列，根据 link.csv 查找 tmdbID 并获取电影名称
    """
    options = Options()
    service = Service()
    driver = webdriver.Edge(service=service, options=options)

    try:
        existing_movie_ids = get_existing_movie_ids(output_file)
        with open(movie_csv_path, "r", encoding="utf-8") as csvfile:
            reader = csv.reader(csvfile)
            next(reader)  # 跳过标题行
            for row in reader:
                movie_id = row[0]
                if movie_id in existing_movie_ids:
                    logging.info(f"电影 ID {movie_id} 已存在于 {OUTPUT_FILE} 中，跳过。")
                    continue

                logging.info(f"开始处理电影 ID：{movie_id}")
                start_time = time.time()  # 记录开始时间

                tmdb_id = get_tmdb_id(movie_id, link_csv_path)
                if not tmdb_id:
                    logging.warning(f"在 link.csv 中找不到电影 ID {movie_id} 的 tmdbID，跳过。")
                    continue

                movie_name = get_movie_name_with_edge(movie_id, tmdb_id, driver)
                if movie_name:
                    save_to_output(movie_id, movie_name)
                else:
                    logging.warning(f"电影 ID {movie_id} 未成功获取名称，跳过。")

                # 计算处理时间并补足到指定最小时间
                elapsed_time = time.time() - start_time
                if elapsed_time < MIN_TIME_PER_REQUEST:
                    remaining_time = MIN_TIME_PER_REQUEST - elapsed_time
                    logging.info(f"当前操作耗时 {elapsed_time:.2f} 秒，延时 {remaining_time:.2f} 秒以补足到 {MIN_TIME_PER_REQUEST} 秒")
                    time.sleep(remaining_time)

    except Exception as e:
        logging.error(f"处理电影名称任务时发生错误：{e}")
    finally:
        driver.quit()


if __name__ == "__main__":
    logging.info("开始处理电影名称获取任务...")
    process_movies_with_edge(MOVIE_CSV_PATH, LINK_CSV_PATH, OUTPUT_FILE)
    logging.info("任务完成！")
