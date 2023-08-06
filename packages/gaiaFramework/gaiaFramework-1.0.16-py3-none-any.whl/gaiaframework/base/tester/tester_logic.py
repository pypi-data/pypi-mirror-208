import pandas as pd
import json
from typing import Dict, List
from gaiaframework.base.common.functions import flatten


class DS_Tester:

    def __init__(self):
        self.truth_dataset_id = -1
        self.model_type_id = -1
        self.data_keys = []
        self.pred_name = ""
        self.target_name = ""

    def save_meta_data(self, input_req):
        """
        Save input request meta data.
        Parameters:
            input_req: An object of type TestInputRequest
        """
        self.truth_dataset_id = input_req.truth_dataset_id
        self.model_type_id = input_req.model_type_id

    def test_batch(self, test_request):
        raise NotImplementedError

    def convert_input_to_dataframe(self, data_rows):
        """
        Convert from a list of TestInputRow to a dataframe.
        Also apply Model-Specific conversion.

        Parameters:
            data_rows: A list of objects, List[TestInputRow]
        Returns:
            Pandas dataframe that contains all the relevant information
        """
        df = pd.DataFrame.from_records((data_row.dict() for data_row in data_rows))
        df = df.apply(self.adapt_to_dsp_format, axis=1)
        return df

    def create_model_request(self, batch_input_rows):
        raise NotImplementedError

    def run_model_on_data_rows(self, row_dataframe: pd.DataFrame) -> pd.DataFrame:
        """
        Run model on all data rows. Create a format the the model can work with, and run the pipeline.
        Parameters:
            row_dataframe: Input dataframe, containing all data rows.
        Returns:
            Extended dataframe which contains the output of the model
        """
        batch_of_pages = row_dataframe.to_dict(orient='records')

        model_request = self.create_model_request(batch_of_pages)

        # Call the model to get predictions
        predicted_records = self.pipeline.execute(model_request)

        if predicted_records:
            df_predicted = self.create_predicted_records_dataframe(predicted_records)
            row_dataframe = row_dataframe.join(df_predicted)
        else:
            # we did not get any records, create empty records
            self.create_empty_predictions(row_dataframe)

        return row_dataframe

    def adapt_to_dsp_format(self, df_row):
        """
        Adapt for DSP format compatibility
        'data' is provided as string since the DSP saves it this way.
        Please feel free to modify due to your project needs

        Parameters:
            df_row: A single row from the processed data frame
        Returns:
            df_row: The flattened data frame, with all the fields previously compressed in the 'data' field
        """

        # Extract keys for later use
        self.data_keys = json.loads(df_row['data']).keys()

        # Restructure as a data frame line
        for k, v in json.loads(df_row['data']).items():
            df_row[k] = v
        return df_row

    def create_predicted_records_dataframe(self, predicted_records):
        # create a dataframe formatted as input for evaluation
        df_predicted = pd.DataFrame(predicted_records)
        df_predicted = df_predicted.rename(columns={self.pred_name: 'pred_model'})
        return df_predicted

    @staticmethod
    def create_empty_predictions(row_dataframe):
        """
        Create empty predictions in case where the model returns an error and we wish to keep evaluating
        """
        raise NotImplementedError

    def format_evaluation_output(self, row_dataframe) -> List[Dict]:
        """
        Make the results fit with the expected DSP data format
        :param row_dataframe:
        :return:
        """

        row_dataframe = row_dataframe.rename(columns={'pred': 'target', 'pred_model': 'pred'})

        output = row_dataframe.to_dict(orient='records')
        for rec in output:
            pred_dict = {}
            target_dict = {}
            for row_key in self.data_keys:
                pred_dict[row_key] = rec[row_key]
                target_dict[row_key] = rec[row_key]
            pred_dict['pred'] = rec['pred']
            target_dict['pred'] = rec['target']

            for row_key in self.data_keys:
                del rec[row_key]

            rec['target'] = json.dumps(pred_dict)
            rec['pred'] = json.dumps(target_dict)

        return output

    @staticmethod
    def format_response_row_for_dsp_upload(output, test_request):
        """
        Adapt response format to the DSP requirements
        :param output:
        :param test_request:
        :return:
        """
        row_extra_data = {
            "truth_dataset_id": test_request.truth_dataset_id,
            "model_type_id": test_request.model_type_id
        }
        for row in output:
            row.update(row_extra_data)
            row['truth_id'] = row.get('id', -1)

            if 'id' in row:
                del row['id']

            confusion_matrix_flattened = flatten(row['confusion_matrix'])
            row.update(confusion_matrix_flattened)

            del row['confusion_matrix']

            if 'id' in row:
                del row['data']

    @staticmethod
    def get_f1_precision_recall(var_name, df):
        """
        Calculate from detailed output report the f1, precision and recall scores per attribute.
        @param var_name: variable name to calculate the scores for.
        @param df: detailed results dataframe with per attribute confusion matrix as outputted by tester.
        @return: f1, precision and recall scores.
        This function should be overridden if other form of calculation is needed
        """
        tp = df[var_name + '_tp']
        fp = df[var_name + '_fp']
        tn = df[var_name + '_tn']
        fn = df[var_name + '_fn']
        recall = 0
        precision = 0
        f1 = 0
        if len(np.where(tp + fp + tn + fn != 1)[0]) > 0:
            print(f'{len(np.where(tp + fp + tn + fn != 1)[0])} examples have errors')
        if (tp.sum() + fn.sum()) != 0:
            recall = tp.sum() / (tp.sum() + fn.sum())
        if (tp.sum() + fp.sum()) != 0:
            precision = tp.sum() / (tp.sum() + fp.sum())
        if (precision + recall) != 0:
            f1 = 2 * ((precision * recall) / (precision + recall))
        return f1, precision, recall