import numpy as np
import pandas as pd

def read_csv(filename):
    """Read a CSV file"""
    data = pd.read_csv(filename, encoding='utf-8')
    return data

# def get_csv_data(filename):
#     """Get the data from a CSV file"""
#     data = np.genfromtxt(filename, delimiter=',')
#     return data

def get_target_column(data, _col="avg_correct"):
    """Get the avg_score column from the data"""
    target = data[:, _col]
    return target

def get_scores(data):
    """Get the scores from the data"""
    scores = data["avg_correct"]
    return scores

def get_quartiles(_scores):
    # Ensure the data is a numpy array
    data = np.array(pd.to_numeric(_scores, errors='coerce'))
    print(data)
    # Handle NaN values
    data = data[~np.isnan(data)]
    # Calculate quartiles
    Q1 = np.percentile(data, 25)
    Q2 = np.percentile(data, 50)
    Q3 = np.percentile(data, 75)
    return Q1, Q2, Q3

# def get_quartiles(_scores):
#     # Ensure the data is a numpy array
#     data = np.array(pd.to_numeric(_scores, errors='coerce'))
#     print(data)
#     # # Calculate quartiles
#     # Q1 = np.percentile(data, 25)
#     # Q2 = np.percentile(data, 50)
#     # Q3 = np.percentile(data, 75)
#     # # Q4 = np.percentile(data, .100)
#     # return Q1, Q2, Q3

if __name__ == "__main__":
    filename = (f"SA_questions.csv")
    data = read_csv(filename)
    print(data.head())
    avg_correct = get_scores(data)
    print (avg_correct)

    Q1, Q2, Q3 = get_quartiles(avg_correct)
    print(f"Q1: {Q1}, Q2: {Q2}, Q3: {Q3}")