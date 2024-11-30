import os
import csv

MOVIE_CSV_PATH = "data/movie.csv"
POSTER_FOLDER = "movie_posters"
MISSING_IDS_OUTPUT = "missing_movie_ids.csv"

def find_missing_posters(movie_csv_path, poster_folder):
    missing_ids = []
    try:
        with open(movie_csv_path, "r", encoding="utf-8") as csvfile:
            reader = csv.reader(csvfile)
            next(reader)  # 跳过标题行
            for row in reader:
                movie_id = row[0]
                poster_path = os.path.join(poster_folder, f"{movie_id}.jpg")
                if not os.path.exists(poster_path):
                    missing_ids.append(movie_id)
    except Exception as e:
        print(f"读取 {movie_csv_path} 时发生错误：{e}")

    # 将缺失的 movieId 保存到文件
    try:
        with open(MISSING_IDS_OUTPUT, "w", encoding="utf-8", newline="") as outfile:
            writer = csv.writer(outfile)
            writer.writerow(["movieId"])  # 写入标题行
            for movie_id in missing_ids:
                writer.writerow([movie_id])
        print(f"缺失的电影 ID 已保存到：{MISSING_IDS_OUTPUT}")
    except Exception as e:
        print(f"保存缺失电影 ID 时发生错误：{e}")

if __name__ == "__main__":
    find_missing_posters(MOVIE_CSV_PATH, POSTER_FOLDER)
