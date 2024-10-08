import csv
from collections import Counter


def cardinality_items(filename):
    if not filename or filename == '':
        return 0
    record = set()
    with open(filename, mode='r', encoding='utf-8') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            for item in row:
                trimmed_text = item.strip()
                if trimmed_text in record:
                    continue
                record.add(trimmed_text)
    return len(record)


def all_itemsets(unique_items, k):
    result = []

    def generate_combinations(cur_set, index):
        if len(cur_set) == k:
            result.append(cur_set.copy())
            return

        for i in range(index, len(unique_items)):
            cur_set.append(unique_items[i])
            generate_combinations(cur_set, i + 1)
            cur_set.pop()

    generate_combinations([], 0)
    return result


def data_handler(filename):
    valid_cnt = 0
    user_id_set = set()
    dates = []

    with open(filename, 'r', encoding='utf-8') as file:
        for line in file:
            if ',' in line:
                valid_cnt += 1
                user_id, rating, date = line.split(',')
                user_id_set.add(user_id)
                dates.append(date)

    return valid_cnt, user_id_set, (min(dates), max(dates))


def process_combined_data_files():
    files = ["./netflix-data/combined_data_1.txt", "./netflix-data/combined_data_2.txt", "./netflix-data/combined_data_3.txt", "./netflix-data/combined_data_4.txt"]
    total_records = 0
    total_unique_users = set()
    min_date, max_date = "9999-12-31", "1900-01-01"

    # with ThreadPoolExecutor() as executor:
    #     futures = {executor.submit(data_handler, file): file for file in files}
    #
    #     for future in as_completed(futures):
    #         valid_cnt, user_id_set, date_range = future.result()
    #         total_records += valid_cnt
    #         total_unique_users.update(user_id_set)
    #         min_date = min(min_date, date_range[0])
    #         max_date = max(max_date, date_range[1])
    for file in files:
        valid_cnt, user_id_set, date_range = data_handler(file)
        total_records += valid_cnt
        total_unique_users.update(user_id_set)
        min_date = min(min_date, date_range[0])
        max_date = max(max_date, date_range[1])
    return total_records, len(total_unique_users), (min_date, max_date)


def process_movie_titles_files(filename):
    movie_title_map = Counter()
    with open(filename, mode='r', encoding='ISO-8859-1') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            movie_name = ','.join(row[2:])
            movie_title_map[movie_name] += 1
    four_diff_movies = []
    for key, value in movie_title_map.items():
        if value == 4:
            four_diff_movies.append(key)
    return len(movie_title_map.keys()), len(four_diff_movies)


def process_review_both():
    files = [
            "./netflix-data/combined_data_1.txt",
            "./netflix-data/combined_data_2.txt",
            "./netflix-data/combined_data_3.txt",
            "./netflix-data/combined_data_4.txt"
    ]
    '''
        users_rate_map scheme:
        { 
            'user_id': {
                'movie_id': rating,
                ...
            },
            ...
        }
    '''
    users_rate_map = {}
    for file_name in files:
        with open(file_name, 'r', encoding='utf-8') as file:
            current_movie_id = ""
            for line in file:
                if ':' in line:
                    current_movie_id = line.split(':')[0]
                elif ',' in line:
                    user_id, rating, date = line.split(',')
                    if user_id not in users_rate_map.keys():
                        users_rate_map[user_id] = {}
                    users_rate_map[user_id][current_movie_id] = rating
    '''
        rating_200_movies_users scheme:
        {
            'user_id': {
                'movie_name': rating,
                ...
            },
            ...
        }
    '''
    rating_200_movies_users = {}
    for user_id, rating_history in users_rate_map.items():
        if len(rating_history.keys()) == 200:
            if user_id not in rating_200_movies_users.keys():
                rating_200_movies_users[user_id] = {}
            rating_200_movies_users[user_id] = rating_history
    if len(rating_200_movies_users.keys()) == 0:
        return 0, '', []
    lowest_user_id = min(rating_200_movies_users.keys(), key=lambda x: int(x))
    lowest_id_user_5_start_rating_movies_id = set()
    for movie_id, rating in rating_200_movies_users[lowest_user_id].items():
        if str(rating) == str(5):
            lowest_id_user_5_start_rating_movies_id.add(movie_id)

    lowest_id_user_5_start_rating_movies_name = []
    # get movies name
    with open('./netflix-data/movie_titles.csv', mode='r', encoding='ISO-8859-1') as file:
        csv_reader = csv.reader(file)
        for row in csv_reader:
            movie_id, movie_name = row[0], row[2]
            if movie_id in lowest_id_user_5_start_rating_movies_id:
                lowest_id_user_5_start_rating_movies_name.append(movie_name)
    return len(rating_200_movies_users.keys()), lowest_user_id, lowest_id_user_5_start_rating_movies_name


if __name__ == '__main__':
    # answer for Q1
    basket_data_file = './basket_data.csv'
    cardinality = cardinality_items(basket_data_file)
    print(f"Cardinality is {cardinality}")

    # answer for Q2
    items = ["ham", "cheese", "bread",  "beer"]
    k = 2
    combinations = all_itemsets(items, k)
    with open('output.txt', 'w') as file:
        for combination in combinations:
            file.write(str(combination) + '\n')

    # answer for Q3
    total_records, total_unique_users_num, date_range = process_combined_data_files()
    # There are total 100480507 records of movie ratings, 480189 unique users in the dataset, the range of years is ('1999-11-11', '2005-12-31').
    print(f"There are total {total_records} records of movie ratings, {total_unique_users_num} unique users in the dataset, the range of years is {date_range}.")

    # answer for Q4
    total_unique_movie, four_diff_movies_cnt = process_movie_titles_files('./netflix-data/movie_titles.csv')
    # Q4: There are 17359 movies with unique names, and 5 movie names refer to four different movies.
    print(f"Q4: There are {total_unique_movie} movies with unique names, and {four_diff_movies_cnt} movie names refer to four different movies.")

    # answer for Q5
    users_rated_exactly_200, lowest_user_id, favorite_movies = process_review_both()
    # Q5: There are 605 users rated exactly 200 movies, and favorite movie names of lowest user ID: 508 are ['High Fidelity', "Monty Python's The Meaning of Life: Special Edition", 'American Beauty', 'Roger & Me', 'Eternal Sunshine of the Spotless Mind', 'Being John Malkovich', 'Vietnam: A Television History', 'Super Size Me', 'Lord of the Rings: The Fellowship of the Ring', 'This Is Spinal Tap', 'The Pianist', 'The Silence of the Lambs', 'Sideways', 'Whale Rider', 'Garden State', 'Bowling for Columbine', 'Gandhi', 'Apocalypse Now Redux', 'To Die For', "Monty Python's Life of Brian", 'The Manchurian Candidate', 'Memento', 'Amelie', 'Apocalypse Now', 'The Usual Suspects', 'Lord of the Rings: The Two Towers: Extended Edition', 'The Lord of the Rings: The Fellowship of the Ring: Extended Edition', 'Touching the Void', 'Minority Report', 'The Royal Tenenbaums', 'Election', 'Good Will Hunting', 'L.A. Confidential', 'Taxi Driver', 'Lord of the Rings: The Two Towers', 'Cabaret', 'Adaptation', 'The Accused', 'Lost in Translation', "Boys Don't Cry", 'To Be and To Have', "Schindler's List", 'Raging Bull', 'Lord of the Rings: The Return of the King', 'Monty Python and the Holy Grail', 'Raising Arizona', 'The Shawshank Redemption: Special Edition', 'Harold and Maude', 'Downfall', 'Lord of the Rings: The Return of the King: Extended Edition', 'Monster', 'Band of Brothers', 'Three Kings', 'Unforgiven', 'Maria Full of Grace', 'Days of Wine and Roses', 'Shakespeare in Love']
    print(f"Q5: There are {users_rated_exactly_200} users rated exactly 200 movies, and favorite movie names of lowest user ID: {lowest_user_id} are {favorite_movies}")





















































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































































