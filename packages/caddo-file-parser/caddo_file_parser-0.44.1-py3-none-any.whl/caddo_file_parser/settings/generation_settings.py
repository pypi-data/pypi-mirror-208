class GenerationSettings:
    data_settings_file_path = ''
    data_input_path = ''
    data_input_separator = ''
    data_extraction_function_path = ''
    data_splitting_folding_number = 0
    data_splitting_runs = 0
    data_output_file_name = ''
    data_splitting_folding_method = ''
    data_splitting_folding_seeds_from_list = []
    data_splitting_folding_seeds_file_path = ''
    data_output_file_separator = ''

# SAMPLE FILE
# data:
#   input:
#     path: data.csv
#     separator: $
#   extraction:
#     function:
#       path: extraction_function
#   output:
#     file:
#       name: results.csv
#       separator: $
#   splitting:
#     folding:
#       method: KFOLDS
#       number: 10
#       runs: 10
#       seeds:
#         from_list: [1,2,3,4,5, 6, 7, 8, 9, 10] //only one of them should be filled, the second one live empty
#         from_path: seeds.yaml

