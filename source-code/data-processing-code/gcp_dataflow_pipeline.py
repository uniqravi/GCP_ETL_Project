import argparse
import logging
import re

import apache_beam as beam
from apache_beam.io import ReadFromText
from apache_beam.io import WriteToText
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.options.pipeline_options import SetupOptions

SCHEMA = 'product_category_name:String,product_category_name_english:STRING'

def main(argv=None, save_main_session=True):
  """Main entry point; defines and runs the wordcount pipeline."""

  parser = argparse.ArgumentParser()
  parser.add_argument(
      '--input',
      dest='input',
      #default='gs://dataflow-samples/shakespeare/kinglear.txt',
      help='Input file to process.')
  known_args, pipeline_args = parser.parse_known_args(argv)

  # We use the save_main_session option because one or more DoFn's in this
  # workflow rely on global context (e.g., a module imported at module level).
  pipeline_options = PipelineOptions(pipeline_args)
  #pipeline_options.view_as(SetupOptions).save_main_session = save_main_session
  with beam.Pipeline(options=pipeline_options) as p:

    # Read the text file[pattern] into a PCollection.
     (
        p | ReadFromText(known_args.input,skip_header_lines =1)
        | 'Split' >> beam.Map(lambda x :x.split(','))
        | 'FilterBlankRow' >> beam.Filter(lambda x : x[0]!='' & x[1]!='')
        | 'DictMappiing' >> beam.Map(lambda x: {'product_category_name':x[0],'product_category_name_english':x[1]})
        | 'WriteProductCatToBigQuery' >> beam.io.WriteToBigQuery(table='olist.product_category',
                                                       schema=SCHEMA,
                                                       write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND
                                                       )
    )

if __name__ == '__main__':
  logging.getLogger().setLevel(logging.INFO)
  main()

  # Use Python argparse module to parse custom arguments
  import argparse

  import apache_beam as beam
  from apache_beam.options.pipeline_options import PipelineOptions

  # For more details on how to use argparse, take a look at:
  #   https://docs.python.org/3/library/argparse.html
  parser = argparse.ArgumentParser()
  parser.add_argument(
      '--input-file',
      default='gs://dataflow-samples/shakespeare/kinglear.txt',
      help='The file path for the input text to process.')
  parser.add_argument(
      '--output-path', required=True, help='The path prefix for output files.')
  args, beam_args = parser.parse_known_args()

  # Create the Pipeline with remaining arguments.
  beam_options = PipelineOptions(beam_args)
  with beam.Pipeline(options=beam_options) as pipeline:
      lines = (
              pipeline
              | 'Read files' >> beam.io.ReadFromText(args.input_file)
              | 'Write files' >> beam.io.WriteToText(args.output_path))