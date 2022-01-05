import argparse
import logging

import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions

class OlistDatasetOptions(PipelineOptions):
    @classmethod
    def _add_argparse_args(cls, parser):
        # Use add_value_provider_argument for arguments to be templatable
        # Use add_argument as usual for non-templatable arguments
        parser.add_value_provider_argument(
            '--input',
            default='gs://dataflow-samples/shakespeare/kinglear.txt',
            help='Path of the file to read from')


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.INFO)
    # Create the Pipeline with remaining arguments.
    beam_options = PipelineOptions()
    #pipeline = beam.Pipeline(options=beam_options)

    with beam.Pipeline(options=beam_options) as p:
        olist_dataset_options = beam_options.view_as(OlistDatasetOptions)

        SCHEMA = 'product_category_name:String,product_category_name_english:STRING'
        (p | 'Read files' >> beam.io.ReadFromText(olist_dataset_options.input, skip_header_lines=1)
         | 'Split' >> beam.Map(lambda x: x.split(','))
         | 'Filter Blank Row' >> beam.Filter(lambda x: x[0] != '' and x[1] != '')
         | 'Making product Dict Map' >> beam.Map(
                    lambda x: {'product_category_name': x[0], 'product_category_name_english': x[1]})
         | 'Write ProductCat BigQuery' >> beam.io.WriteToBigQuery(table='gcp-learning-333002:olist.product_category',
                                                                  schema=SCHEMA,
                                                                  write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND)
         )
