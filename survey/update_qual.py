import pandas as pd

#data = pd.read_csv('Batch_3141946_batch_results.csv')
data = pd.read_csv('Batch_3145473_batch_results.csv')
workers = data.WorkerId

update_qual = pd.DataFrame({'Worker ID': workers, 'UPDATE-did fact check survey': 1})

update_qual.to_csv('update_qual.csv')