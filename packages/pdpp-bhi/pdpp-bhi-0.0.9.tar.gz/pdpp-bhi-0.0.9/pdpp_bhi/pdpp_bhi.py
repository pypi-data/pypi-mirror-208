'''
An unlocked version of the timeseries API intended for testing alternate inputs.
Mirrors the production timeseries API in the crucial respects, but won't be as fast.

ONLY works afer the first three variables in MockAPI.__init__ are populated.
'''

from typing import Sequence, Tuple
from collections import defaultdict

import pandas as pd
import numpy as np

class MockApi:
    def __init__(
            self, clinical_path, peptide_path, protein_path,
            month_gaps=[0, 6, 12, 24],
            group_id_column='group_key', export_group_id_column=False
        ):
        '''
        YOU MUST UPDATE THE FIRST THREE LINES of this method.
        They've been intentionally left in an invalid state.

        Variables to set:
            input_paths: a list of two or more paths to the csv files to be served
            group_id_column: the column that identifies which groups of rows the API should serve.
                A call to iter_test serves all rows of all dataframes with the current group ID value.
            export_group_id_column: if true, the dataframes iter_test serves will include the group_id_column values.
        '''
        clinical = pd.read_csv(clinical_path)
        peptide = pd.read_csv(peptide_path)
        protein = pd.read_csv(protein_path)
        self.month_gaps = month_gaps
        
        self.input_paths: Sequence[str] = [protein_path, peptide_path, clinical_path]
        self.group_id_column: str = group_id_column
        self.export_group_id_column: bool = export_group_id_column
        # iter_test is only designed to support at least two dataframes, such as test and sample_submission
        assert len(self.input_paths) >= 2

        # compose `test` dataframe, which has
        # visit_id, visit_month, patient_id, updrs_test, row_id, group_key columns
        test = clinical[['visit_id', 'visit_month', 'patient_id']].apply(lambda row: row.repeat(4), axis=0).reset_index(drop=True)
        test['updrs_test'] = [f'updrs_{idx}' for idx in range(1, 5)] * len(clinical)
        test['row_id'] = test.visit_id + '_' + test.updrs_test
        test['group_key'] = test['visit_month']
        self.test = test.sort_values('group_key')

        # compose `test_peptides` dataframe, which has
        # visit_id, visit_month, patient_id, UniProt, Peptide, PeptideAbundance, group_key columns
        test_peptides = peptide
        test_peptides['group_key'] = test_peptides['visit_month']
        self.test_peptides = test_peptides.sort_values('group_key')

        # compose `test_proteins` dataframe, which has
        # visit_id, visit_month, patient_id, UniProt, NPX, group_key columns
        test_proteins = protein
        test_proteins['group_key'] = test_proteins['visit_month']
        self.test_proteins = test_proteins.sort_values('group_key')
        
        # Keep track of the first measurement timepoint for each patient.
        pid2init_month = self.test_proteins.groupby('patient_id').agg({'visit_month': 'min'})['visit_month'].to_dict()

        # compose `sample_submission` dataframe, which has
        # prediction_id, rating, group_key columns
        prediction_ids, group_keys = [], []
        for r in test.to_records():
            for month in self.month_gaps:
                pid = f'{r.row_id}_plus_{month}_months'
                prediction_ids.append(pid)
                group_keys.append(r.visit_month)
        
        self.sample_submission = pd.DataFrame({
            'prediction_id': prediction_ids,
            'rating': [0] * len(prediction_ids),
            'group_key': group_keys,
        })

        # hold dataframes
        self.dataframes = [self.test, self.test_peptides, self.test_proteins, self.sample_submission]

        # map prediction_id to true updrs values
        absmap = {} # (patient_id, visit_month, updrs_idx)
        for r in clinical.to_records():
            for idx in range(1, 5):
                # Skip if it is before the first measurement.
                if r.visit_month < pid2init_month[r.patient_id]:
                    continue

                absmap[(r.patient_id, r.visit_month, idx)] = r[f'updrs_{idx}']

        pids, targets = [], []
        for pid in self.sample_submission.prediction_id.values:
            patient_id = int(pid.split('_')[0])
            visit_month = int(pid.split('_')[1])
            month_gap = int(pid.split('_')[-2])
            updrs_idx = int(pid.split('_')[3])

            pids.append(pid)
            targets.append(absmap.get((patient_id, visit_month + month_gap, updrs_idx), np.nan))

        self.target = pd.DataFrame({
            'prediction_id': pids,
            'target_rating': targets,
        })

        self._status = 'initialized'
        self.predictions = []

    def iter_test(self) -> Tuple[pd.DataFrame]:
        '''
        Loads all of the dataframes specified in self.input_paths,
        then yields all rows in those dataframes that equal the current self.group_id_column value.
        '''
        if self._status != 'initialized':
            raise Exception('WARNING: the real API can only iterate over `iter_test()` once.')

        group_order = self.dataframes[0][self.group_id_column].drop_duplicates().tolist()
        self.dataframes = [df.set_index(self.group_id_column) for df in self.dataframes]

        for group_id in group_order:
            self._status = 'prediction_needed'
            current_data = []
            for df in self.dataframes:
                if group_id in df.index.values:
                    cur_df = df.loc[group_id].copy()
                else:
                    cur_df = pd.DataFrame({})

                # returning single line dataframes from df.loc requires special handling
                if not isinstance(cur_df, pd.DataFrame):
                    cur_df = pd.DataFrame({a: b for a, b in zip(cur_df.index.values, cur_df.values)}, index=[group_id])
                    cur_df = cur_df.index.rename(self.group_id_column)

                cur_df = cur_df.reset_index(drop=not(self.export_group_id_column))
                current_data.append(cur_df)

            yield tuple(current_data)

            while self._status != 'prediction_received':
                print('You must call `predict()` successfully before you can continue with `iter_test()`', flush=True)
                yield None

        self.predictions = pd.concat(self.predictions)
        self._status = 'finished'
    
    def score(self, return_result=False):
        if not self._status == 'finished':
            raise Exception('You must run a full iteration of `iter_test()` first to score.')
        
        merged = self.predictions.merge(self.target, on='prediction_id')
        merged = merged.dropna(subset=['target_rating'])

        scores = {'total': smape_p1(merged.target_rating, merged.rating)}
        for idx in range(1, 5):
            sub_df = merged[merged.prediction_id.str.contains(f'updrs_{idx}')]
            scores[f'updrs_{idx}'] = smape_p1(sub_df.target_rating, sub_df.rating)
        
        if not return_result:
            return scores
        else:
            return scores, self.predictions.merge(self.target, on='prediction_id')

    def predict(self, user_predictions: pd.DataFrame):
        '''
        Accepts and stores the user's predictions and unlocks iter_test once that is done
        '''
        if self._status == 'finished':
            raise Exception('You have already made predictions for the full test set.')
        if self._status != 'prediction_needed':
            raise Exception('You must get the next test sample from `iter_test()` first.')
        if not isinstance(user_predictions, pd.DataFrame):
            raise Exception('You must provide a DataFrame.')

        self.predictions.append(user_predictions)
        self._status = 'prediction_received'

def smape_p1(target, pred):
    t, p = target + 1, pred + 1
    return 200 / len(t) * (np.abs(t - p) / (np.abs(t) + np.abs(p))).sum()

def make_env(clinical_path, peptide_path, protein_path):
    return MockApi(clinical_path, peptide_path, protein_path)

if __name__ == '__main__':

    for fold in [1, 2, 3, 4, 5]:
        clinical_path = f'/home/dohoon/park/note/data/val_clinical_data.fold{fold}.csv'
        peptide_path = f'/home/dohoon/park/note/data/val_peptides.fold{fold}.csv'
        protein_path = f'/home/dohoon/park/note/data/val_proteins.fold{fold}.csv'

        env = make_env(clinical_path, peptide_path, protein_path)

        for test, test_peptide, test_protein, sample_sub in env.iter_test():
            env.predict(sample_sub)
        
        print(fold, env.score())

    score, res = env.score(return_result=True)
    print(res)
